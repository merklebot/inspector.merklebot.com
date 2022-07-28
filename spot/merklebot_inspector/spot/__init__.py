from typing import TypedDict, Optional, Dict


class SpotState(TypedDict):
    battery: Optional[float]
    camera_images: Dict[str, str]
