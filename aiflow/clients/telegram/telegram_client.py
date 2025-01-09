import asyncio

from telegram import Bot, Update
from telegram.error import Conflict, NetworkError, TelegramError
from telegram.ext import (
    ApplicationBuilder,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    filters,
)

from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
from utils.logging_utils import enable_logging, log_message, setup_logging

from sia.clients.client_interface import SiaClientInterface


class SiaTelegram(SiaClientInterface):
    platform_name = "telegram"

    def __init__(self, sia, bot_token, chat_id=None, logging_enabled=True):
        super().__init__(sia=sia, logging_enabled=logging_enabled)
        self.bot_token = bot_token
        self.bot = Bot(token=self.bot_token)
        self.application = ApplicationBuilder().token(bot_token).build()
        self.chat_id = (
            chat_id  # Set this to the chat ID where you want to post messages
        )
        self.sia = sia
        self.logging_enabled = logging_enabled

        self.logger = setup_logging()
        enable_logging(self.logging_enabled)

    async def start(self, update: Update, context: CallbackContext):
        self.chat_id = update.message.chat_id  # Store chat ID for posting messages
        await update.message.reply_text("Hello! I am your bot.")

    async def handle_message(self, update: Update, context: CallbackContext):
        try:
            message_text = update.message.text
            user = update.message.from_user
            user_id = user.id
            username = user.username or user.first_name
            chat = update.message.chat
            chat_id = chat.id
            chat_title = chat.title or "Private Chat"
            chat_username = chat.username or "No username"
        except Exception as e:
            log_message(
                self.logger,
                "error",
                self,
                f"Error in handle_message: {e}\nUpdate: {update}",
            )
            return

        message = SiaMessageGeneratedSchema(
            platform=self.platform_name,
            # character=self.sia.character.name,
            author=username,
            content=message_text,
            conversation_id=str(chat_id),
        )

        self.sia.memory.add_message(
            message_id=f"{chat_id}-{update.message.message_id}",
            message=message,
            character=self.sia.character.name
        )

        print(
            f"Received message from {username} (ID: {user_id}) in chat '{chat_title}' (ID: {chat_id}, t.me/{chat_username}), message ID {
                update.message.message_id}: {message_text}"
        )

        # Check if the message is a reply to another message
        if update.message.reply_to_message:
            original_message = update.message.reply_to_message
            original_user = original_message.from_user

            # Extract user ID and username of the original message sender
            original_user.id
            original_username = original_user.username or original_user.first_name

            if original_username == self.sia.character.platform_settings.get(
                "telegram", {}
            ).get("username", "<no bot username>"):

                generated_response = self.sia.generate_response(
                    message=SiaMessageSchema(
                        id=f"{self.chat_id}-{update.message.message_id}",
                        **message.dict(),
                    )
                )

                if generated_response:

                    tg_reply_response = await update.message.reply_text(
                        generated_response.content
                    )

                    self.sia.memory.add_message(
                        message_id=f"{self.chat_id}-{tg_reply_response.message_id}",
                        message=generated_response,
                    )

        # Respond to mentions
        if f"@{context.bot.username}" in message_text:

            generated_response = self.sia.generate_response(
                message=SiaMessageSchema(
                    id=f"{self.chat_id}-{update.message.message_id}", **message.dict()
                )
            )

            if generated_response:

                tg_reply_response = await update.message.reply_text(
                    generated_response.content
                )

                self.sia.memory.add_message(
                    message_id=f"{self.chat_id}-{tg_reply_response.message_id}",
                    message=generated_response,
                )
        else:
            print(
                f"[@{context.bot.username}] No reply to message from {username} (ID: {user_id}) in chat '{chat_title}' (ID: {chat_id}, t.me/{chat_username}), message ID {update.message.message_id}: {message_text}"
            )

    # def is_time_to_post(self):
    #     platform_settings = self.sia.character.platform_settings["telegram"]

    #     log_message(
    #         self.logger,
    #         "info",
    #         self,
    #         f"Character settings: {
    #             platform_settings['post_frequency']}",
    #     )

    #     return True

    async def periodic_post(self):
        # self.is_time_to_post()
        while True:

            if self.chat_id:

                bot_username = self.sia.character.platform_settings.get(
                    "telegram", {}
                ).get("username", "<no bot username>")

                post, media = self.sia.generate_post(
                    platform=self.platform_name,
                    author=bot_username
                )

                try:
                    message_send_response = await self.bot.send_message(
                        chat_id=self.chat_id, text=post.content
                    )
                    print(
                        f"New message id: {
                            message_send_response.message_id}"
                    )

                    self.sia.memory.add_message(
                        message_id=f"{self.chat_id}-{message_send_response.message_id}",
                        message=SiaMessageGeneratedSchema(
                            platform=self.platform_name,
                            # character=self.sia.character.name,
                            author=bot_username,
                            content=post.content,
                            conversation_id=str(self.chat_id),
                        ),
                    )

                    if media:
                        print(f"Sending media: {media}")
                        for media_file in media:
                            with open(media_file, "rb") as photo_file:
                                await self.bot.send_photo(
                                    chat_id=self.chat_id, photo=photo_file
                                )
                    print("Post sent successfully!")
                except TelegramError as e:
                    print(f"Failed to send post: {e}")
            post_frequency_hours = self.sia.character.platform_settings.get(
                "telegram", {}
            ).get("post", {}).get("frequency", 2)
            # Wait for the specified number of hours
            await asyncio.sleep(post_frequency_hours * 3600)

    async def run(self):

        conflict_wait_time = 10

        if self.sia.character.platform_settings.get("telegram", {}).get(
            "enabled", False
        ):

            while True:
                try:
                    # Add handlers to the application
                    self.application.add_handler(CommandHandler("start", self.start))
                    self.application.add_handler(
                        MessageHandler(
                            filters.TEXT & ~filters.COMMAND, self.handle_message
                        )
                    )

                    # Initialize the application
                    await self.application.initialize()

                    # Start the periodic posting task
                    asyncio.create_task(self.periodic_post())

                    # Start the bot using start() and updater.start_polling()
                    await self.application.start()
                    await self.application.updater.start_polling()

                    # Keep the application running
                    while True:
                        # Sleep for an hour, adjust as needed
                        await asyncio.sleep(3600)

                except Conflict:
                    log_message(
                        self.logger,
                        "error",
                        self,
                        "Conflict error: Another instance of the bot is running.",
                    )
                    # Wait before retrying
                    await asyncio.sleep(conflict_wait_time)
                    conflict_wait_time += 5
                    log_message(
                        self.logger, "info", self, "Retrying to start the bot..."
                    )

                except NetworkError as e:
                    log_message(
                        self.logger, "error", self, f"Network error occurred: {e}"
                    )
                    # Handle network errors, possibly with a retry mechanism
                    await asyncio.sleep(5)

                except Exception as e:
                    log_message(
                        self.logger, "error", self, f"An unexpected error occurred: {e}"
                    )
                    break  # Exit the loop if an unexpected error occurs

                # Sleep for a while before retrying
                await asyncio.sleep(1)

        else:
            log_message(
                self.logger,
                "info",
                self,
                f"Telegram client is disabled for character {
                    self.sia.character.name}",
            )
            while True:
                await asyncio.sleep(1)
