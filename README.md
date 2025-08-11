run the docker-compose file:
docker-compose up --build

check database:
docker-compose exec db psql -U tstdb -d users