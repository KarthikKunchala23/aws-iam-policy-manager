from dataclasses import dataclass, field
from typing import Any


@dataclass
class Policy:
    """
    Represents an AWS IAM Managed Policy.
    """

    policy_name: str
    description: str
    document: dict[str, Any]
    path: str = "/"
    tags: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Policy object into a dictionary.

        Returns:
            dict: Policy attributes as a dictionary.
        """
        return {
            "policy_name": self.policy_name,
            "description": self.description,
            "document": self.document,
            "path": self.path,
            "tags": self.tags,
        }