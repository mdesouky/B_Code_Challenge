#!/bin/bash -xe

## Set Timezone
timedatectl set-timezone Australia/Sydney

## Install the Cloudwatch Agent
yum install -y amazon-cloudwatch-agent

## Configuring Cloudwatch agent
amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c ssm:{CW_AGENT_CONFIG_PARAMETER} -s

## Check Cloudwatch Agent Status'
amazon-cloudwatch-agent-ctl -a status


## Install the Apache web server
yum install -y httpd

## Copy Down Html Page from s3
aws s3 cp s3://{CONTENT_BUCKET}/belong-test.html /var/www/html/index.html
## Start the Apache web server
systemctl start httpd

## Configure the Apache web server to start at each system boot
systemctl enable httpd