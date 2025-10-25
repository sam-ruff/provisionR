"""Global configuration management with database persistence."""
import json
from sqlalchemy.orm import Session
from provisionR.models import GlobalConfig, DBGlobalConfig, TargetOS
from provisionR.database import SessionLocal


def get_global_config_from_db(db: Session) -> GlobalConfig:
    """
    Get the global configuration from the database.

    If no config exists, create and return the default config.
    """
    db_config = db.query(DBGlobalConfig).first()

    if db_config is None:
        # Create default config
        default_config = GlobalConfig()
        db_config = DBGlobalConfig(
            target_os=default_config.target_os.value,
            generate_passwords=default_config.generate_passwords,
            values=json.dumps(default_config.values),
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)

    # Convert DB model to Pydantic model
    return GlobalConfig(
        target_os=TargetOS(db_config.target_os),
        generate_passwords=db_config.generate_passwords,
        values=json.loads(db_config.values) if db_config.values else {},
    )


def update_global_config_in_db(db: Session, new_config: GlobalConfig) -> GlobalConfig:
    """
    Update the global configuration in the database.

    If no config exists, create it. Otherwise update the existing one.
    """
    db_config = db.query(DBGlobalConfig).first()

    if db_config is None:
        # Create new config
        db_config = DBGlobalConfig(
            target_os=new_config.target_os.value,
            generate_passwords=new_config.generate_passwords,
            values=json.dumps(new_config.values),
        )
        db.add(db_config)
    else:
        # Update existing config
        db_config.target_os = new_config.target_os.value
        db_config.generate_passwords = new_config.generate_passwords
        db_config.values = json.dumps(new_config.values)

    db.commit()
    db.refresh(db_config)

    return GlobalConfig(
        target_os=TargetOS(db_config.target_os),
        generate_passwords=db_config.generate_passwords,
        values=json.loads(db_config.values),
    )
