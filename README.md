# B_Code_Challenge
A python CDK App to provision an EC2 instance with Apache installed on it

## Running Locally
---
### Prerequisites
1. Python3
2. AWS CLI
3. NodeJs
4. AWS CDK

## Notes
1. I've Went with CDK although the choices were Terraform or Cloudformation since CDK practically deploys a cloudformation stack and a template can be easily sythesized from the code
2. I have not spent time writing code to deploy a dedicated VPC since a [best practices VPC](https://docs.aws.amazon.com/quickstart/latest/vpc/architecture.html) done by AWS is readily available and can be easily deployed into any account
3. By design server can only be accessed using Session manager, hence no ssh key has been configured on the instance.
4. Since not much detail was given, I've configured a really simple html page to replace the default page of Apache, otherwise there should be a virtual host configured
5. Since the Instance is in a private subnet with no LB configured then it can be only tested from within the instance itself as illustrated below

```bash
[root@ip-10-10-22-169 ~]# curl 127.0.0.1
<!DOCTYPE html>
<html>
    <head>
        Welcome to B!
    </head>
    <body>
        Hello World!
    </body>
</html>
```
## Potential Improvements
1. Enable Encryption on the EBS volume for the instance
2. Enable Encryption on s3 Bucket
3. Parametrize Log group name and other variables in the cloudwatch agent json config file
4. Build a Golden AMI with packer, version it and just lookup the AMI-ID with CDK and deploy it
5. Configure an Autoscaling Group with a LB in front


### Running CDK Commands
To run CDK commands you can follow the default CDK guide at the end of this section or simply run `Make` commands which have been programmed in the [Makefile](./Makefile) to create a python virtual environment, install requirements and then run the CDK command for you such as:
`make synth`
`make test`
`make deploy` 

You can run `make help` to get more info on the different commands
```bash
> make help     

Usage:
  make <target>

Targets:
  test                 Run Unit tests on CDK code
  synth                Synthesize Cloudformation Stacks from CDK Code for the target account/environment
  diff                 Show CDK diff on the target account/environment
  context              Fetch CDK context from the target account
  deploy               Deploy All CDK Stacks into the target account
  destroy              Destroy All CDK Stacks in the target account
  bootstrap            Install Bootstrap CDK into the target account
  install-pre-commit   Install Pre-Commit Hooks
Help
  help                 Show help
```

# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
