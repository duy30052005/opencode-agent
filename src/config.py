class Settings(BaseSettings):
    GOOGLE_API_KEY: str = Field(default="")
    GOOGLE_API_KEYS: str = Field(default="")
    GITHUB_TOKEN: str = Field(default="")
    GITHUB_OWNER: str = Field(default="")
    GITHUB_REPO: str = Field(default="")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
