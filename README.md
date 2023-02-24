# Cloud-Image-Gallery

# About Project

This project is a storage web application with an in-memory key-value memory cache. Python and the Flask framework are used to implement this project. This project will also be deployed and run on Amazon EC2. The project consists of two flask instances, one is called FrontEnd which displays web pages and interacts with users, and the other one is an internal memcache integrated with a scheduler for periodic reporting statistics tasks. 

Key components include:

* A web browser that initiates requests
* A web front end that manages requests and operations
* A local file system where all data is stored
* A mem-cache that provides faster access
* A relational database


# Prerequisites

Main packages required:

* python 3.8
* flask 2.2.2
* mysql-connector 2.2.9
* requests 3.7.0
* APScheduler 3.8.0
* Werkzeug 2.2.2

Execute `start.sh` will install the required packages for you.

# Installation

Make sure port 5000 is opened before initializing the server.

Use `git clone https://github.com/xinyu910/Cloud--Image-Gallery.git`

Download the software package, run `start.sh` in the root dictionary to start the system.

Go to `localhost:5000` to access the application.

# Screenshots of the usage scenarios
* Home Page:
![HomePage](https://user-images.githubusercontent.com/52727328/221234464-678fe64b-4f63-4fed-bab6-17d2769604a8.jpg)
* Browse Image Form Page:
![BrowsePage](https://user-images.githubusercontent.com/52727328/221234460-191791c6-8cbe-4695-843e-45822458fe89.jpg)
* Configuration Page:
![ConfigurationPage](https://user-images.githubusercontent.com/52727328/221234462-f51d42b0-19fe-4748-ac27-3b809054950c.jpg)
* Show Keys Page:
![KeysPage](https://user-images.githubusercontent.com/52727328/221234469-c650ab08-38ad-4461-aa02-9bdaddbc828d.jpg)
* Show Image Page:
![ShowPage](https://user-images.githubusercontent.com/52727328/221234471-4ba3d88a-c806-4a1f-9473-474b0f979696.jpg)
* Statistics Page:
![StatisticsPage](https://user-images.githubusercontent.com/52727328/221234472-350ae7b8-72bd-415e-a67b-450856fabcc2.jpg)
* Upload Form Page
![UploadPage](https://user-images.githubusercontent.com/52727328/221234473-9b797f97-fa01-43cc-88a8-48808dff496f.jpg)

