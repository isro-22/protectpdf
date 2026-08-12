from dataclasses import dataclass
from enum import Enum

class PrintMode(str, Enum):
    BLOCK = "block"
    BLANK_EXPERIMENTAL = "blank_experimental"
    ALLOW = "allow"

@dataclass(frozen=True)
class WatermarkConfig:
    enabled: bool = False
    text: str = "CONFIDENTIAL"
    opacity: float = 0.20
    font_size: float = 48
    rotation: float = 45
    add_document_id: bool = False
    add_timestamp: bool = False
    username: str = ""

@dataclass(frozen=True)
class ProtectionConfig:
    user_password: str = ""
    owner_password: str = ""
    disable_copy: bool = True
    disable_edit: bool = True
    disable_annotation: bool = True
    print_mode: PrintMode = PrintMode.BLOCK
