from pathlib import Path
import json
import logging

from src.iam_policy_manager.models.policy import Policy

logger = logging.getLogger(__name__)


class FileService:
    """
    Handles reading and writing policy files.
    """

    def save_policy(
        self,
        policy: Policy,
        target_path: Path
    ) -> Path:
        """
        Save a policy document to the specified target path.
        """

        target_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with target_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                policy.document,
                file,
                indent=4
            )

        logger.info(
            "Saved policy to %s",
            target_path
        )

        return target_path

    def load_policy(
        self,
        policy_path: Path
    ) -> dict:

        with policy_path.open(
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)