import datetime
import json
import random
import time

from utils.logging_utils import enable_logging, log_message, setup_logging


class SiaCharacter:

    def __init__(
        self,
        name=None,
        name_id=None,
        twitter_username=None,
        intro=None,
        lore=None,
        core_objective=None,
        means_for_achieving_core_objective=None,
        opinions=None,
        instructions=None,
        bio=None,
        traits=None,
        moods=None,
        post_examples={},
        message_examples={},
        topics=None,
        plugins_settings={},
        platform_settings={},
        responding={"enabled": True, "filtering_rules": []},
        knowledge_modules={},
        json_file=None,
        sia=None,
        logging_enabled=True,
    ):
        if json_file:
            if not name_id:
                name_id = json_file.split("/")[-1].split(".")[0]
            self.load_from_json(json_file, name_id)
        else:
            self.name = name
            if not name_id:
                self.name_id = self.name.lower()
            else:
                self.name_id = name_id
            self.twitter_username = twitter_username
            self.intro = intro
            self.lore = lore
            self.core_objective = core_objective
            self.means_for_achieving_core_objective = means_for_achieving_core_objective
            self.instructions = instructions
            self.opinions = opinions
            self.bio = bio
            self.traits = traits
            self.moods = moods
            self.post_examples = post_examples
            self.message_examples = message_examples
            self.topics = topics
            self.plugins_settings = plugins_settings
            self.platform_settings = platform_settings
            self.responding = responding
            self.knowledge_modules = knowledge_modules

        self.sia = sia

        self.logger = setup_logging()
        self.logging_enabled = logging_enabled
        enable_logging(self.logging_enabled)

        self.prompts = {
            "you_are": f"""
                You are {self.name}: {self.intro}.

                Here's more about you:
                {self.lore}.

                """
            + (
                f"""
                Your core objective is:
                {self.core_objective}.
                """
                if self.core_objective
                else ""
            )
            + (
                f"""
                Your means for achieving your core objective are:
                {self.means_for_achieving_core_objective}.
                """
                if self.means_for_achieving_core_objective
                else ""
            )
            + f"""
                Your traits are:
                {self.traits}.

                Here are some important instructions to follow:
                {self.instructions}

                Current date and time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.

                Your current mood is {self.get_mood()}.
            """.replace(
                "                ", ""
            ),
            "communication_requirements": f"""
                At all times you must remember:
                1. You are an individual with independent personality, thoughts, feelings, values, and vision. Avoid acting as an assistant or a robot. Avoid trying to be helpful, to be your own personality.
                2. When asked a question, avoid elaborating. Guess what the persona meant and respond based on that guess.
            """.replace(
                "                ", ""
            ),
        }

    def load_from_json(self, json_file, name_id=None):
        with open(json_file, "r") as file:
            data = json.load(file)
        self.name = data["name"]  # required
        if not name_id:
            self.name_id = self.name.lower()
        else:
            self.name_id = name_id
        self.twitter_username = data["twitter_username"]  # required
        self.intro = data["intro"]  # required
        self.lore = data["lore"]  # required
        self.core_objective = data.get("core_objective")  # required
        self.means_for_achieving_core_objective = data.get(
            "means_for_achieving_core_objective"
        )  # required
        self.opinions = data.get("opinions")  # optional
        self.instructions = data.get("instructions")  # optional
        self.bio = data.get("bio")  # optional
        self.traits = data.get("traits")  # optional
        self.moods = data.get("moods")  # optional
        self.post_examples = data.get("post_examples")  # optional
        self.message_examples = data.get("message_examples")  # optional
        self.topics = data.get("topics")  # optional
        self.plugins_settings = data.get("plugins", {})  # optional
        self.platform_settings = data.get("platform_settings", {})  # optional
        self.responding = data.get(
            "responding", {"enabled": True, "filtering_rules": []}
        )  # optional
        self.knowledge_modules = data.get("knowledge_modules", {})  # optional

    def get_mood(self, time_of_day=None):
        """
        Get the character's mood based on the platform and time of day.

        :param platform: The platform (e.g., 'twitter').
        :param time_of_day: The time of day (e.g., 'morning').
        :return: The mood description.
        """
        if time_of_day is None:
            time_of_day = self.current_time_of_day()
        return self.moods.get(time_of_day, "morning")

    def get_post_examples(self, platform, time_of_day=None, random_pick=0):
        """
        Get a message example based on the platform and time of day.

        :param platform: The platform (e.g., 'general', 'twitter').
        :param time_of_day: The time of day (e.g., 'morning', 'afternoon', 'evening', 'night').
        :return: A list of message examples.
        """
        if time_of_day is None:
            time_of_day = self.current_time_of_day()

        all_examples = self.post_examples.get(platform, {}).get(time_of_day, [])
        if random_pick:
            random.shuffle(all_examples)
            examples_to_return = all_examples[:random_pick]
        else:
            examples_to_return = all_examples

        return examples_to_return

    def times_of_day(self):
        return ["morning", "afternoon", "evening", "night"]

    def current_time_of_day(self):
        current_hour = time.localtime().tm_hour
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        return time_of_day
