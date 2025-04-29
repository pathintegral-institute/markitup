from ast import Tuple
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Literal, Dict, Any, Tuple, override


CHUNK_SIZE = 300
TIKTOKEN_ENCODER = 'gpt-4'

@dataclass
class StreamInfo:
    magic_type: Optional[str] = None
    category: Optional[str] = None


@dataclass
class Config:
    modalities: List[Literal["image", "audio"]] = field(
        default_factory=lambda: ["image", "audio"]
    )
    chunk: bool = False
    chunk_size: int = CHUNK_SIZE
    # CHUNK_OVERLAP = 0 # Warning, the current pdf chunking localization depends on chunk_overlap == 0
    tiktoken_encoder: str = TIKTOKEN_ENCODER
    image_use_webp: bool = True  # TODO: support files contains images
    image_max_width_or_height: int = 768


@dataclass
class MarkdownChunk:
    chunk_modality: Literal["text", "image"]
    content: str  # The content of the chunk ONLY contains one type of modality

    # LOCATION INFO
    chunk_id: int  # The global chunk id of the chunk

    page_id: Optional[int] = None  # The 0-based page id of the chunk, currently exclusive for pdf

    bbox_id_list: Optional[List[int]] = field(
        default_factory=list
    )  # The 0-based bounding box id of the chunk, currently exclusive for pdf

    bbox_list: Optional[List[Tuple[float, float, float, float]]] = field(
        default_factory=list
    )  # The bounding box of the chunk, currently exclusive for pdf

@dataclass
class Chunk:
    chunk_modality: Literal["text", "image", "audio"]
    content: Dict[str, Any]  # The content of the chunk ONLY contains one type of modality

    # LOCATION INFO
    chunk_id: int  # The global chunk id of the chunk @rong: do we need a local chunk id here?

    page_id: Optional[int]  # The 0-based page id of the chunk, currently exclusive for pdf
    
    bbox_list: Optional[List[Tuple[float, float, float, float]]]  # The bounding box of the chunk, currently exclusive for pdf
