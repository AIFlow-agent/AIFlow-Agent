from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class GoogleNewsSearchMetadataSchema(BaseModel):
    id: str
    status: str
    created_at: str
    request_time_taken: float
    parsing_time_taken: float
    total_time_taken: float
    request_url: HttpUrl
    html_url: HttpUrl
    json_url: HttpUrl

    class Config:
        from_attributes = True


class GoogleNewsSearchParametersSchema(BaseModel):
    engine: str = "google_news"
    q: str
    device: str = "desktop"
    google_domain: str = "google.com"
    hl: str = "en"
    gl: str = "us"
    num: int = 30
    time_period: str = "last_day"

    class Config:
        from_attributes = True


class GoogleNewsSearchInformationSchema(BaseModel):
    query_displayed: Optional[str] = "Unknown"
    total_results: Optional[int] = 0
    time_taken_displayed: Optional[float] = 0.0
    detected_location: Optional[str] = "Unknown"

    class Config:
        from_attributes = True


class GoogleNewsSearchResultSchema(BaseModel):
    position: int
    title: str
    link: HttpUrl
    source: str
    date: str
    snippet: str
    favicon: Optional[str]
    thumbnail: Optional[str]

    class Config:
        from_attributes = True


class GoogleNewsSearchResultsSchema(BaseModel):
    search_metadata: GoogleNewsSearchMetadataSchema = None
    search_parameters: GoogleNewsSearchParametersSchema
    search_information: GoogleNewsSearchInformationSchema = None
    organic_results: List[GoogleNewsSearchResultSchema] = []

    class Config:
        from_attributes = True
