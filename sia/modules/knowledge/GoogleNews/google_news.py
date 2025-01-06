import importlib
import json
import os
from datetime import datetime, timedelta, timezone

import requests
from dateutil import parser
from sqlalchemy import inspect

from sia.modules.knowledge.GoogleNews.models_db import (
    GoogleNewsSearchModel,
    GoogleNewsSearchResultModel,
)
from sia.modules.knowledge.GoogleNews.schemas import (
    GoogleNewsSearchParametersSchema,
    GoogleNewsSearchResultsSchema,
)
from sia.modules.knowledge.models_db import KnowledgeModuleSettingsModel
from sia.modules.knowledge.schemas import KnowledgeModuleSettingsSchema
from sia.sia import Sia
from utils.logging_utils import enable_logging, log_message, setup_logging


class GoogleNewsModule:
    module_name = "GoogleNewsModule"

    def __init__(self, sia: Sia = None, api_key: str = None, logging_enabled=True):
        self.sia = sia
        self.api_key = api_key or os.getenv("SEARCHAPI_API_KEY")

        # setup logging
        self.logger = setup_logging()
        enable_logging(logging_enabled)

        # setup plugins
        self.plugins = {}
        plugins_folder = os.path.join(os.path.dirname(__file__), "plugins")
        log_message(self.logger, "info", self, f"Plugins folder: {plugins_folder}")
        for filename in os.listdir(plugins_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = f".plugins.{filename[:-3]}"
                module = importlib.import_module(module_name, package=__package__)
                log_message(self.logger, "info", self, f"Module: {module}")
                for attr in dir(module):
                    attr_value = getattr(module, attr)
                    log_message(self.logger, "info", self, f"Attr value: {attr_value}")
                    if isinstance(attr_value, type) and attr.endswith("Plugin"):
                        self.plugins[attr_value.plugin_name] = attr_value(module=self)

        log_message(self.logger, "info", self, f"Plugins: {self.plugins}")

        # ensure tables exist
        self.ensure_tables_exist()

    def ensure_tables_exist(self):
        engine = self.sia.memory.engine
        inspector = inspect(engine)
        if not inspector.has_table(KnowledgeModuleSettingsModel.__tablename__):
            KnowledgeModuleSettingsModel.__table__.create(engine)
        if not inspector.has_table(GoogleNewsSearchModel.__tablename__):
            GoogleNewsSearchModel.__table__.create(engine)
        if not inspector.has_table(GoogleNewsSearchResultModel.__tablename__):
            GoogleNewsSearchResultModel.__table__.create(engine)

    def _datetime_converter(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        raise TypeError(f"Type {o.__class__.__name__} not serializable")

    def get_settings(self):
        session = self.sia.memory.Session()
        try:
            settings_model = (
                session.query(KnowledgeModuleSettingsModel)
                .filter(KnowledgeModuleSettingsModel.module_name == self.module_name)
                .first()
            )
        finally:
            session.close()
        if settings_model:
            settings_schema = KnowledgeModuleSettingsSchema(
                character_name_id=settings_model.character_name_id,
                module_name=settings_model.module_name,
                module_settings=settings_model.module_settings,
            )
            log_message(
                self.logger,
                "info",
                self,
                f"Loaded settings for {
                    self.module_name} module: {
                    json.dumps(
                        settings_schema.dict(),
                        indent=4,
                        default=self._datetime_converter)}",
            )
            return settings_schema
        else:
            module_settings = self.sia.character.knowledge_modules.get(
                self.module_name, {}
            )
            settings_schema = KnowledgeModuleSettingsSchema(
                module_name=self.module_name,
                character_name_id=self.sia.character.name_id,
                module_settings={
                    **module_settings,
                    "next_run_at": datetime.now(timezone.utc) - timedelta(seconds=1),
                },
            )
            log_message(
                self.logger,
                "info",
                self,
                f"Created new settings for {
                    self.module_name} module: {
                    json.dumps(
                        settings_schema.dict(),
                        indent=4,
                        default=self._datetime_converter)}",
            )
            return settings_schema

    def update_settings(self, settings: KnowledgeModuleSettingsSchema):
        session = self.sia.memory.Session()
        try:
            settings_model = (
                session.query(KnowledgeModuleSettingsModel)
                .filter(KnowledgeModuleSettingsModel.module_name == self.module_name)
                .first()
            )
            if settings_model:
                # Convert datetime objects to strings in module_settings
                settings_dict = settings.dict()
                settings_dict["module_settings"] = {
                    key: (value.isoformat() if isinstance(value, datetime) else value)
                    for key, value in settings_dict["module_settings"].items()
                }
                for key, value in settings_dict.items():
                    setattr(settings_model, key, value)
            else:
                settings_dict = settings.dict()
                settings_dict["module_settings"] = {
                    key: (value.isoformat() if isinstance(value, datetime) else value)
                    for key, value in settings_dict["module_settings"].items()
                }
                settings_model = KnowledgeModuleSettingsModel(**settings_dict)
                session.add(settings_model)
            session.commit()
        finally:
            session.close()

    def search(
        self, parameters: GoogleNewsSearchParametersSchema
    ) -> GoogleNewsSearchResultsSchema:
        url = "https://www.searchapi.io/api/v1/search"

        try:
            response = requests.get(
                url, params={**parameters.dict(), "api_key": self.api_key}
            )

            try:
                return GoogleNewsSearchResultsSchema(**response.json())
            except Exception as e:
                log_message(
                    self.logger, "error", self, f"Error searching Google News: {e}"
                )
                return None

        except Exception as e:
            log_message(self.logger, "error", self, f"Error searching Google News: {e}")
            return None

    def save_search_results_to_db(self, search_results: GoogleNewsSearchResultsSchema):
        # Create a new GoogleNewsSearchModel instance
        search_model = GoogleNewsSearchModel(
            metadata_id=search_results.search_metadata.id,
            status=search_results.search_metadata.status,
            created_at=search_results.search_metadata.created_at,
            request_time_taken=search_results.search_metadata.request_time_taken,
            parsing_time_taken=search_results.search_metadata.parsing_time_taken,
            total_time_taken=search_results.search_metadata.total_time_taken,
            request_url=str(search_results.search_metadata.request_url),
            html_url=str(search_results.search_metadata.html_url),
            json_url=str(search_results.search_metadata.json_url),
            engine=search_results.search_parameters.engine,
            q=search_results.search_parameters.q,
            device=search_results.search_parameters.device,
            google_domain=search_results.search_parameters.google_domain,
            hl=search_results.search_parameters.hl,
            gl=search_results.search_parameters.gl,
            num=search_results.search_parameters.num,
            time_period=search_results.search_parameters.time_period,
            query_displayed=search_results.search_information.query_displayed,
            total_results=search_results.search_information.total_results,
            time_taken_displayed=search_results.search_information.time_taken_displayed,
            detected_location=search_results.search_information.detected_location,
        )

        # Add the search model to the session
        session = self.sia.memory.Session()
        session.add(search_model)
        session.flush()  # Flush to get the search_model.id for foreign key

        # Create GoogleNewsSearchResultModel instances for each search result
        for result in search_results.organic_results:
            result_model = GoogleNewsSearchResultModel(
                position=result.position,
                title=result.title,
                link=str(result.link),
                source=result.source,
                date=result.date,
                snippet=result.snippet,
                favicon=result.favicon,
                thumbnail=result.thumbnail,
                search_id=search_model.id,  # Use the ID from the flushed search_model
            )
            session.add(result_model)

        # Commit the transaction
        session.commit()

    def run(self):

        log_message(
            self.logger,
            "info",
            self,
            f"Running {
                self.module_name} module",
        )

        settings = self.get_settings()

        next_run_at_str = settings.module_settings.get("next_run_at")
        next_run_at = (
            parser.isoparse(next_run_at_str)
            if isinstance(next_run_at_str, str)
            else next_run_at_str
        )

        # Check if next_run_at is in the future
        if next_run_at > datetime.now(timezone.utc):
            log_message(
                self.logger,
                "info",
                self,
                f"Skipping {
                    self.module_name} module because next_run_at is in the future (time now: {
                    datetime.now(
                        timezone.utc)}, next_run_at: {
                    settings.module_settings.get('next_run_at')})",
            )
            return

        searches_parameters = settings.module_settings.get("search_parameters", [])
        log_message(
            self.logger,
            "info",
            self,
            f"Running {
                self.module_name} module with {
                len(searches_parameters)} search parameters:\n{
                json.dumps(
                    searches_parameters, indent=4)}",
        )

        for i, search_parameters in enumerate(searches_parameters):
            search_results = self.search(
                GoogleNewsSearchParametersSchema(**search_parameters)
            )
            # log_message(self.logger, "info", self, f"Search results {i+1}: {json.dumps(search_results.dict(), indent=4)}")
            if search_results:
                self.save_search_results_to_db(search_results)

        settings.module_settings["next_run_at"] = datetime.now(
            timezone.utc
        ) + timedelta(days=1 / settings.module_settings.get("search_frequency", 1))

        log_message(
            self.logger,
            "info",
            self,
            f"Updated settings after running {
                self.module_name} module",
        )

        self.update_settings(settings)
