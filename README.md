# Install

    virtualenv --no-site-packages -p python3 .env
    source .env/bin/activate
    pip install -r requirements.txt

If you run into problems installing psycopg make sure you can execute the
`pg_config` command. If not, you need to add the directory containing pg_config
to your path. You can find the path with `locate pg_config`. On my machine, I
had to do:

    export PATH=/usr/pgsql-9.3/bin:$PATH

## PostgreSQL

    createdb mussels;
    psql mussels;
    > CREATE EXTENSION postgis;
    > CREATE EXTENSION postgis_topology;

## Generate Image

    mkdir static/img/generated
    python generateimages.py

## Database migrations

    make migrate

## Run the server

Varlet will ask you to fill in settings

    make

## Testing and Coverage

Run unit tests with

    make test

Or, to use coverage

    make coverage

and visit 0.0.0.0:8000/htmlcov/index.html
