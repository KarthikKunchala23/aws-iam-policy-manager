from pathlib import Path
import json

from jinja2 import Environment, FileSystemLoader

from src.iam_policy_manager.models.policy import Policy
from src.iam_policy_manager.services.mapping_service import (
    MappingService
)


def resolve_substitutions(
    substitute: dict,
    mapping_service: MappingService
) -> list[dict]:
    """
    Resolve substitution configuration and generate
    all required substitution combinations.
    """

    resolved = [{}]

    for key, value in substitute.items():

        if isinstance(value, list):

            new_resolved = []

            for existing in resolved:

                for item in value:

                    context = existing.copy()
                    context[key] = item

                    new_resolved.append(context)

            resolved = new_resolved

        elif isinstance(value, str):

            new_resolved = []

            for existing in resolved:

                resolved_value = mapping_service.resolve(
                    value,
                    existing
                )

                context = existing.copy()
                context[key] = resolved_value

                new_resolved.append(context)

            resolved = new_resolved

        else:

            for existing in resolved:
                existing[key] = value

    return resolved


def resolve_path(
    path_template: str,
    context: dict
) -> Path:
    """
    Resolve Python-style placeholders in a path.

    Example:

        {environment}
        {team}
        {account}

    """

    try:
        resolved_path = path_template.format(
            **context
        )
    except KeyError as exc:
        raise KeyError(
            f"Missing substitution '{exc.args[0]}' "
            f"required by path '{path_template}'"
        ) from exc

    return Path(resolved_path)


def render_policy(
    config: dict,
    policy_generator: dict,
    config_root: Path
) -> list[dict]:
    """
    Generate IAM Policy objects from a policy generator.
    """

    mappings = config.get(
        "mappings",
        {}
    )

    mapping_service = MappingService(
        mappings
    )

    substitute = policy_generator.get(
        "substitute",
        {}
    )

    substitutions = resolve_substitutions(
        substitute,
        mapping_service
    )

    template_path_template = policy_generator[
        "template_path"
    ]

    target_path_template = policy_generator[
        "target_policy_path"
    ]

    policies = []

    for context in substitutions:

        # -------------------------------------------------
        # Resolve template path
        # -------------------------------------------------

        template_relative_path = resolve_path(
            template_path_template,
            context
        )

        template_path = (
            config_root /
            template_relative_path
        ).resolve()

        if not template_path.exists():
            raise FileNotFoundError(
                f"Template not found: {template_path}"
            )

        # -------------------------------------------------
        # Load Jinja template
        # -------------------------------------------------

        environment = Environment(
            loader=FileSystemLoader(
                template_path.parent
            )
        )

        template = environment.get_template(
            template_path.name
        )

        # -------------------------------------------------
        # Render JSON policy document
        # -------------------------------------------------

        rendered = template.render(
            **context
        )

        document = json.loads(
            rendered
        )

        # -------------------------------------------------
        # Generate unique IAM policy name
        # -------------------------------------------------

        policy_name = (
            f"{policy_generator['name']}"
            f"_{context['environment']}"
            f"_{context['team']}"
        )

        # -------------------------------------------------
        # Resolve target file path
        # -------------------------------------------------

        target_relative_path = resolve_path(
            target_path_template,
            context
        )

        target_policy_path = (
            config_root /
            target_relative_path
        ).resolve()

        # -------------------------------------------------
        # Create Policy object
        # -------------------------------------------------

        policy = Policy(
            policy_name=policy_name,
            description=policy_generator.get(
                "description",
                ""
            ),
            document=document
        )

        policies.append(
            {
                "policy": policy,
                "target_policy_path": target_policy_path,
                "context": context
            }
        )

    return policies