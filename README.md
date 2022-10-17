# Cloud-Computing-MemCache (UofT ECE 1779 Project)

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

You can install via all packages listed before using pip3 command by first activating your venv 

# Installation

Make sure port 5000 is opened before initializing the server.

Use `git clone https://github.com/xinyu910/Cloud-Computing-MemCache.git`

Download the software package, run `start.sh` in the root dictionary to start the system.

Go to `localhost:5000` to access the application.

# Contributing

Thank you for investing your time in contributing to our project!

You are welcome to:


* Post Issues

* Solve an issue

* Make Changes

* If you have any issues you would like to discuss, see the readme file-contact for contact information.

see [Contributing](https://github.com/xinyu910/Cloud-Computing-MemCache/blob/main/CONTRIBUTING.md) for details


# License
see file [MIT License](https://github.com/xinyu910/Cloud-Computing-MemCache/commit/7e5a9d3732e5ef3b4975cdb0eea4be54c50379d2)

for information about `Copyright (c) 2022 ECE1779f2022G11 `


# Citation

For citation information， please refer to [Citation](https://github.com/xinyu910/Cloud-Computing-MemCache/blob/main/CITATION.cff)


# Contact

Yuxin Liu xinyuxy.liu@mail.utoronto.ca

Ziqi Zhou zq.zhou@mail.utoronto.ca

Yuming Li yming.li@mail.utoronto.ca
