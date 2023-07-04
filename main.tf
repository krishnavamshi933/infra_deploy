# Define variables
variable "vpc_id" {
  default = "vpc-02bd2eed3cfb565df"  # Replace with your VPC ID
}

variable "subnet_id" {
  default = "subnet-05022afbdb17f196c"  # Replace with your subnet ID
}

variable "key_pair_name" {
  default = "uma-test"  # Replace with your key pair name
}

# Configure AWS provider
provider "aws" {
  region = "us-west-2"  # Replace with your desired region
}

# Create Nginx Load Balancer Security Group
resource "aws_security_group" "nginx_sg" {
  name        = "nginx-sg"
  description = "Security group for Nginx"

  vpc_id = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create Django Servers Security Group
resource "aws_security_group" "django_sg" {
  name        = "django-sg"
  description = "Security group for Django servers"

  vpc_id = var.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.nginx_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create DB Server Security Group
resource "aws_security_group" "db_sg" {
  name        = "db-sg"
  description = "Security group for PostgreSQL database server"

  vpc_id = var.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    self        = true
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create Nginx Load Balancer Instance
resource "aws_instance" "nginx_lb" {
  ami           = "ami-0430580de6244e02e"  # Replace with your desired Nginx AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name

  tags = {
    Name = "nginx-lb"
  }

  network_interface {
    device_index                = 0
    subnet_id                   = var.subnet_id
    security_group_ids          = [aws_security_group.nginx_sg.id]
    associate_public_ip_address = false
  }

  instance_initiated_shutdown_behavior = "terminate"
}

# Create Django App Instances
resource "aws_instance" "django_app_1" {
  ami           = "ami-0430580de6244e02e"  # Replace with your desired Django AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name

  tags = {
    Name = "django-app-1"
  }

  network_interface {
    device_index                = 0
    subnet_id                   = var.subnet_id
    security_group_ids          = [aws_security_group.django_sg.id, aws_security_group.nginx_sg.id]
    associate_public_ip_address = false
  }

  instance_initiated_shutdown_behavior = "terminate"
}

resource "aws_instance" "django_app_2" {
  ami           = "ami-0430580de6244e02e"  # Replace with your desired Django AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name

  tags = {
    Name = "django-app-2"
  }

  network_interface {
    device_index                = 0
    subnet_id                   = var.subnet_id
    security_group_ids          = [aws_security_group.django_sg.id, aws_security_group.nginx_sg.id]
    associate_public_ip_address = false
  }

  instance_initiated_shutdown_behavior = "terminate"
}

# Create PostgreSQL Database Instance
resource "aws_instance" "postgres_db" {
  ami           = "ami-0430580de6244e02e"  # Replace with your desired PostgreSQL AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name

  tags = {
    Name = "postgres-db"
  }

  network_interface {
    device_index                = 0
    subnet_id                   = var.subnet_id
    security_group_ids          = [aws_security_group.db_sg.id]
    associate_public_ip_address = false
  }

  instance_initiated_shutdown_behavior = "terminate"
}
