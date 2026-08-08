import logging

from src.iam_policy_manager.managers.policy_manager import PolicyManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def main():

    logger.info("Starting IAM Policy Manager")

    manager = PolicyManager()

    manager.sync()

    logger.info("IAM Policy Manager sync completed successfully")


if __name__ == "__main__":
    main()