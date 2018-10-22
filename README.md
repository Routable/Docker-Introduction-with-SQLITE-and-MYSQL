# Docker-Introduction-with-SQLITE-and-MYSQL
This application was used in combination with dockerhub as a way to research using Docker containers, and connecting several Docker swarm nodes to a single MYSQL database instance. This project can be used as a template to quickly get a Flask docker container with MySQL or SQLITE connectivity up and running.

![Alt text](https://media.discordapp.net/attachments/492769970321883148/503003573429338112/unknown.png)


# Deploying your Application to a Docker Swarm using Digital Ocean

#### Note: This tutorial assumes that you have already created a Digital Ocean server using the one-click install option for the Docker image. If you have not completed this step, please follow the guide available at: 
https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-docker-application


1) wget https://github.com/docker/machine/releases/download/v0.15.0/docker-machine-$(uname -s)-$(uname -m)
2) mv docker-machine-Linux-x86_64 docker-machine
3) chmod +x docker-machine 
4) sudo mv docker-machine /usr/local/bin
5) docker-machine create --driver digitalocean --digitalocean-access-token YOURTOKENAPIKEY machinename
6) (Repeat to create as many nodes as you want)
7) docker swarm init --advertise-addr ip_address_of_host
8) (copy the string outputted from step 7)
9) Docker-machine ssh slave1  (Paste the string from step 7 on each node. Repeat as necessary.)

10) Run the following commands on every node and host:

  ufw allow 22/tcp
  ufw allow 2376/tcp
  ufw allow 2377/tcp
  ufw allow 7946/tcp
  ufw allow 7946/udp
  ufw allow 4789/udp
  ufw allow 5000/tcp
  ufw allow 5000/udp
  
Note: Run the following commands individually, as copy pasting them tends to break them when inputted into the terminal.
 
  ufw enable
  ufw reload
  systemctl restart docker

11) Navigate back to the Swarm Master/Host machine, and execute the following command:
  docker pull stevenabucholtz/middleware

Note: Pull the image from dockerhub that you wish to run. In this example, I have already created my own docker image that we will be running. 

12) On the Swarm Master/host machine, run the following command to initialize and deploy your application to the swarm:
	docker service create -p 5000:5000 -replicas 3 stevenabucholtz/middleware 

# Connect your Docker node to a MySQL database on Ubuntu 18.0.4

1) Install MYSQL on your server.

  sudo apt update
  sudo apt install mysql-server
  sudo mysql_secure_installation

2) Log into your MYSQL server from the terminal.

  mysql -p YOURPASSWORD

3) Grant privileges to your existing root account, or create a new MYSQL user and provide permissions to it with the following command:

GRANT ALL PRIVILEGES ON *.* TO 'middleware'@'%'
IDENTIFIED BY 'yourpassword';

4) Create a database, and set it to be your primarily used database.

CREATE DATABASE middleware;
use middleware;

5) Create the tables you require for your project. Feel free to do an insert after to make sure it's working. 

CREATE TABLE examplecount(id int);
INSERT INTO examplecount(id) VALUES (1);

6) Now that you have MySQL setup, you need to do a few specific server changed to allow outside connections to hit your database:

  nano /etc/mysql/mysql.conf.d/mysqld.cnf
  
  In the file, make sure the line "set bind-address to" looks like "set bind-address to 0.0.0.0" instead of "set bind-address to 127.0.0.1".

 7) Restart the MYSQL service.
  systemctl restart mysql.service

  8) Verify that your connection settings are correct in your application. In my example, I am using the Flask-MySql Python extension to connect to my database. Inside my app.py, I have the following settings that are used for my connection:

  app.config['MYSQL_DATABASE_USER'] = 'root'
  app.config['MYSQL-DATABASE_PASSWORD'] = 'password'
  app.config['MYSQL_DATABASE_DB'] = 'middleware'
  app.config['MYSQL_DATABASE_HOST'] = 'ip of mysql server'

9)  Install the Flask-MySQL dependency on the server your application will be making the connection from. Alternatively, add the flask-mysqldb to your Docker requirements file.  

pip install flask-mysqldb

10) If you did everything correctly, you should have access to your database from your application. Most problems are typically due to incorrect privilege levels being assigned to the MySQL user, or firewall settings preventing the connection. Depending on your system settings, you made need to add the default MySQL port (3306) to your firewall whitelist. It is recommended to only allow connections from machines you trust, as MySQL is a commonly attacked service.

sudo ufw allow from your.ip.address/24 to any port 3306
(potentially optional) ufw enable
ufw reload

Note: If you are unsure of what dependencies you require for your docker setup files, you can use the command 
'pip freeze > requirements.txt' to list all active dependencies on your system. You can then add these dependencies to your docker file.








