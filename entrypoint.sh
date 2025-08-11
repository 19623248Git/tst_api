#!/bin/sh

# This script waits for the database to be ready before starting the web server.

# The database host is available as the 'db' service in docker-compose
DB_HOST=db
DB_PORT=5432

echo "Waiting for database to be ready at $DB_HOST:$DB_PORT..."

# Use netcat (nc) to check if the port is open.
# The -z flag makes nc scan for listening daemons without sending any data.
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1 # wait for 1 second before trying again
done

echo "Database is ready."

# Now that the database is ready, execute the main command
# (passed to this script as arguments)
exec "$@"