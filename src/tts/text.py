import re
from typing import Literal


def preprocess_text(text: str, input_type: Literal["TEXT", "SSML", "RAWMARYXML"]) -> str | None:
    if input_type == "RAWMARYXML":
        return None
    if input_type == "TEXT":
        return text
    if input_type == "SSML":
        stripped = re.sub(r"<[^>]*>", " ", text)
        collapsed = re.sub(r" {2,}", " ", collapsed := stripped)
        return collapsed.strip()
    return text
