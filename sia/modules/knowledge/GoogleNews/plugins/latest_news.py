import json
import random
from datetime import datetime, timedelta, timezone

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from sqlalchemy.orm.attributes import flag_modified

from sia.modules.knowledge.GoogleNews.models_db import (
    GoogleNewsSearchModel,
    GoogleNewsSearchResultModel,
)
from sia.modules.knowledge.GoogleNews.schemas import GoogleNewsSearchResultSchema
from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
from utils.logging_utils import enable_logging, setup_logging


class LatestNewsPlugin:
    plugin_name = "LatestNews"

    def __init__(self, module, logging_enabled=True):
        self.module = module

        self.logger = setup_logging()
        enable_logging(logging_enabled)

    def get_latest_news_from_db(self):
        # Use a context manager to ensure the session is closed properly
        with self.module.sia.memory.Session() as session:
            # Use timezone-aware datetime if your database uses TIMESTAMP WITH
            # TIME ZONE
            twenty_four_hours_ago = datetime.now(timezone.utc) - timedelta(hours=24)

            # Query the database for searches created in the last 24 hours
            latest_searches = (
                session.query(GoogleNewsSearchModel.id)
                .filter(GoogleNewsSearchModel.created_at >= twenty_four_hours_ago)
                .all()
            )

            # Extract search IDs
            search_ids = [search.id for search in latest_searches]

            # Query the search results using the search IDs
            if search_ids:
                latest_results = (
                    session.query(GoogleNewsSearchResultModel)
                    .filter(GoogleNewsSearchResultModel.search_id.in_(search_ids))
                    .all()
                )

                # Convert the results to the appropriate Pydantic schema
                return [
                    GoogleNewsSearchResultSchema.from_orm(result)
                    for result in latest_results
                ]

            return []  # Return an empty list if no results are found

    def pick_one_news(self, latest_news):
        character_details = self.module.sia.character.prompts["you_are"]

        latest_news_str = "\n".join(
            [
                f"{i + 1}. {news.title}. {news.snippet} [{news.link}]"
                for i, news in enumerate(latest_news)
            ]
        )

        prompt = ChatPromptTemplate.from_template(
            """
            {character_details}

            Latest News:
            {latest_news}

            Based on the character details, pick the most interesting news for the character.

            You must pick only 1 news story.

            Output in the following format:
            Title: <title>
            Snippet: <snippet>
            Link: <link>
        """.replace(
                "\n", "            "
            )
        )

        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
        ai_chain = prompt | llm
        return ai_chain.invoke(
            {"character_details": character_details, "latest_news": latest_news_str}
        ).content

    def get_instructions_and_knowledge(self):
        latest_news = self.get_latest_news_from_db()
        random.shuffle(latest_news)
        news_picked = self.pick_one_news(latest_news[:20])

        prompt_part = f"""
            You chose the following news story:
            {news_picked}

            Write your next post about it and the link to the news story.
        """.replace(
            "            ", ""
        )

        return prompt_part

    def update_settings(self, next_use_after: datetime):
        session = self.module.sia.memory.Session()
        try:
            settings_model = (
                session.query(KnowledgeModuleSettingsModel)
                .filter(
                    KnowledgeModuleSettingsModel.module_name == self.module.module_name
                )
                .first()
            )

            if settings_model:
                # Deserialize module_settings to update next_use_after
                module_settings = settings_model.module_settings

                # Update the next_use_after field
                if (
                    "plugins" in module_settings
                    and self.plugin_name in module_settings["plugins"]
                ):
                    module_settings["plugins"][self.plugin_name][
                        "next_use_after"
                    ] = next_use_after.isoformat()

                print(
                    f"\n\nmodule_settings: {
                        json.dumps(
                            module_settings,
                            indent=4)}\n\n"
                )

                # Serialize the updated module_settings back to JSON
                settings_model.module_settings = module_settings

                # # Merge the updated model to ensure it's attached to the session
                # session.merge(settings_model)

                flag_modified(settings_model, "module_settings")

                # Flush the session to ensure changes are detected
                session.flush()
                # Commit the session to persist changes
                session.commit()

        finally:
            session.close()
