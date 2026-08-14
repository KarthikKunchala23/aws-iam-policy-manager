import re


MAPPING_PATTERN = re.compile(
    r"^mappings\(([^,]+),\s*([^)]+)\)$"
)


class MappingService:
    """
    Resolves mapping expressions from the central configuration.
    """

    def __init__(self, mappings: dict) -> None:
        self.mappings = mappings

    def resolve(
        self,
        expression: str,
        substitutions: dict
    ):
        """
        Resolve a mapping expression such as:

            mappings(account_id, environment)

        Args:
            expression: Mapping expression.
            substitutions: Already resolved substitution values.

        Returns:
            Resolved mapping value.
        """

        match = MAPPING_PATTERN.match(expression)

        if not match:
            return expression

        mapping_name = match.group(1).strip()
        lookup_variable = match.group(2).strip()

        if mapping_name not in self.mappings:
            raise KeyError(
                f"Mapping '{mapping_name}' does not exist."
            )

        if lookup_variable not in substitutions:
            raise KeyError(
                f"Substitution '{lookup_variable}' "
                f"is required to resolve '{expression}'."
            )

        lookup_value = substitutions[lookup_variable]

        mapping = self.mappings[mapping_name]

        if lookup_value not in mapping:
            raise KeyError(
                f"Value '{lookup_value}' not found in "
                f"mapping '{mapping_name}'."
            )

        return mapping[lookup_value]