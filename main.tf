variable "vpc_id" {
  default = "vpc-02bd2eed3cfb565df"  # Replace with your VPC ID
}

variable "subnet_id" {
  default = "subnet-05022afbdb17f196c"  # Replace with your subnet ID
}

variable "key_pair_name" {
  default = "uma-test"  # Replace with your key pair name
}

variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks allowed for SSH access"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Update with your desired CIDR blocks
}

# Configure AWS provider
provider "aws" {
  region = "us-east-2"  # Replace with your desired region
}

# Create Nginx Load Balancer Security Group
resource "aws_security_group" "nginx_sg" {
  name        = "nginx-sg"
  description = "Security group for Nginx"

  vpc_id = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.django_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create Django Servers Security Group
resource "aws_security_group" "django_sg" {
  name        = "django-sg"
  description = "Security group for Django servers"

  vpc_id = var.vpc_id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.nginx_sg.id]
  }

  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    cidr_blocks     = var.allowed_ssh_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create Nginx Load Balancer
resource "aws_instance" "nginx_lb" {
  ami           = "ami-0123456789"  # Replace with your desired Nginx AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name
  associate_public_ip_address = true  # Enable public IP for the Nginx server

  tags = {
    Name = "nginx-lb"
  }

  network_interface {
    device_index = 0
    subnet_id    = var.subnet_id
    security_groups = [aws_security_group.nginx_sg.id]
  }
}

# Create Django Application Servers
resource "aws_instance" "django_app_1" {
  ami           = "ami-0123456789"  # Replace with your desired Django AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name
  associate_public_ip_address = false  # Disable public IP for the Django app servers

  tags = {
    Name = "django-app-1"
  }

  network_interface {
    device_index    = 0
    subnet_id       = var.subnet_id
    security_groups = [aws_security_group.django_sg.id, aws_security_group.nginx_sg.id]
  }
}

resource "aws_instance" "django_app_2" {
  ami           = "ami-0123456789"  # Replace with your desired Django AMI ID
  instance_type = "t2.micro"  # Replace with your desired instance type
  key_name      = var.key_pair_name
  associate_public_ip_address = false  # Disable public IP for the Django app servers

  tags = {
    Name = "django-app-2"
  }

  network_interface {
    device_index    = 0
    subnet_id       = var.subnet_id
    security_groups = [aws_security_group.django_sg.id, aws_security_group.nginx_sg.id]
  }
}

# Output
output "nginx_lb_public_ip" {
  value = aws_instance.nginx_lb.public_ip
}

output "django_app_1_private_ip" {
  value = aws_instance.django_app_1.private_ip
}

output "django_app_2_private_ip" {
  value = aws_instance.django_app_2.private_ip
}
