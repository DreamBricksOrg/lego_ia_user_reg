from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = Field("LogCenter API", env="APP_NAME")
    ENV: str = Field("dev", env="ENV")
    HOST: str = Field("0.0.0.0", env="HOST")
    PORT: int = Field(5005, env="PORT")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    SHORTENER_BASE_URL: str = Field("https://go.dbpe.com.br", env="SHORTENER_BASE_URL")
    SHORTENER_USER: str = Field(...,env="SHORTENER_USER")
    SHORTENER_PASSWORD: str = Field(...,env="SHORTENER_PASSWORD")
    LOGCENTER_SDK_ENABLED: bool = Field(False, env="LOGCENTER_SDK_ENABLED")
    LOGCENTER_BASE_URL: str = Field(..., env="LOGCENTER_BASE_URL")
    LOGCENTER_API_KEY: str = Field(..., env="LOGCENTER_API_KEY")
    LOGCENTER_PROJECT_ID: str = Field(..., env="LOGCENTER_PROJECT_ID")
    LOGCENTER_MIN_LEVEL: str = Field("INFO", env="LOGCENTER_MIN_LEVEL")
    CADASTRO_BASE_URL: str = Field(..., env="CADASTRO_BASE_URL")
    UDP_PORT: int = Field(5004, env="UDP_PORT")
    SERIAL_PORT: str = Field("COM3", env="SERIAL_PORT")
    SERIAL_BAUDRATE: int = Field(9600, env="SERIAL_BAUDRATE")
    MALL_ID: int = Field(84, env="MALL_ID")


    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()