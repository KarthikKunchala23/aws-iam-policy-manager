from pathlib import Path
import logging

from src.iam_policy_manager.config.loader import load_config
from src.iam_policy_manager.services.template_service import render_policy
from src.iam_policy_manager.services.file_service import FileService
from src.iam_policy_manager.services.aws_iam_service import AWSIAMService

logger = logging.getLogger(__name__)

aws_iam_service = AWSIAMService()

class PolicyManager:
    """
    Coordinates the end-to-end policy generation workflow.
    """

    def __init__(self) -> None:
        self.file_service = FileService()

    def sync(self, config_files: list[str]) -> None:
        """
        Generate IAM policies from all YAML configuration files.
        """

        project_root = Path(__file__).resolve().parents[3]

        config_directory = project_root / "configs" / "services"

        logger.info("Reading configurations from %s", config_directory)

        # for config_file in config_directory.glob("*.yaml"):
        for config_file in config_files:
            
            config_path = (config_directory / config_file).resolve()

            config_directory = config_directory.resolve()

            if config_directory not in config_path.parents:
                raise ValueError(
                    f"Configuration must be inside {config_directory}"
                    )
            
            if not config_path.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {config_path}"
                    )

            if config_path.suffix not in {".yaml", ".yml"}:
                raise ValueError(
                    f"Configuration file must be YAML: {config_path}"
                    )

            logger.info("Processing %s", config_path.name)

            try:
                config = load_config(config_path)

                policy = render_policy(
                    config,
                    config.get("template", "managed_policy.j2")
                )

                output = self.file_service.save_policy(policy)

                logger.info(
                    "Generated policy saved at %s",
                    output
                )

                self.sync_policy_to_aws(policy)

            except Exception:
                logger.exception(
                    "Failed to process %s",
                    config_path.name
                )


    def sync_policy_to_aws(self, policy) -> None:
        """
        Sync the generated policy to AWS IAM.

        Args:
            policy: The Policy object to sync.
        """

        if aws_iam_service.policy_exists(policy.policy_name):

            logger.info(
                "Policy '%s' exists in AWS IAM. Updating policy.",
                policy.policy_name
            )

            new_version = aws_iam_service.create_policy_version(
                policy.policy_name,
                policy.document
            )

            logger.info(
                "Created new policy version '%s' for policy '%s'",
                new_version["PolicyVersion"]["VersionId"],
                policy.policy_name
            )

        else:
            logger.info(
                "Policy '%s' does not exist in AWS IAM. Creating policy.",
                policy.policy_name
            )

            created_policy = aws_iam_service.create_policy(policy)

            logger.info(
                "Created new policy '%s' with ARN '%s'",
                created_policy["Policy"]["PolicyName"],
                created_policy["Policy"]["Arn"]
            )
