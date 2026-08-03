import json
import boto3


class AWSIAMService:

    def __init__(self):

        self.client = boto3.client("iam")

    def policy_exists(self, policy_arn: str) -> bool:

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

    def get_default_policy_document(self, policy_arn):

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
        policy_arn,
        document
    ):

        return self.client.create_policy_version(

            PolicyArn=policy_arn,

            PolicyDocument=json.dumps(document),

            SetAsDefault=True
        )