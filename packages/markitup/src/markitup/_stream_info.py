from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class StreamInfo:
    magic_type: Optional[str] = None
    category: Optional[str] = None