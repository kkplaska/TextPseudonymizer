from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional
import os

MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000000"))
MAX_WORDS_COUNT = int(os.getenv("MAX_WORDS_COUNT", "5000"))

class AnonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH, description="The text to anonymize")
    words: List[str] = Field(..., min_length=1, max_length=MAX_WORDS_COUNT, description="List of phrases to replace")
    existing_mapping: Optional[Dict[str, str]] = Field(default=None, description="Previously generated mapping to reuse")
    match_whole_words: bool = Field(default=True, description="Whether to match whole words only")

    @field_validator('words')
    @classmethod
    def validate_words(cls, v: List[str]) -> List[str]:
        # Filter out empty strings and strip whitespace
        cleaned = [w.strip() for w in v if w.strip()]
        if not cleaned:
            raise ValueError("The 'words' list must contain at least one non-empty string.")
        # Return unique elements while preserving order (optional, but good practice)
        # Using a list comprehension over a dict to keep order in >= py3.7
        return list(dict.fromkeys(cleaned))

class AnonymizeResponse(BaseModel):
    result_text: str
    mapping: Dict[str, str]

class DeanonymizeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=MAX_TEXT_LENGTH, description="The text to deanonymize")
    mapping: Dict[str, str] = Field(..., max_length=MAX_WORDS_COUNT, description="Mapping of original words to their tokens")

    @field_validator('mapping')
    @classmethod
    def validate_mapping(cls, v: Dict[str, str]) -> Dict[str, str]:
        if not v:
            raise ValueError("The mapping dictionary cannot be empty.")
        return v

class DeanonymizeResponse(BaseModel):
    result_text: str
