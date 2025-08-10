current run command (without docker compose):

docker build -t tst-app .

docker run -d -p 8000:80 --name prod-app tst-app