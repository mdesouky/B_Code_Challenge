from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as _s3,
    RemovalPolicy,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancing as elasticloadbalancing,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_s3_deployment as s3deploy,
    Tags
)
from constructs import Construct
from b_code_challenge.tagging import add_tagging
class BCodeChallengeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        stack=Stack.of(self)
        # Returns the AWS::AccountId for this stack (or the literal value if known)
        stack.account
        # Returns the AWS::Region for this stack (or the literal value if known)
        stack.region

        ## Cloudwatch Loggroup ##
        app_loggroup=logs.LogGroup(
            scope=self,
            id=f"{props['app']}LogGroup",
            log_group_name=f"{props['app'].lower()}",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_YEAR
        )
        ## Instance Role ##
        app_iam_role=iam.Role(
            scope=self,
            id=f"{props['app'].lower()}InstanceRole",
            role_name=f"{props['app'].lower()}-Instance-Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_managed_policy_arn(
                    scope=self,
                    id="CloudWatchAgentServerPolicy",
                    managed_policy_arn="arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
                ),
                iam.ManagedPolicy.from_managed_policy_arn(
                    scope=self,
                    id="AmazonSSMManagedInstanceCore",
                    managed_policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
                ),
            ]
        )
        app_vpc=ec2.Vpc.from_lookup(
                scope=self, id="AppVPC", vpc_name="sandbox-VPC"
            )
        ## Security Group ##
        app_security_group=ec2.SecurityGroup(
            scope=self,
            id=f"{props['app'].lower()}SecurityGroup",
            vpc=app_vpc,
            allow_all_outbound=True,
            security_group_name=f"{props['app'].lower()}-Security-Group"
        )
        app_security_group.add_ingress_rule(
            description="Allow HTTP",
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80)
        )
        ## Instance ##
        add_tagging(self, props)