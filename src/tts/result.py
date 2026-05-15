from dataclasses import dataclass


@dataclass
class TTSResult:
    audio: bytes
    sample_rate: int
    model: str
