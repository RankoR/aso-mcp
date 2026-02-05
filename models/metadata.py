from typing import List

from pydantic import BaseModel


class MetadataValidationError(BaseModel):
    message: str


class MetadataValidationResult(BaseModel):
    length: int
    is_valid: bool
    errors: List[MetadataValidationError] = []
