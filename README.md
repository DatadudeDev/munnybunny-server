# munnybunny-server

The simple backend server for MunnyBunny, a business expense tracker. 

![alt text](https://datadude.dev/wp-content/uploads/2023/10/00002-2207509569.png)



Features: 

@ Automatically assigns unique expense Serial Numbers for each addition  
@ Contains a SQLITE databse which stores expenses, including photo attachements of receipts.  
@ Automatically calcualtes the sum of expenses to reimburse  
@ Uses a simple API to execute commands from a Web GUI (Munnybunny-webServer)  
@ Contains functionality to add, remove and edit expenses.  
@ Python and Javascript 


Docker Installation: 

Docker Compose is the preferred method of installation.  
My docker repo is private, but you can close the git repo and compile the image  
locally with the following commands: 

```
git clone https://github.com/DatadudeDev/munnybunny-webserver.git
cd ./munnybunny-webserver
docker build -t munnybunny-webserver:latest .
```

When you've built the images for both the server and the webserver, you can use  
the below docker compose template to spin up the containers in a stack (important  
for networking) 

Once done, navigate to your LAN IP:PORT (80 or whatever you picked) to access the web GUI.

Enjoy!

```
version: '2'
services:
  budget:
    image: munnybunny-server:latest
    restart: unless-stopped
    volumes:
      - server:/app/
    ports:
      - 81:5050 # you can change port 81 to whatever you want
    networks:
      - my_network

  webserver:
    image: munnybunny-webserver:latest
    restart: unless-stopped
    volumes:
      - webserver:/app/
    ports:
      - 80:8050  # you can change port 80 to whatever you want
    networks:
      - my_network

networks:
  my_network:
    driver: bridge

volumes:
  server:
  webserver:

```

Navigate to your LAN IP:PORT (80 or whatever you picked) to access the web GUI. 

Enjoy! 
