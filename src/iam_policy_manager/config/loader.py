from pathlib import Path
import logging
import yaml

logger = logging.getLogger(__name__)

REQUIRED_FIELDS = [
    "target_policy_path",
    "mappings",
    "policy_generators",
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
    Validate the central IAM policy manager configuration.

    Args:
        config: Loaded YAML configuration.

    Raises:
        ValueError: If the configuration structure is invalid.
    """

    for field in REQUIRED_FIELDS:
        if field not in config:
            raise ValueError(
                f"Missing required configuration: '{field}'"
            )

    if not isinstance(config["mappings"], dict):
        raise ValueError("'mappings' must be a dictionary.")

    if not isinstance(config["policy_generators"], list):
        raise ValueError("'policy_generators' must be a list.")

    for generator in config["policy_generators"]:

        if not isinstance(generator, dict):
            raise ValueError(
                "Each policy generator must be a dictionary."
            )

        required_generator_fields = [
            "name",
            "template_path",
            "target_policy_path",
            "substitute",
        ]

        for field in required_generator_fields:
            if field not in generator:
                raise ValueError(
                    f"Policy generator is missing required field: "
                    f"'{field}'"
                )

        if not isinstance(generator["substitute"], dict):
            raise ValueError(
                f"'substitute' must be a dictionary in generator "
                f"'{generator['name']}'."
            )