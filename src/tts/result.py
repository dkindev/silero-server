import io
from dataclasses import dataclass


@dataclass
class TTSResult:
    audio: io.BytesIO
    sample_rate: int
    model: str
