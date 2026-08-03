from pathlib import Path
import logging

from src.iam_policy_manager.config.loader import load_config
from src.iam_policy_manager.services.template_service import render_policy
from src.iam_policy_manager.services.file_service import FileService

logger = logging.getLogger(__name__)


class PolicyManager:
    """
    Coordinates the end-to-end policy generation workflow.
    """

    def __init__(self) -> None:
        self.file_service = FileService()

    def sync(self) -> None:
        """
        Generate IAM policies from all YAML configuration files.
        """

        project_root = Path(__file__).resolve().parents[3]

        config_directory = project_root / "configs" / "services"

        logger.info("Reading configurations from %s", config_directory)

        for config_file in config_directory.glob("*.yaml"):

            logger.info("Processing %s", config_file.name)

            try:
                config = load_config(config_file)

                policy = render_policy(
                    config,
                    config.get("template", "managed_policy.j2")
                )

                output = self.file_service.save_policy(policy)

                logger.info(
                    "Generated policy saved at %s",
                    output
                )

            except Exception:
                logger.exception(
                    "Failed to process %s",
                    config_file.name
                )