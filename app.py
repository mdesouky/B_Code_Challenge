#!/usr/bin/env python3
import os, sys
from aws_cdk import App, Environment
import aws_cdk as cdk
import yaml

from b_code_challenge.b_code_challenge_stack import BCodeChallengeStack


app = cdk.App()

def build_config(env: str):
    """This a function that generates stack properties based on Environment, basically reads a yaml
    file with the environment name, parses it and returns a dict

    Args:
        env (str): The Environment Name i.e dev/prod

    Returns:
        config (dict): a dictionary of properties/config values for the CDK stack
    """
    with open(f"config/{env}.yaml") as yaml_config:
        try:
            build_config = yaml.safe_load(yaml_config)
        except yaml.YAMLError as exc:
            print(exc)
        except: #handle other exceptions
            print ("Unexpected error:", sys.exc_info()[0])
        build_config['environment']=env
    return build_config


environment = os.environ.get("ENV") or "dev"

# Generate Config
props = build_config(environment)


deployment_environment = Environment(
    account=props["account_id"], region=props["region"]
)
infra_stack_name = f"{props['app']}-infra-cdk-stack-{props['account_id']}-{props['environment']}"


BCodeChallengeStack(
    scope=app,
    construct_id=infra_stack_name,
    props=props,
    description=f"{props['org']} {props['app']} Infrastructure CDK Stack",
    env=deployment_environment,
    )

app.synth()
