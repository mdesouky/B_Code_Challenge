from aws_cdk import (
    Duration,
    Stack,
    aws_s3 as s3,
    RemovalPolicy,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancing as elasticloadbalancing,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    aws_s3_deployment as s3deploy,
    Tags
)
from constructs import Construct
from b_code_challenge.tagging import add_tagging
import sys, os

## Read User Data
with open("config/user_data/user_data.sh") as f:
    try:
        user_data_template = f.read()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
    except: #handle other exceptions
        print ("Unexpected error:", sys.exc_info()[0])

## Read Cloudwatch Config
with open("config/cloudwatch/cw_agent_config.json") as f:
    try:
        cloudwatch_config=f.read()
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
    except: #handle other exceptions
        print ("Unexpected error:", sys.exc_info()[0])
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
            log_group_name=f"/{props['org'].lower()}/{props['app'].lower()}",
            removal_policy=RemovalPolicy.DESTROY,
            retention=logs.RetentionDays.ONE_YEAR
        )

        ## Create Content s3 Bucket ##
        app_content_bucket=s3.Bucket(
            scope=self,
            id=f"{props['app'].lower()}ContentBucket",
            bucket_name=f"{props['org'].lower()}-{props['app'].lower()}-content-bucket-{stack.account}-{stack.region}-{props['environment']}",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True
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
        ## Generate Cloudwatch Config from Template and put it in ssm ##
        cw_config_parameter=ssm.StringParameter(
            scope=self,
            id=f"{props['app'].lower()}CloudwatchConfig",
            parameter_name=f"/{props['org'].lower()}/{props['app'].lower()}/{props['environment']}/cloudwatch_config",
            string_value=cloudwatch_config
        )
        # Enable reading files from s3 bucket and ssm parameter store
        read_config_policy = iam.Policy(
            scope=self,
            id="ReadConfigPolicy",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:Get*",
                        "s3:List*"],
                    resources=[
                        app_content_bucket.bucket_arn,
                        app_content_bucket.arn_for_objects("*")
                    ],
                ),
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=[
                        "s3:Describe*",
                        "s3:Get*"],
                    resources=[cw_config_parameter.parameter_arn],
                )
            ]
        )
        app_iam_role.attach_inline_policy(read_config_policy)

        app_vpc=ec2.Vpc.from_lookup(
                scope=self, id="AppVPC", vpc_id=props['vpc_id']
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
            description="Allow HTTP From World",
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80)
        )

        ## Machine Image ##
        amzn_linux_2 = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE)
        
        ## Upload HTML File ##
        deployment = s3deploy.BucketDeployment(
            scope=self,
            id="DeployWebsite",
            sources=[s3deploy.Source.asset("config/html")],
            destination_bucket=app_content_bucket,
            extract=True
        )
        ## Generate Userdata From Template ##
        user_data=user_data_template.format(
            CW_AGENT_CONFIG_PARAMETER=cw_config_parameter.parameter_name,
            CONTENT_BUCKET=app_content_bucket.bucket_name
        )

        ## Instance ##
        app_instance=ec2.Instance(
            scope=self,
            id=f"{props['app'].lower()}Instance",
            instance_name=f"{props['app']}-Instance",
            instance_type=ec2.InstanceType(props["instance_type"]),
            machine_image=amzn_linux_2,
            vpc=app_vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_group=app_security_group,
            role=app_iam_role,
            user_data_causes_replacement=True,
            user_data=ec2.UserData.custom(user_data)
        )
        app_instance.instance.add_property_override(
            "BlockDeviceMappings", [{
                "DeviceName": "/dev/xvda",
                "Ebs": {
                    "VolumeSize": "30",
                    "VolumeType": "gp2",
                    "DeleteOnTermination": "true"
                }
            }])
        add_tagging(self, props)