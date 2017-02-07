# Usage

1. Require `docker-machine` and `docker-compose` to be already installed on your computer
2. `$ docker-machine create -d virtualbox dev` to create a docker virtual machine called "dev"
3. `$ eval $(docker-machine env dev)` to point Docker client to this virtual machine
4. Navigate to the project root
5. `$ docker-compose build`
6. `$ docker-compose up -d`
7. Get the IP address of the Docker virtual machine: `$ docker-machine ip dev`
8. Go to that IP in browser

## Migrate Database

Everytime after the models are modified, a manual migration of the database is required in order to apply the changes to the database.

1. Display all docker running containers : `$ docker ps`
2. Get the **CONTAINER ID** of the `mindrateserverdocker_web` container, e.g. `7fac64c6cf8a`
3. Log into the running container: `$ docker exec -t -i 7fac64c6cf8a bash`
4. `$ cd /usr/src/app`
5. `$ python manage.py migrate`