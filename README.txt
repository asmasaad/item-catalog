# Item Catalog


This project is for Udacity Full Stack Nanodegree to
 develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system . Registered users will have the ability to post, edit and delete their own items.
 in this project we learn how to develop a RESTful web application using the Python framework Flask along with implementing third-party OAuth authentication


## Installing
*  [Vagrant](https://www.vagrantup.com/downloads.html)
* [Virtual Box](https://www.virtualbox.org/wiki/Downloads)
* [Udacity FSND virtual machine](https://github.com/udacity/fullstack-nanodegree-vm)
* python 2


## How to run the project
* cd fullstack-nanodegree-vm
* cd vagrant
* Launch the Vagrant VM   **vagrant up**
* login to the VM  **vagrant ssh**
* cd /vagrant
* cd catalog
* run the application   **python project.py**
* home page for website  http://localhost:5000/universty/
* click on login button to add delete and update your items

## json
* this link show all colleges under universty specified in **id** part http://localhost:5000/universty/<int:id>/college/json
* this link show all universty  http://localhost:5000/universty/json
* this link show details of specific college http://localhost:5000/universty/colleges/items/<int:college_id>/json

