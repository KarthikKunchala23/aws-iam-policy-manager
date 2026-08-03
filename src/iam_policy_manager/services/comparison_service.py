import json
from copy import deepcopy


class ComparisonService:

    def normalize(self, policy: dict) -> dict:
        """
        Normalize policy JSON before comparison.
        """

        normalized = deepcopy(policy)

        for statement in normalized.get("Statement", []):

            if isinstance(statement.get("Action"), list):
                statement["Action"] = sorted(statement["Action"])

            if isinstance(statement.get("Resource"), list):
                statement["Resource"] = sorted(statement["Resource"])

        return normalized

    def compare(self, local_policy: dict, aws_policy: dict) -> bool:
        """
        Returns True if policies are identical.
        """

        return (
            json.dumps(self.normalize(local_policy), sort_keys=True)
            ==
            json.dumps(self.normalize(aws_policy), sort_keys=True)
        )