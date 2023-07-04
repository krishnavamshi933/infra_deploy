import boto3

# Set your desired region
region = "us-west-2"

# Create EC2 client
ec2_client = boto3.client('ec2', region_name=region)

# Specify your existing key pair name
key_pair_name = "your-existing-key-pair-name"

# Create Nginx Load Balancer Security Group
nginx_sg = ec2_client.create_security_group(
    GroupName="nginx-sg",
    Description="Security group for Nginx",
    VpcId="your-vpc-id"  # Replace with your VPC ID
)
nginx_sg_id = nginx_sg['GroupId']

# Add rule to allow incoming HTTP traffic (port 80) from anywhere
ec2_client.authorize_security_group_ingress(
    GroupId=nginx_sg_id,
    IpProtocol="tcp",
    FromPort=80,
    ToPort=80,
    CidrIp="0.0.0.0/0"
)

# Create Django Servers Security Group
django_sg = ec2_client.create_security_group(
    GroupName="django-sg",
    Description="Security group for Django servers",
    VpcId="your-vpc-id"  # Replace with your VPC ID
)
django_sg_id = django_sg['GroupId']

# Add rule to allow incoming traffic from Nginx Load Balancer (port 80)
ec2_client.authorize_security_group_ingress(
    GroupId=django_sg_id,
    IpProtocol="tcp",
    FromPort=80,
    ToPort=80,
    SourceSecurityGroupId=nginx_sg_id
)

# Add rule to allow incoming traffic from DB server (port 5432)
ec2_client.authorize_security_group_ingress(
    GroupId=django_sg_id,
    IpProtocol="tcp",
    FromPort=5432,
    ToPort=5432,
    SourceSecurityGroupId=db_sg_id  # Replace with the security group ID for DB server
)

# Create DB Server Security Group
db_sg = ec2_client.create_security_group(
    GroupName="db-sg",
    Description="Security group for PostgreSQL database server",
    VpcId="your-vpc-id"  # Replace with your VPC ID
)
db_sg_id = db_sg['GroupId']

# Add rule to allow incoming traffic from Django servers (port 5432)
ec2_client.authorize_security_group_ingress(
    GroupId=db_sg_id,
    IpProtocol="tcp",
    FromPort=5432,
    ToPort=5432,
    SourceSecurityGroupId=django_sg_id
)

# Create Nginx Load Balancer
nginx_lb = ec2_client.run_instances(
    ImageId='ami-0c94855ba95c71c99',  # Replace with your desired Nginx AMI ID
    InstanceType='t2.micro',  # Replace with your desired instance type
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'nginx-lb'
                },
            ]
        },
    ],
    NetworkInterfaces=[
        {
            'DeviceIndex': 0,
            'SubnetId': 'your-subnet-id',  # Replace with your subnet ID
            'Groups': [nginx_sg_id],
            'AssociatePublicIpAddress': False,
        },
    ],
    InstanceInitiatedShutdownBehavior='terminate',
    KeyName=key_pair_name
)

# Create Django App Instances
django_app_1 = ec2_client.run_instances(
    ImageId='ami-0c94855ba95c71c99',  # Replace with your desired Django AMI ID
    InstanceType='t2.micro',  # Replace with your desired instance type
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'django-app-1'
                },
            ]
        },
    ],
    NetworkInterfaces=[
        {
            'DeviceIndex': 0,
            'SubnetId': 'your-subnet-id',  # Replace with your subnet ID
            'Groups': [django_sg_id, nginx_sg_id],
            'AssociatePublicIpAddress': False,
        },
    ],
    InstanceInitiatedShutdownBehavior='terminate',
    KeyName=key_pair_name
)

django_app_2 = ec2_client.run_instances(
    ImageId='ami-0c94855ba95c71c99',  # Replace with your desired Django AMI ID
    InstanceType='t2.micro',  # Replace with your desired instance type
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'django-app-2'
                },
            ]
        },
    ],
    NetworkInterfaces=[
        {
            'DeviceIndex': 0,
            'SubnetId': 'your-subnet-id',  # Replace with your subnet ID
            'Groups': [django_sg_id, nginx_sg_id],
            'AssociatePublicIpAddress': False,
        },
    ],
    InstanceInitiatedShutdownBehavior='terminate',
    KeyName=key_pair_name
)

# Create PostgreSQL Database Instance
postgres_db = ec2_client.run_instances(
    ImageId='ami-0c94855ba95c71c99',  # Replace with your desired PostgreSQL AMI ID
    InstanceType='t2.micro',  # Replace with your desired instance type
    MinCount=1,
    MaxCount=1,
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'postgres-db'
                },
            ]
        },
    ],
    NetworkInterfaces=[
        {
            'DeviceIndex': 0,
            'SubnetId': 'your-subnet-id',  # Replace with your subnet ID
            'Groups': [db_sg_id],
            'AssociatePublicIpAddress': False,
        },
    ],
    InstanceInitiatedShutdownBehavior='terminate',
    KeyName=key_pair_name
)

# Get the instance IDs
nginx_lb_instance_id = nginx_lb['Instances'][0]['InstanceId']
django_app_1_instance_id = django_app_1['Instances'][0]['InstanceId']
django_app_2_instance_id = django_app_2['Instances'][0]['InstanceId']
postgres_db_instance_id = postgres_db['Instances'][0]['InstanceId']
