from typing import List

from pydantic import BaseModel


class GooglePlayCountryWithLanguages(BaseModel):
    country_code: str
    language_codes: List[str]
