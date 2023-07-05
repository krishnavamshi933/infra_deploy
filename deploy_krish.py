import datetime
import shutil
from fabric import Connection
import os

# Server configuration
server = '18.218.189.203'
pem_file_path = 'krish-test.pem'

# Repository configuration
repo_url = 'https://github.com/krishnavamshi933/myprojectdir.git'
repo_destination = '/home/ubuntu/myprojectdir'

# Connect to the server using SSH
key = os.path.expanduser(pem_file_path)
conn = Connection(host=server, user='ubuntu', connect_kwargs={'key_filename': key})

def update_repository(connection, repo_url, repo_destination):
    if connection.run(f'test -d {repo_destination}', warn=True).failed:
        # If the repository doesn't exist, clone it
        connection.run(f'git clone {repo_url} {repo_destination}')
    else:
        # If the repository exists, take a backup and update it with the latest code
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_folder = f'{repo_destination}_backup_{timestamp}'
        connection.run(f'mv {repo_destination} {backup_folder}')
        with connection.cd(os.path.dirname(repo_destination)):
            connection.run(f'git clone {repo_url} {repo_destination}')
            # connection.run(f'rm -rf {backup_folder}')

def update_environment(connection):
    # Update the environment by installing required packages
    connection.sudo('apt-get update')
    connection.sudo('apt-get install -y python3-venv python3-dev libpq-dev postgresql postgresql-contrib nginx curl')

def install_dependencies(connection, repo_destination):
    with connection.cd(repo_destination):
        connection.run('python3 -m venv myprojectenv')
        connection.run('source myprojectenv/bin/activate && pip install -r requirements.txt')

def configure_nginx(connection, project_path):
    nginx_config = f'''
server {{
    listen 80;
    server_name {server};
    access_log /var/log/nginx/access.log;

    location / {{
        include proxy_params;
        proxy_pass http://unix:{project_path}/myproject.sock;
    }}
}}
'''
    connection.sudo(f'echo "{nginx_config}" | sudo tee /etc/nginx/sites-available/myproject')
    connection.sudo('sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled')
    connection.sudo('sudo systemctl restart nginx')

def configure_gunicorn(connection, project_path):
    virtualenv_path = os.path.join(project_path, 'myprojectenv')
    gunicorn_service = f'''
[Unit]
Description=Gunicorn service for myproject
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory={project_path}
ExecStart={virtualenv_path}/bin/gunicorn --access-logfile - --workers 3 --bind unix:{project_path}/myproject.sock myproject.wsgi:application

[Install]
WantedBy=multi-user.target
'''
    connection.sudo(f'echo "{gunicorn_service}" | sudo tee /etc/systemd/system/gunicorn.service')
    connection.sudo('sudo systemctl daemon-reload')
    connection.sudo('sudo systemctl enable gunicorn')
    connection.sudo('sudo systemctl start gunicorn')

def main():
    print(f'Connecting to {server}...')
    conn.open()

    try:
        print('Updating the environment...')
        update_environment(conn)

        print('Updating the repository...')
        update_repository(conn, repo_url, repo_destination)

        print('Installing dependencies...')
        install_dependencies(conn, repo_destination)

        print('Configuring Gunicorn...')
        configure_gunicorn(conn, repo_destination)

        print('Configuring Nginx...')
        configure_nginx(conn, repo_destination)

    finally:
        conn.close()

if __name__ == '__main__':
    main()
