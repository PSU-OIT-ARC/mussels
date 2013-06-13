# Install

    virtualenv-2.6 --no-site-packages .env
    source .env/bin/activate
    pip install -r requirements.txt

If you run into problems installing psycopg make sure you can execute the
`pg_config` command. If not, you need to add the directory containing pg_config
to your path. You can find the path with `locate pg_config`. On my machine, I
had to do:

    export PATH=/usr/pgsql-9.2/bin:$PATH

## Configure

    cp mussels/example_settings.py mussels/local_settings.py
    vim mussels/local_settings.py # adjust settings

## Generate Image

    mkdir static/img/generated
    python generateimages.py
