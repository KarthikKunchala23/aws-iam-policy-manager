from pathlib import Path
import logging

from src.iam_policy_manager.config.loader import load_config
from src.iam_policy_manager.services.template_service import (
    render_policy
)
from src.iam_policy_manager.services.file_service import FileService
from src.iam_policy_manager.services.aws_iam_service import AWSIAMService
from src.iam_policy_manager.services.comparison_service import (
    ComparisonService
)


logger = logging.getLogger(__name__)


class PolicyManager:
    """
    Coordinates the end-to-end policy generation workflow.
    """

    def __init__(self) -> None:
        self.file_service = FileService()
        self.aws_iam_service = AWSIAMService()
        self.comparison_service = ComparisonService()

    def sync(self, config_file: str) -> None:
        """
        Generate IAM policies from the single YAML
        configuration file.
        """

        project_root = Path(__file__).resolve().parents[3]

        config_path = (
            project_root / "configs" / config_file
        ).resolve()

        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        if config_path.suffix not in {".yaml", ".yml"}:
            raise ValueError(
                f"Configuration file must be YAML: {config_path}"
            )

        logger.info(
            "Processing configuration %s",
            config_path
        )

        config = load_config(config_path)

        config_root = config_path.parent

        for generator in config.get(
            "policy_generators",
            []
        ):

            logger.info(
                "Processing policy generator '%s'",
                generator["name"]
            )

            policies = render_policy(
                config,
                generator,
                config_root
            )

            for generated in policies:

                policy = generated["policy"]

                target_policy_path = generated[
                    "target_policy_path"
                ]

                context = generated[
                    "context"
                ]

                logger.info(
                    "Generated policy '%s' "
                    "with context: %s",
                    policy.policy_name,
                    context
                )

                # Save generated JSON locally
                output = self.file_service.save_policy(
                    policy,
                    target_policy_path
                )

                logger.info(
                    "Generated policy saved at %s",
                    output
                )

                # Sync policy with AWS IAM
                self.sync_policy_to_aws(policy)

    def sync_policy_to_aws(self, policy) -> None:
        """
        Sync the generated Policy object
        to AWS IAM.
        """

        policy_name = policy.policy_name

        # ---------------------------------------------------------
        # 1. Check whether policy exists in AWS
        # ---------------------------------------------------------

        if self.aws_iam_service.policy_exists(
            policy_name
        ):

            logger.info(
                "Policy '%s' exists in AWS IAM. "
                "Checking for changes.",
                policy_name
            )

            # -----------------------------------------------------
            # 2. Get the current policy document from AWS
            # -----------------------------------------------------

            aws_policy_document = (
                self.aws_iam_service.get_default_policy_document(
                    policy_name
                )
            )

            # -----------------------------------------------------
            # 3. Compare local policy with AWS policy
            # -----------------------------------------------------

            policies_match = (
                self.comparison_service.compare(
                    policy.document,
                    aws_policy_document
                )
            )

            # -----------------------------------------------------
            # 4. If policies are identical, do nothing
            # -----------------------------------------------------

            if policies_match:

                logger.info(
                    "Policy '%s' is already up to date. "
                    "No AWS update required.",
                    policy_name
                )

                return

            # -----------------------------------------------------
            # 5. Policies are different → create new version
            # -----------------------------------------------------

            logger.info(
                "Policy '%s' has changed. "
                "Creating new policy version.",
                policy_name
            )

            new_version = (
                self.aws_iam_service.create_policy_version(
                    policy_name,
                    policy.document
                )
            )

            logger.info(
                "Created new policy version '%s' "
                "for policy '%s'",
                new_version[
                    "PolicyVersion"
                ]["VersionId"],
                policy_name
            )

        # ---------------------------------------------------------
        # 6. Policy does not exist → create it
        # ---------------------------------------------------------

        else:

            logger.info(
                "Policy '%s' does not exist in AWS IAM. "
                "Creating policy.",
                policy_name
            )

            created_policy = (
                self.aws_iam_service.create_policy(
                    policy
                )
            )

            logger.info(
                "Created new policy '%s' with ARN '%s'",
                created_policy[
                    "Policy"
                ]["PolicyName"],
                created_policy[
                    "Policy"
                ]["Arn"]
            )