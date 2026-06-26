from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    kakao_bot_secret: str = ""
    kakao_channel_token: str = ""
    notification_time: str = "09:00"

    class Config:
        env_file = ".env"


settings = Settings()
