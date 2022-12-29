import aws_cdk as core
from constructs import Construct
from aws_cdk import App, Environment, Stack
from aws_cdk.assertions import Template
import aws_cdk.assertions as assertions

from b_code_challenge.b_code_challenge_stack import BCodeChallengeStack
import os
import app
import pytest

# Generate Config
props = app.build_config(os.environ.get("ENV") or "dev")
infra_stack_name = f"test-{props['app']}-infrastructure-cdk-stack-{props['account_id']}-{props['environment']}"


@pytest.fixture
def template():
    app = App()
    deployment_environment = Environment(
        account=props["account_id"], region=props["region"]
    )

    infra_stack = BCodeChallengeStack(
        scope=app,
        construct_id=infra_stack_name,
        props=props,
        description=f"{props['org']} {props['app']} Infrastructure CDK Test Stack",
        env=deployment_environment,
    )
    template = Template.from_stack(infra_stack)
    return template

def test_app_loggroup_created(template):
    template.has_resource(
        "AWS::Logs::LogGroup",
        {
            "Properties": {
                "LogGroupName": f"{props['app'].lower()}",
                "RetentionInDays": 365,
            },
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete"
        }
    )
