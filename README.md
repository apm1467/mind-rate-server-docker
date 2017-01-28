# Usage

1. Require `docker-machine` and `docker-compose` to be already installed on your computer
2. `$ docker-machine create -d virtualbox dev` to create a docker virtual machine called "dev"
3. `$ eval $(docker-machine env dev)` to point Docker client to this virtual machine
4. Navigate to the project root
5. `$ docker-compose build`
6. `$ docker-compose up -d`
7. Get the IP address of the Docker virtual machine: `$ docker-machine ip dev`
8. Go to that IP in browser