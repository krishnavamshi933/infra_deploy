from fabric import Connection

# Define the deployment script function
def deploy_db():
    # Connect to the remote server using SSH key authentication
    conn = Connection(
        host='your-server-ip',  # Replace with your server IP
        user='ubuntu',  # Replace with the SSH username
        connect_kwargs={'key_filename': '/path/to/your.pem'}  # Replace with the path to your PEM file
    )

    try:
        # Update package lists
        conn.sudo('apt-get update')

        # Install PostgreSQL and related packages
        conn.sudo('apt-get install -y postgresql postgresql-contrib')
        conn.sudo('apt-get install -y libpq-dev python3-dev')

        # Install psycopg2 Python package
        conn.run('pip install psycopg2')

        # Execute PostgreSQL commands
        conn.sudo('sudo -u postgres psql -c "CREATE DATABASE mydb;"')
        conn.sudo('sudo -u postgres psql -c "CREATE USER myuser WITH ENCRYPTED PASSWORD \'mypass\';"')
        conn.sudo('sudo -u postgres psql -c "ALTER ROLE myuser SET client_encoding TO \'utf8\';"')
        conn.sudo('sudo -u postgres psql -c "ALTER ROLE myuser SET default_transaction_isolation TO \'read committed\';"')
        conn.sudo('sudo -u postgres psql -c "ALTER ROLE myuser SET timezone TO \'UTC\';"')
        conn.sudo('sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mydb TO myuser;"')
        conn.sudo('sudo -u postgres psql -c "\q"')

        # Update PostgreSQL configuration
        conn.sudo('sed -i "s/#listen_addresses = \'localhost\'/listen_addresses = \'*\'/g" /etc/postgresql/13/main/postgresql.conf')
        conn.sudo('echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/13/main/pg_hba.conf')

        # Restart PostgreSQL service
        conn.sudo('systemctl restart postgresql')

        print("PostgreSQL deployment completed successfully!")
    except Exception as e:
        print("An error occurred during PostgreSQL deployment:", str(e))
    finally:
        # Close the connection
        conn.close()

# Execute the deployment script
deploy_db()
