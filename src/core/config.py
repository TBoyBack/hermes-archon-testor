"""
配置管理模块

提供统一的配置加载和管理功能，支持多种配置源：
- 环境变量
- .env 文件
- YAML 配置文件
- 默认值
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class HermesConfig(BaseModel):
    """Hermes Agent 配置"""
    host: str = "localhost"
    port: int = 8080
    api_key: Optional[str] = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 30
    retry_count: int = 3


class ArchonConfig(BaseModel):
    """Archon 工作流引擎配置"""
    workflows_dir: str = "./.archon/workflows"
    skills_dir: str = "./.archon/skills"
    max_parallel: int = 4
    default_timeout: int = 300
    retry_count: int = 3
    cache_enabled: bool = True
    cache_ttl: int = 86400


class DatabaseConfig(BaseModel):
    """数据库配置"""
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "hermes"
    postgres_password: Optional[str] = None
    postgres_db: str = "hermes"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    @property
    def postgres_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = "INFO"
    dir: str = "./logs"
    max_size: str = "100MB"
    backup_count: int = 5


class AppConfig(BaseModel):
    """应用配置"""
    name: str = "hermes-archon-testor"
    version: str = "1.0.0"
    env: str = "development"
    debug: bool = False


class Settings(BaseSettings):
    """全局配置设置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    app: AppConfig = Field(default_factory=AppConfig)
    hermes: HermesConfig = Field(default_factory=HermesConfig)
    archon: ArchonConfig = Field(default_factory=ArchonConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    
    hermes_api_key: Optional[str] = Field(default=None, alias="HERMES_API_KEY")
    hermes_model: str = Field(default="gpt-4", alias="HERMES_MODEL")
    db_password: Optional[str] = Field(default=None, alias="HERMES_DB_PASSWORD")
    env_mode: str = Field(default="development", alias="HERMES_ENV")
    log_level: str = Field(default="INFO", alias="HERMES_LOG_LEVEL")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.hermes_api_key:
            self.hermes.api_key = self.hermes_api_key
        if self.hermes_model:
            self.hermes.model = self.hermes_model
        if self.db_password:
            self.database.postgres_password = self.db_password
        if self.env_mode:
            self.app.env = self.env_mode
        if self.log_level:
            self.logging.level = self.log_level


class Config:
    """配置管理器"""
    
    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or Settings()
    
    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> "Config":
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        settings = Settings(**cls._flatten_dict(data))
        return cls(settings)
    
    @classmethod
    def from_env(cls) -> "Config":
        return cls(Settings())
    
    @classmethod
    def _flatten_dict(cls, d: Dict[str, Any], parent_key: str = "") -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}_{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(cls._flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    @property
    def settings(self) -> Settings:
        return self._settings
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._settings
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            elif isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        return self._settings.model_dump()


settings = Settings()


def validate_config() -> List[str]:
    """验证配置，返回警告列表"""
    warnings = []
    if not settings.hermes.api_key:
        warnings.append("HERMES_API_KEY 未设置，Hermes 功能可能不可用")
    if settings.app.env == "production":
        if not settings.app.debug:
            warnings.append("生产环境应设置 SECRET_KEY")
    return warnings


def print_config() -> None:
    """打印当前配置"""
    from loguru import logger
    logger.info("=" * 50)
    logger.info(f"应用: {settings.app.name} v{settings.app.version}")
    logger.info(f"环境: {settings.app.env}")
    logger.info(f"Hermes: {settings.hermes.host}:{settings.hermes.port}")
    logger.info(f"Hermes 模型: {settings.hermes.model}")
    logger.info("=" * 50)
