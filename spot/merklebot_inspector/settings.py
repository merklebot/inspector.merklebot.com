from typing import List

from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):
    # Spot
    SPOT_IP: str
    BOSDYN_CLIENT_USERNAME: str
    BOSDYN_CLIENT_PASSWORD: str

    # Web server
    WEB_HOST: str
    WEB_PORT: int
    WEB_CORS_ORIGINS: List[AnyHttpUrl]
