import logging
import argparse

from src.iam_policy_manager.managers.policy_manager import PolicyManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def main():

    parser = argparse.ArgumentParser(
        description="IAM Policy Manager: Generate and sync IAM policies from YAML configurations."
    )

    parser.add_argument(
        "configs",
        nargs="+",
        help="List of YAML configuration files to process"
    )

    args = parser.parse_args()

    logger.info("Starting IAM Policy Manager")

    manager = PolicyManager()

    manager.sync(args.configs)

    logger.info("IAM Policy Manager sync completed successfully")


if __name__ == "__main__":
    main()