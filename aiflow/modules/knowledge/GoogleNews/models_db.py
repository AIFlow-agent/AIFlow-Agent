from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class GoogleNewsSearchModel(Base):
    __tablename__ = "knowledge_google_news_search"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metadata_id = Column(String, unique=True, nullable=False)
    status = Column(String)
    created_at = Column(String)
    request_time_taken = Column(Float)
    parsing_time_taken = Column(Float)
    total_time_taken = Column(Float)
    request_url = Column(String)
    html_url = Column(String)
    json_url = Column(String)
    engine = Column(String)
    q = Column(String)
    device = Column(String)
    google_domain = Column(String)
    hl = Column(String)
    gl = Column(String)
    num = Column(String)
    time_period = Column(String)
    query_displayed = Column(String)
    total_results = Column(Integer)
    time_taken_displayed = Column(Float)
    detected_location = Column(String)

    # Relationship to organic results
    results = relationship("GoogleNewsSearchResultModel", back_populates="search")


class GoogleNewsSearchResultModel(Base):
    __tablename__ = "knowledge_google_news_search_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    position = Column(Integer)
    title = Column(String)
    link = Column(String)
    source = Column(String)
    date = Column(String)
    snippet = Column(String)
    favicon = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    search_id = Column(Integer, ForeignKey("knowledge_google_news_search.id"))

    # Relationship back to search schema
    search = relationship("GoogleNewsSearchModel", back_populates="results")
