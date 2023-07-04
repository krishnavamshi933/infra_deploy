from fabric import Connection

# List of server SSH details
servers = [
    {
        'server_ip': 'server1_ip',
        'username': 'server1_username',
        'pem_file_path': '/path/to/server1.pem'
    },
    {
        'server_ip': 'server2_ip',
        'username': 'server2_username',
        'pem_file_path': '/path/to/server2.pem'
    },
    # Add more server details as needed
]

# Function to establish a connection to a server
def connect(server):
    return Connection(host=server['server_ip'], user=server['username'], connect_kwargs={'key_filename': server['pem_file_path']})

# Function to update packages and install essential security tools
def update_packages_and_install_tools(server):
    conn = connect(server)
    conn.sudo('apt-get update')
    conn.sudo('apt-get upgrade -y')
    conn.sudo('apt-get install -y ufw fail2ban')

# Function to configure firewall (UFW)
def configure_firewall(server):
    conn = connect(server)
    conn.sudo('ufw default deny incoming')
    conn.sudo('ufw default allow outgoing')
    conn.sudo('ufw allow OpenSSH')
    conn.sudo('ufw enable')

# Function to configure Fail2ban
def configure_fail2ban(server):
    conn = connect(server)
    conn.sudo('systemctl enable fail2ban')
    conn.sudo('systemctl start fail2ban')

# Function to perform security hardening steps on a server
def perform_security_hardening(server):
    update_packages_and_install_tools(server)
    configure_firewall(server)
    configure_fail2ban(server)

# Execute security hardening steps on each server
for server in servers:
    print(f"Performing security hardening on {server['server_ip']}...")
    perform_security_hardening(server)
    print(f"Security hardening completed for {server['server_ip']}")
