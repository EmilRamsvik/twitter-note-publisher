from pydantic import BaseSettings


class Settings(BaseSettings):

    TWITTER_CONSUMER_KEY: str = ""
    TWITTER_CONSUMER_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_TOKEN_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""
    API_KEY_SECRET: str = ""
    BEARER_TOKEN: str = ""
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    AIRTABLE_BASE_ID: str = "appO7OaB8EmeAn0Zm"
    AIRTABLE_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
