from pydantic import BaseSettings


class Settings(BaseSettings):
    SPOT_IP: str
    BOSDYN_CLIENT_USERNAME: str
    BOSDYN_CLIENT_PASSWORD: str
