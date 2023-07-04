from fabric import Connection
from fabric import Config

# Nginx server details
nginx_server = {
    'ip': 'nginx_server_ip',
    'username': 'nginx_server_username',
    'pem_file_path': '/path/to/nginx_server.pem'
}

# List of private IP addresses of Django application servers
django_ips = [
    '10.0.0.2',
    '10.0.0.3'
]

# SSH username and PEM file path for Django servers
username = 'django_server_username'
pem_file_path = '/path/to/django_server.pem'

# Nginx configuration template
nginx_config_template = """
events {{
    worker_connections 1024;
}}

http {{
    upstream backend {{
        server {django_server_1};
        server {django_server_2};
    }}

    server {{
        listen 80;
        server_name localhost;

        location / {{
            proxy_pass http://backend;
        }}
    }}
}}
"""

# Function to establish a connection to a server
def connect(host, username, pem_file_path):
    config = Config(overrides={'sudo': {'password': 'your_sudo_password'}})  # Replace with your sudo password
    return Connection(host=host, user=username, connect_kwargs={'key_filename': pem_file_path}, config=config)

# Function to generate Nginx server blocks
def generate_nginx_config():
    nginx_config = nginx_config_template.format(
        django_server_1=django_ips[0],
        django_server_2=django_ips[1]
    )
    return nginx_config

# Function to install and configure Nginx
def install_and_configure_nginx():
    conn = connect(nginx_server['ip'], nginx_server['username'], nginx_server['pem_file_path'])
    conn.sudo('apt-get update')
    conn.sudo('apt-get install -y nginx')
    conn.put('nginx.conf', '/tmp/nginx.conf')
    conn.sudo('mv /tmp/nginx.conf /etc/nginx/nginx.conf')
    conn.sudo('systemctl restart nginx')

# Function to run Nginx as a load balancer
def run_nginx_load_balancer():
    nginx_config = generate_nginx_config()
    conn = connect(nginx_server['ip'], nginx_server['username'], nginx_server['pem_file_path'])
    conn.put('nginx.conf', '/tmp/nginx.conf')
    conn.sudo(f'echo "{nginx_config}" | sudo tee /etc/nginx/nginx.conf')
    conn.sudo('systemctl restart nginx')

# Execute the script
install_and_configure_nginx()
run_nginx_load_balancer()
