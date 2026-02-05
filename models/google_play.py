from typing import List, Optional

from pydantic import BaseModel
from google_play_scraper.models import Review


class GooglePlayCountryWithLanguages(BaseModel):
    country_code: str
    language_codes: List[str]


class ReviewsResponse(BaseModel):
    """Response from reviews endpoint including pagination token"""
    reviews: List[Review]
    continuation_token: Optional[str] = None
