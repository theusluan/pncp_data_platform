from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    # Opção 1 - URL completa
    database_url: Optional[str] = None

    # Opção 2 - Variáveis separadas
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_db: Optional[str] = None
    postgres_host: Optional[str] = "localhost"
    postgres_port: Optional[int] = 5432

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def get_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()