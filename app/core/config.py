from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    kakao_bot_secret: str = ""
    kakao_channel_token: str = ""
    kakao_push_api_url: str = ""
    admin_user_id: str = ""
    notification_time: str = "09:00"
    weekly_report_day: str = "mon"

    class Config:
        env_file = ".env"


settings = Settings()
