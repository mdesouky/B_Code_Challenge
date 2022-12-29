from aws_cdk import Tags

import os


def add_tagging(self, props):
    Tags.of(self).add(key=f"{props['org']}:cost-allocation:ApplicationId", value=props["app"])
    Tags.of(self).add(key=f"{props['org']}:automation:EnvironmentId",value=props["environment"])
    Tags.of(self).add(key=f"{props['org']}:automation:Deployment", value="Automated")
    Tags.of(self).add(key=f"{props['org']}:cost-allocation:AwsAccount", value=props["account_name"])
    Tags.of(self).add(key=f"{props['org']}:architecture:ServiceId", value=props["service"])
    Tags.of(self).add(key=f"{props['org']}:data:classification", value=props["data_classification"])
    Tags.of(self).add(key=f"{props['org']}:operations:Owner", value="Devops")
