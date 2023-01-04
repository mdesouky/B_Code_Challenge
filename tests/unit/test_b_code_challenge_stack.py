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
                "LogGroupName": f"/{props['org'].lower()}/{props['app'].lower()}",
                "RetentionInDays": 365,
            },
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete"
        }
    )

def test_app_content_bucket_created(template):
    template.has_resource(
        "AWS::S3::Bucket",
        {
            "Properties": {
                "BucketName": f"{props['org'].lower()}-{props['app'].lower()}-content-bucket-{props['account_id']}-{props['region']}-{props['environment']}",
                "PublicAccessBlockConfiguration": {
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True
                }
            },
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete"
        }
    )

def test_app_instance_role_created(template):
    template.has_resource(
        "AWS::IAM::Role",
        {
            "Properties": {
                "AssumeRolePolicyDocument": {
                    "Statement": [
                        {
                            "Action": "sts:AssumeRole",
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "ec2.amazonaws.com"
                            }
                        }
                    ],
                    "Version": "2012-10-17"
                },
                "ManagedPolicyArns": [
                    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
                    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
                ],
            "RoleName": f"{props['app'].lower()}-Instance-Role"
            }
        }
    )

def test_cw_config_ssm_parameter_created(template):
    template.has_resource(
        "AWS::SSM::Parameter",
        {
            "Properties": {
                "Name": f"/{props['org'].lower()}/{props['app'].lower()}/{props['environment']}/cloudwatch_config",
            },
        }
    )

def test_app_security_group_created(template):
    template.has_resource(
        "AWS::EC2::SecurityGroup",
        {
            "Properties": {
                "GroupName": f"{props['app'].lower()}-Security-Group",
                "SecurityGroupEgress": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Allow all outbound traffic by default",
                        "IpProtocol": "-1"
                    }
                ],
                "SecurityGroupIngress": [
                    {
                        "CidrIp": "0.0.0.0/0",
                        "Description": "Allow HTTP From World",
                        "FromPort": 80,
                        "IpProtocol": "tcp",
                        "ToPort": 80
                    }
                ]
            },
        }
    )

def test_app_instance_created(template):
    template.has_resource(
        "AWS::EC2::Instance",
        {
            "Properties": {
                "BlockDeviceMappings": [
                    {
                        "DeviceName": "/dev/xvda",
                        "Ebs": {
                            "VolumeSize": "30",
                            "VolumeType": "gp2",
                            "DeleteOnTermination": "true"
                        }
                    }
                ],
                "InstanceType": props["instance_type"]
            },
        }
    )