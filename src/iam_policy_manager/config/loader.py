from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "policy_name",
    "description",
    "actions",
    "resources"
]


def load_config(config_path: Path | None = None) -> dict:
    """
    Load application configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        dict: Configuration dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the YAML is invalid.
    """

    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"

    logger.info(f"Loading configuration from {config_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with config_path.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        logger.info("Configuration loaded successfully.")

        validate_config(config)
        return config

    except yaml.YAMLError:
        logger.exception("Invalid YAML configuration.")
        raise

    except Exception:
        logger.exception("Failed to load configuration.")
        raise


def validate_config(config: dict) -> None:
    """
    Validate the loaded configuration.

    Args:
        config: Configuration dictionary.

    Raises:
        ValueError: If required fields are missing.
    """

    for field in REQUIRED_FIELDS:
        if field not in config:
            raise ValueError(f"Missing required configuration: '{field}'")

    if not isinstance(config["actions"], list):
        raise ValueError("'actions' must be a list.")

    if not isinstance(config["resources"], list):
        raise ValueError("'resources' must be a list.")