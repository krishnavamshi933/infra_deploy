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

# Function to update packages and perform system hardening steps
def perform_security_hardening(server):
    conn = connect(server)

    # Update packages
    conn.sudo('apt-get update')
    conn.sudo('apt-get upgrade -y')

    # Secure SSH
    #conn.sudo('sed -i "s/#PermitRootLogin prohibit-password/PermitRootLogin no/" /etc/ssh/sshd_config')
    #conn.sudo('sed -i "s/PasswordAuthentication yes/PasswordAuthentication no/" /etc/ssh/sshd_config')
    #conn.sudo('systemctl restart ssh')

    # Configure firewall (UFW)
    conn.sudo('ufw default deny incoming')
    conn.sudo('ufw default allow outgoing')
    conn.sudo('ufw allow OpenSSH')
    conn.sudo('ufw enable')

    # Configure Fail2ban
    conn.sudo('apt-get install -y fail2ban')
    conn.sudo('systemctl enable fail2ban')
    conn.sudo('systemctl start fail2ban')

# Execute security hardening steps on each server
for server in servers:
    print(f"Performing security hardening on {server['server_ip']}...")
    perform_security_hardening(server)
    print(f"Security hardening completed for {server['server_ip']}")
