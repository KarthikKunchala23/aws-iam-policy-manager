import json
import boto3


class AWSIAMService:

    def __init__(self):

        self.client = boto3.client("iam")

        sts_client = boto3.client("sts")

        self.account_id = sts_client.get_caller_identity()["Account"]

    def get_policy_arn(self, policy_name: str) -> str:

        return (
            f"arn:aws:iam::{self.account_id}:policy/{policy_name}"
            )

    def policy_exists(self, policy_name: str) -> bool:

        policy_arn = self.get_policy_arn(policy_name)

        try:

            self.client.get_policy(
                PolicyArn=policy_arn
            )

            return True

        except self.client.exceptions.NoSuchEntityException:

            return False

    def create_policy(self, policy):

        return self.client.create_policy(

            PolicyName=policy.policy_name,

            PolicyDocument=json.dumps(policy.document),

            Description=policy.description,

            Path=policy.path,

            Tags=policy.tags
        )

    def get_default_policy_document(self, policy_name: str):

        policy_arn = self.get_policy_arn(policy_name)

        policy = self.client.get_policy(
            PolicyArn=policy_arn
        )

        version = policy["Policy"]["DefaultVersionId"]

        response = self.client.get_policy_version(
            PolicyArn=policy_arn,
            VersionId=version
        )

        return response["PolicyVersion"]["Document"]

    def create_policy_version(
        self,
        policy_name: str,
        document
    ):
        policy_arn = self.get_policy_arn(policy_name)

        return self.client.create_policy_version(

            PolicyArn=policy_arn,

            PolicyDocument=json.dumps(document),

            SetAsDefault=True
        )