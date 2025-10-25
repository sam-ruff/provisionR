"""Database models for provisionR."""

from enum import Enum
from typing import Dict, Any
from datetime import datetime, UTC
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from provisionR.database import Base


class TargetOS(str, Enum):
    """Supported target operating systems."""

    ROCKY9 = "Rocky9"
    UBUNTU2504 = "Ubuntu25.04"


# Pydantic models for API validation
class GlobalConfig(BaseModel):
    """Global configuration for provisionR."""

    target_os: TargetOS = Field(
        default=TargetOS.ROCKY9, description="Target operating system"
    )
    generate_passwords: bool = Field(
        default=True, description="Whether to auto-generate passwords"
    )
    values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom key-value pairs available during templating",
    )


# SQLAlchemy models for database persistence
class DBGlobalConfig(Base):
    """Database model for global configuration."""

    __tablename__ = "global_config"

    id = Column(Integer, primary_key=True, index=True)
    target_os = Column(String, nullable=False, default="Rocky9")
    generate_passwords = Column(Boolean, nullable=False, default=True)
    values = Column(Text, nullable=False, default="{}")  # JSON string
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class DBMachinePasswords(Base):
    """Database model for storing machine-specific passwords."""

    __tablename__ = "machine_passwords"

    id = Column(Integer, primary_key=True, index=True)
    mac = Column(String, nullable=False, index=True)
    uuid = Column(String, nullable=False, index=True)
    serial = Column(String, nullable=False, index=True)
    root_password = Column(String, nullable=False)
    user_password = Column(String, nullable=False)
    luks_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    # Composite unique constraint on mac+uuid+serial
    __table_args__ = ({"sqlite_autoincrement": True},)
