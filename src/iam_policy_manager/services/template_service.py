from pathlib import Path
import json
import logging

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from src.iam_policy_manager.models.policy import Policy

logger = logging.getLogger(__name__)


def render_policy(
    config: dict,
    template_name: str = "managed_policy.j2"
) -> Policy:
    """
    Render an IAM policy from a Jinja2 template.

    Args:
        config: Configuration dictionary.
        template_name: Jinja2 template filename.

    Returns:
        Policy: Rendered Policy object.
    """

    try:
        project_root = Path(__file__).resolve().parents[3]
        template_dir = project_root / "templates"

        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

        template = env.get_template(template_name)

        rendered_policy = template.render(config)

        policy_document = json.loads(rendered_policy)

        logger.info(
            "Successfully rendered policy '%s'",
            config["policy_name"]
        )

        return Policy(
            policy_name=config["policy_name"],
            description=config["description"],
            document=policy_document,
            path=config.get("path", "/"),
            tags=config.get("tags", [])
        )

    except TemplateNotFound:
        logger.exception("Template '%s' not found.", template_name)
        raise

    except json.JSONDecodeError:
        logger.exception("Generated policy is not valid JSON.")
        raise

    except Exception:
        logger.exception("Failed to render policy.")
        raise