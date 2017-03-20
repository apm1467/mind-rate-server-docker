python3 web/manage.py makemigrations survey
python3 web/manage.py migrate
sudo docker-compose down
sudo docker-compose build --no-cache
sudo docker-compose up -d
