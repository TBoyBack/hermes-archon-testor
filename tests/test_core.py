"""
核心模块单元测试

测试配置管理和日志工具的基本功能
"""

import os
import sys
from pathlib import Path

import pytest

# 确保 src 目录在路径中
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestConfig:
    """配置管理测试"""
    
    def test_settings_defaults(self):
        """测试默认配置"""
        from src.core.config import Settings
        
        settings = Settings()
        assert settings.app.name == "hermes-archon-testor"
        assert settings.app.version == "1.0.0"
        assert settings.app.env == "development"
    
    def test_hermes_config_defaults(self):
        """测试 Hermes 默认配置"""
        from src.core.config import HermesConfig
        
        config = HermesConfig()
        assert config.host == "localhost"
        assert config.port == 8080
        assert config.model == "gpt-4"
        assert config.timeout == 30
    
    def test_database_config(self):
        """测试数据库配置"""
        from src.core.config import DatabaseConfig
        
        config = DatabaseConfig(
            postgres_host="db.example.com",
            postgres_port=5432,
            postgres_user="test",
            postgres_password="secret",
            postgres_db="testdb",
        )
        
        assert config.postgres_host == "db.example.com"
        assert "test:secret@db.example.com" in config.postgres_url
        assert "testdb" in config.postgres_url
    
    def test_redis_url_generation(self):
        """测试 Redis URL 生成"""
        from src.core.config import DatabaseConfig
        
        # 无密码
        config = DatabaseConfig(redis_host="redis.local", redis_port=6380)
        assert config.redis_url == "redis://redis.local:6380/0"
        
        # 有密码
        config = DatabaseConfig(redis_host="redis.local", redis_password="pwd")
        assert "redis://:pwd@redis.local" in config.redis_url
    
    def test_config_get_method(self):
        """测试配置获取方法"""
        from src.core.config import Config, Settings
        
        settings = Settings()
        config = Config(settings)
        
        # 测试嵌套访问
        assert config.get("hermes.host") == "localhost"
        assert config.get("hermes.port") == 8080
        assert config.get("app.name") == "hermes-archon-testor"
        
        # 测试默认值
        assert config.get("nonexistent.key", "default") == "default"
    
    def test_validate_config(self):
        """测试配置验证"""
        from src.core.config import validate_config
        
        # 默认配置应该有一些警告
        warnings = validate_config()
        assert isinstance(warnings, list)
    
    def test_env_override(self):
        """测试环境变量覆盖"""
        from src.core.config import Settings
        
        # 设置环境变量
        os.environ["HERMES_MODEL"] = "gpt-3.5-turbo"
        os.environ["HERMES_ENV"] = "production"
        
        settings = Settings()
        assert settings.hermes.model == "gpt-3.5-turbo"
        assert settings.app.env == "production"
        
        # 清理
        del os.environ["HERMES_MODEL"]
        del os.environ["HERMES_ENV"]


class TestLogger:
    """日志工具测试"""
    
    def test_logger_creation(self):
        """测试日志实例创建"""
        from src.core.logger import Logger, logger
        
        assert isinstance(logger, Logger)
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")
    
    def test_logger_context(self):
        """测试日志上下文"""
        from src.core.logger import logger
        
        logger.clear_context()
        logger.add_context(user_id=123, action="test")
        
        # 验证上下文添加成功
        assert logger._context.get("user_id") == 123
    
    def test_logger_context_manager(self):
        """测试上下文管理器"""
        from src.core.logger import logger
        
        logger.clear_context()
        
        with logger.context(temp_key="temp_value"):
            assert logger._context.get("temp_key") == "temp_value"
        
        # 退出后上下文应该恢复
        assert logger._context.get("temp_key") is None
    
    def test_get_logger_with_name(self):
        """测试带名称的日志实例"""
        from src.core.logger import get_logger
        
        named_logger = get_logger("test_module")
        assert named_logger is not None
    
    def test_logger_section(self):
        """测试日志分区"""
        from src.core.logger import logger
        
        section = logger.section("Test Section")
        assert section is not None
    
    def test_logger_profile(self):
        """测试性能追踪"""
        from src.core.logger import logger
        import time
        
        with logger.profile("test_operation"):
            time.sleep(0.01)  # 模拟操作
        
        # 如果没有异常，说明追踪成功


class TestIntegration:
    """集成测试"""
    
    def test_config_and_logger_import(self):
        """测试配置和日志模块导入"""
        from src.core import config, logger
        
        assert hasattr(config, "settings")
        assert hasattr(logger, "info")
    
    def test_settings_singleton(self):
        """测试设置单例"""
        from src.core.config import settings
        
        assert settings is not None
        assert settings.app.name == "hermes-archon-testor"


# pytest 配置
def pytest_configure(config: Any) -> None:
    """pytest 配置钩子"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
