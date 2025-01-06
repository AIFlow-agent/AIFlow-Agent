import asyncio
import datetime
import os
import random
import threading
import time
from datetime import timezone
from uuid import uuid4

from langchain.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from plugins.imgflip_meme_generator import ImgflipMemeGenerator
from sia.character import SiaCharacter
from sia.clients.telegram.telegram_client_aiogram import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial
from sia.memory.memory import SiaMemory
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
from sia.schemas.schemas import ResponseFilteringResultLLMSchema
from utils.etc_utils import generate_image_dalle, save_image_from_url
from utils.logging_utils import enable_logging, log_message, setup_logging

from sia.clients.client_interface import SiaClientInterface


class Sia:

    def __init__(
        self,
        character_json_filepath: str,
        memory_db_path: str = None,
        clients=None,
        twitter_creds=None,
        telegram_creds=None,
        plugins=[],
        knowledge_module_classes=[],
        logging_enabled=True,
        testing=False,
    ):
        self.testing = testing
        self.character = SiaCharacter(json_file=character_json_filepath, sia=self)
        self.memory = SiaMemory(character=self.character, db_path=memory_db_path)
        self.clients = clients
        self.twitter = (
            SiaTwitterOfficial(sia=self, **twitter_creds, testing=self.testing)
            if twitter_creds
            else None
        )
        self.telegram = (
            SiaTelegram(
                sia=self,
                **telegram_creds,
                chat_id=self.character.platform_settings.get("telegram", {}).get(
                    "chat_id", None
                ),
            )
            if telegram_creds
            else None
        )
        self.twitter.character = self.character
        self.twitter.memory = self.memory
        self.plugins = plugins

        self.logger = setup_logging()
        enable_logging(logging_enabled)
        self.character.logging_enabled = logging_enabled

        self.knowledge_modules = [kmc(sia=self) for kmc in knowledge_module_classes]
        
        self.run_all_modules()


    def run_all_modules(self):
        import threading

        def run_module(module):
            module.run()

        threads = []
        for module in self.knowledge_modules:
            thread = threading.Thread(target=run_module, args=(module,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def get_modules_settings(self):
        session = self.memory.Session()

        try:
            modules_settings = {}
            for module in self.knowledge_modules:
                module_settings = (
                    session.query(KnowledgeModuleSettingsModel)
                    .filter(
                        KnowledgeModuleSettingsModel.character_name_id
                        == self.character.name_id,
                        KnowledgeModuleSettingsModel.module_name == module.module_name,
                    )
                    .all()
                )
                log_message(
                    self.logger, "info", self, f"Module settings: {module_settings}"
                )
                modules_settings[module.module_name] = module_settings[
                    0
                ].module_settings
            return modules_settings
        finally:
            session.close()

    def get_plugin(self, time_of_day="afternoon"):
        modules_settings = self.get_modules_settings()

        for module in self.knowledge_modules:
            log_message(
                self.logger,
                "info",
                self,
                f"Module: {
                    module.module_name}",
            )
            for plugin_name, plugin in module.plugins.items():
                log_message(self.logger, "info", self, f"Plugin: {plugin_name}")
                log_message(
                    self.logger,
                    "info",
                    self,
                    f"Usage condition: {modules_settings[module.module_name].get('plugins',
                                                                                         {}).get(plugin_name,
                                                                                                 {}).get('usage_condition',
                                                                                                         {}).get('time_of_day')}",
                )
                log_message(self.logger, "info", self, f"Time of day: {time_of_day}")
                if (
                    modules_settings[module.module_name]
                    .get("plugins", {})
                    .get(plugin_name, {})
                    .get("usage_condition", {})
                    .get("time_of_day")
                    == time_of_day
                ):
                    return plugin

        # for module in self.knowledge_modules:
        #     for plugin_name, plugin in module.plugins.items():

        #         if plugin.is_relevant_to_time_of_day(time_of_day) and self.character.moods.get(time_of_day) in plugin.supported_moods:
        #             return plugin
        return None

    def generate_post(
        self, platform="twitter", author=None, character=None, time_of_day=None, conversation_id=None
    ):

        plugin = self.get_plugin(time_of_day=self.character.current_time_of_day())
        plugin_prompt = ""
        if plugin:
            plugin_prompt = plugin.get_instructions_and_knowledge()
            log_message(self.logger, "info", self, f"Plugin prompt: {plugin_prompt}")
        else:
            log_message(self.logger, "info", self, f"No plugin found")

        log_message(self.logger, "info", self, f"Plugin prompt: {plugin_prompt}")

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                {you_are}

                Your post examples are:
                {post_examples}

                Use these examples as an inspiration for the new posts you create.

                Here are your previous posts:
                {previous_posts}

                You are posting to: {platform}

                {plugin_prompt}
            """,
                ),
                (
                    "user",
                    """
                Generate your new post.

                Critically important: your new post must be different from the examples provided and from your previous posts in all ways, shapes or forms.

                Examples:
                - if one of your previous posts starts with "Good morning", your new post must not start with "Good morning"
                - if one of your previous posts starts with an emoji, your new post must not start with an emoji
                - if one of your previous posts has a structure like "Question: <question> Answer: <answer>", your new post must not have that structure

                Your post must be between {length_range} words long.

                You must not use hashtags in your post.
            """,
                ),
            ]
        )

        if not time_of_day:
            time_of_day = self.character.current_time_of_day()

        ai_input = {
            "you_are": self.character.prompts.get("you_are"),
            "post_examples": self.character.get_post_examples(
                "general", time_of_day=time_of_day, random_pick=7
            ),
            "previous_posts": [
                f"[{post.wen_posted}] {post.content}"
                for post in self.memory.get_messages()[-10:]
            ],
            "platform": platform,
            "length_range": random.choice(
                self.character.platform_settings.get(platform, {}).get("post", {}).get("parameters", {}).get("length_ranges", ["1-5", "10-15", "20-30"])
            ),
            "plugin_prompt": plugin_prompt
        }

        try:
            llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.3)

            ai_chain = prompt_template | llm

            generated_post = ai_chain.invoke(ai_input)

            log_message(
                self.logger,
                "info",
                self,
                f"Generated post with Anthropic: {generated_post}",
            )

        except Exception:

            try:
                llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

                ai_chain = prompt_template | llm

                generated_post = ai_chain.invoke(ai_input)

                log_message(
                    self.logger,
                    "info",
                    self,
                    f"Generated post with OpenAI: {generated_post}",
                )

            except Exception as e:

                generated_post = None

                log_message(self.logger, "error", self, f"Error generating post: {e}")

        image_filepaths = []

        # Generate an image for the post
        if random.random() < self.character.plugins_settings.get("dalle", {}).get(
            "probability_of_posting", 0
        ):
            image_url = generate_image_dalle(generated_post.content[0:900])
            if image_url:
                image_filepath = f"media/{uuid4()}.png"
                save_image_from_url(image_url, image_filepath)
                image_filepaths.append(image_filepath)

        # Generate a meme for the post
        imgflip_meme_generator = ImgflipMemeGenerator(
            os.getenv("IMGFLIP_USERNAME"), os.getenv("IMGFLIP_PASSWORD")
        )
        if random.random() < self.character.plugins_settings.get("imgflip", {}).get(
            "probability_of_posting", 0
        ):
            image_url = imgflip_meme_generator.generate_ai_meme(
                prefix_text=generated_post.content
            )
            if image_url:
                os.makedirs("media/imgflip_memes", exist_ok=True)
                image_filepath = f"media/imgflip_memes/{uuid4()}.png"
                save_image_from_url(image_url, image_filepath)
                image_filepaths.append(image_filepath)

        post_content = generated_post.content if generated_post else None
        generated_post_schema = SiaMessageGeneratedSchema(
            content=post_content,
            platform=platform,
            author=author,
            conversation_id=conversation_id
        )

        if plugin:
            log_message(
                self.logger,
                "info",
                self,
                f"Updating settings for {
                    plugin.plugin_name}",
            )
            plugin.update_settings(
                next_use_after=datetime.datetime.now(timezone.utc)
                + datetime.timedelta(hours=1)
            )
        else:
            log_message(self.logger, "info", self, f"No plugin found")

        return generated_post_schema, image_filepaths

    def generate_response(
        self,
        message: SiaMessageSchema,
        platform="twitter",
        time_of_day=None,
        conversation=None,
        previous_messages: str = None,
        use_filtering_rules: str = True,
    ) -> SiaMessageGeneratedSchema | None:
        """
        Generate a response to a message.

        Output:
        - SiaMessageGeneratedSchema
        - None if an error occurred or if filtering rules are not passed
        """

        # do not answer if responding is disabled
        if not self.character.responding.get("enabled", True):
            return None

        if not conversation:
            conversation = self.twitter.get_conversation(
                conversation_id=message.conversation_id
            )
            conversation_first_message = self.memory.get_messages(
                id=message.conversation_id, platform=platform
            )
            conversation = conversation_first_message + conversation[-20:]
            conversation_str = "\n".join(
                [
                    f"[{msg.wen_posted}] {msg.author}: {msg.content}"
                    for msg in conversation
                ]
            )
            log_message(self.logger, "info", self, f"Conversation: {conversation_str.replace('\n', ' ')}")
        else:
            pass

        message_to_respond_str = (
            f"[{message.wen_posted}] {message.author}: {message.content}"
        )
        log_message(
            self.logger, "info", self, f"Message to respond (id {message.id}): {message_to_respond_str.replace('\n', ' ')}"
        )

        # do not answer if the message does not pass the filtering rules but if
        # we need to filter the response
        if self.character.responding.get("filtering_rules") and use_filtering_rules:
            log_message(
                self.logger,
                "info",
                self,
                f"Checking the response against filtering rules: {
                    self.character.responding.get('filtering_rules')}",
            )
            llm_filtering = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            llm_filtering_prompt_template = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """
                    You are a message filtering AI. You are given a message and a list of filtering rules. You need to determine if the message passes the filtering rules. If it does, return 'True'. If it does not, return 'False' Only respond with 1 word: 'True' or 'False'.
                """,
                    ),
                    (
                        "user",
                        """
                    Conversation:
                    {conversation}

                    Message from the conversation to decide whether to respond to:
                    {message}

                    Filtering rules:
                    {filtering_rules}

                    Avoid making assumptions about the message author's intentions. Only apply the filtering rules if the message is in direct conflict with them.

                    Return True unless the message is in direct conflict with the filtering rules.
                """,
                    ),
                ]
            )
            llm_filtering_structured = llm_filtering.with_structured_output(
                ResponseFilteringResultLLMSchema
            )

            filtering_chain = llm_filtering_prompt_template | llm_filtering_structured

            try:
                filtering_result = filtering_chain.invoke(
                    {
                        "conversation": conversation_str,
                        "message": message_to_respond_str,
                        "filtering_rules": self.character.responding.get(
                            "filtering_rules"
                        ),
                    }
                )
                log_message(
                    self.logger,
                    "info",
                    self,
                    f"Response filtering result: {filtering_result}",
                )

            except Exception as e:
                log_message(
                    self.logger, "error", self, f"Error getting filtering result: {e}"
                )
                return None

            if not filtering_result.should_respond:
                return None

        else:
            log_message(self.logger, "info", self, f"No filtering rules found.")

        time_of_day = (
            time_of_day if time_of_day else self.character.current_time_of_day()
        )

        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                        {you_are}

                        {communication_requirements}

                        Your goal is to respond to the message on {platform} provided below in the conversation provided below.

                        Message to response:
                        {message}

                        Conversation:
                        ------------
                        {conversation}
                        ------------

                        Your response must be unique and creative.  It must also be drastically different from your previous messages.

                        It must still be consistent with your personality, mood, core objective and means for achieving it.
                        """.replace("                        ", "")
                    +
                    ("""
                        Some of your previous messages:
                        ------------
                        {previous_messages}
                        ------------
                    """.replace("                        ", "") if previous_messages else "")
                    +
                    ("""
                        Here are your strong opinions:
                        ------------
                        {opinions}
                        ------------
                        You must adhere to these opinions in your response if they are relevant to the message you are responding to.
                    """.replace("                        ", "") if self.character.opinions else "")
                    +
                    """
                        Avoid creating a response that resembles any of your previous ones in how it starts, unfolds and finishes.
                        
                        Important instructions:
                        {instructions}

                        Examples:
                        - if one of your previous messages starts with a question, your new response must not start with a question.
                        - if one of your previous messages continues with an assessment of the situation, your new response must not continue with an assessment of the situation.
                        - if one of your previous messages ends with a question, your new response must not end with a question.
                        - if your previous message is short, your new response must be way longer and vice versa.
                    """.replace("                        ", "")
                ),
                (
                    "user",
                    """
                        Generate your response to the message.

                        Your response length must be fewer than 30 words.

                        Your response must be unique and creative.

                        It must also be drastically different from your previous messages in all ways, shapes or forms.

                        Your response must still be consistent with your personality, mood, core objective and means for achieving it.

                        Your response must be natural continuation of the conversation or the message you are responding to. It must add some value to the conversation.

                        Generate your response to the message following the rules and instructions provided above.
                    """.replace("                        ", ""),
                ),
            ]
        )

        ai_input = {
            "you_are": self.character.prompts.get("you_are"),
            "communication_requirements": self.character.prompts.get(
                "communication_requirements"
            ),
            "instructions": self.character.instructions,
            "opinions": self.character.opinions,
            "platform": platform,
            "message": message_to_respond_str,
            "conversation": conversation_str,
            "previous_messages": previous_messages,
        }

        try:
            llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.0)

            ai_chain = prompt_template | llm

            generated_response = ai_chain.invoke(ai_input)

        except Exception:

            try:
                llm = ChatOpenAI(model="gpt-4o", temperature=0.0)

                ai_chain = prompt_template | llm

                generated_response = ai_chain.invoke(ai_input)

            except Exception as e:
                log_message(
                    self.logger, "error", self, f"Error generating response: {e}"
                )
                return None

        generated_response_schema = SiaMessageGeneratedSchema(
            content=generated_response.content,
            platform=message.platform,
            author=self.character.platform_settings.get(message.platform, {}).get(
                "username", self.character.name
            ),
            response_to=message.id,
            conversation_id=message.conversation_id,
        )
        log_message(
            self.logger,
            "info",
            self,
            f"Generated response: {generated_response_schema}",
        )

        return generated_response_schema


    def run(self):
        """Run all clients concurrently using threads"""
        threads = []
        
        # Add Telegram thread if enabled
        if self.telegram:
            def run_telegram():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.telegram.run())
                except Exception as e:
                    print(f"Telegram error: {e}")
                finally:
                    loop.close()
                    
            telegram_thread = threading.Thread(
                target=run_telegram,
                name="telegram_thread"
            )
            threads.append(telegram_thread)
            
        # Add Twitter thread if enabled    
        if self.twitter:
            def run_twitter():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(self.twitter.run())
                except Exception as e:
                    print(f"Twitter error: {e}")
                finally:
                    loop.close()
                    
            twitter_thread = threading.Thread(
                target=run_twitter,
                name="twitter_thread"
            )
            threads.append(twitter_thread)
            
        # Start all threads
        for thread in threads:
            thread.daemon = True
            thread.start()
            
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
    