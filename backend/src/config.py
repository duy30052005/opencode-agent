from __future__ import annotations

import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

def _load_dotenv(path: str = ".env") -> None:
    """Hàm tự chế để đọc file .env thủ công (dành cho các hệ điều hành kén dotenv)"""
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

# Ép hệ thống nạp file .env ngay khi file config này được gọi
_load_dotenv()

class Settings(BaseSettings):
    """
    Class cấu hình chung, đã được gộp từ cả nhánh main và nhánh của Duy.
    Dùng BaseSettings của Pydantic để tự động ánh xạ với file .env
    """
    # 1. Cấu hình AI (Hỗ trợ cả 2 tên biến để tránh lỗi tương thích ngược)
    GOOGLE_API_KEYS: str = Field(default="")
    GOOGLE_API_KEY: str = Field(default="")
    
    # 2. Cấu hình Github (Code của team)
    GITHUB_TOKEN: str = Field(default="")
    GITHUB_OWNER: str = Field(default="")
    GITHUB_REPO: str = Field(default="")

    # extra="ignore" giúp tránh crash nếu file .env có những biến lạ khác
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# Khởi tạo đối tượng settings duy nhất để toàn dự án sử dụng
settings = Settings()

# Đảm bảo nếu dùng GOOGLE_API_KEY cũ thì GOOGLE_API_KEYS cũng nhận được giá trị
if not settings.GOOGLE_API_KEYS and settings.GOOGLE_API_KEY:
    settings.GOOGLE_API_KEYS = settings.GOOGLE_API_KEY