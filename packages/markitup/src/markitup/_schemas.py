from dataclasses import dataclass, asdict, field
from typing import Optional, List, Literal


@dataclass
class StreamInfo:
    magic_type: Optional[str] = None
    category: Optional[str] = None


@dataclass
class Config:
    modalities: List[Literal["image", "audio"]] = field(
        default_factory=lambda: ["image", "audio"]
    )
    image_use_webp: bool = True  # TODO: support files contains images
