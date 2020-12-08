# loction_mapping_flask

### Use Python 3.6.9

### Clone  Repository
git clone https://github.com/ajinkyagadewar/location_mapping.git

## Create Virtual environment

`virtualenv --python=python3 env`

### Activate envirment 

`source env/bin/activate`

`cd loction_mapping_flask/`

### Install required libraries 

 `pip install -r requirements.txt`

### Install Postgress (Ubuntu). Follow similar process on other operating systems
https://tecadmin.net/install-postgresql-server-on-ubuntu/
Create a database as “world_data“

 `create database world_data;`

### Pass all credentials in app.py file. This can be changed to environment secrets or vault secrets in future

### Dump SQL from here 

### Use the following command for restore database
 `psql -Upostgres world_data <world.sql`


### Then Do DB activities in active environment terminal

  `flask db migrate`
  `flask db upgrade`


### Run the following command for export
 `export FLASK_APP=app.py`

### For Run server
 `flask run`

### Server will Run on 
http://localhost:5000
