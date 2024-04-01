import boto3
import argparse
import os

deploy = False
force = False


def create_arg_parser():
    parser = argparse.ArgumentParser(description="Deploy to AWS")
    parser.add_argument("--action", type=str, help="Action to perform on AWS (create | update | delete)")
    parser.add_argument("--list-and-update", action="store_true", help="List and update AWS resources")
    parser.add_argument("--region", type=str, default="us-east-1", help="AWS Region")
    parser.add_argument("--profile", type=str, default="default", help="AWS Profile")
    parser.add_argument("--tag", type=str, default="bedtime_bot", help="Tag to use for resources")
    parser.add_argument("--key-pair", type=str, default="channel-bot-key-pair", help="Key pair to use for resources")
    parser.add_argument("--deploy", action="store_true", help="Deploy AWS resources")
    parser.add_argument("--force", action="store_true", help="Force deploy AWS resources")

    # TODO: add more arguments
    return parser


def action_check(args):
    if args.deploy:
        global deploy
        deploy = True
    if args.force:
        global force
        force = True


def validate_args(args):
    if args.action == "create":
        print("create" + " TEST" if deploy else "")
    elif args.action == "update":
        print("update" + " TEST" if deploy else "")
    elif args.action == "delete":
        print("delete" + " TEST" if deploy else "")
    elif args.list_and_update:
        print("list_and_update")
    else:
        return False

    return True


def create_ec2_client(region, profile):
    return boto3.client("ec2", region_name=region, profile_name=profile)


def create_ec2_instance(region, profile, tag):
    ec2 = create_ec2_client(region, profile)
    instances = ec2.create_instances(
        ImageId='ami-0c101f26f147fa7fd',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName='ec2-keypair',
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': tag
                    },
                ]
            },
        ])
    # TODO: add keypair, name, and create sg
    return instances


if __name__ == "__main__":
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()
    print(f"args action: {args}")
    if not validate_args(args):
        arg_parser.print_help()
        exit(1)
