from pathlib import Path
import json
import logging

from src.iam_policy_manager.models.policy import Policy

logger = logging.getLogger(__name__)


class FileService:
    """
    Handles reading and writing policy files.
    """

    def __init__(self, policy_directory: Path | None = None):
        self.policy_directory = policy_directory or Path("policies/generated")
        self.policy_directory.mkdir(parents=True, exist_ok=True)

    def save_policy(self, policy: Policy) -> Path:
        """
        Save a policy document to disk.
        """

        file_path = self.policy_directory / f"{policy.policy_name}.json"

        with file_path.open("w", encoding="utf-8") as file:
            json.dump(policy.document, file, indent=4)

        logger.info("Saved policy to %s", file_path)

        return file_path

    def load_policy(self, policy_name: str) -> dict:

        file_path = self.policy_directory / f"{policy_name}.json"

        with file_path.open("r", encoding="utf-8") as file:
            return json.load(file)