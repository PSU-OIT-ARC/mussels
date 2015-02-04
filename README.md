# Mussels Map

This project renders a Google map with icons where mussels have been detected. Each of these mussel observations has information associated with it like a species, substrate, waterbody, and provider.

Users of the map and search and filter for specific things.

There is also an "Add Data" page, that allows people to enter observations.

The (very barebones) admin interface allows for the management of observations, species, agencies, substrates, waterbodies, and users.

This application uses a postgis enabled database. In production, it uses the Atlas of Oregon Lakes (AOL) database, since the AOL application uses some of its data.

The map icons are generated with the generateimages.py script. There is a set of circle icons for the specie, and a set of flag icons for the substrates the specie was detected on. The icon generator makes a zillion combinations of species and one-or-more substrates combined images.

There are a couple fixtures for the species and substrates.

CAS is used for admin authentication.

There is an AdminUser model, and a User model, which was a dumb idea (sorry). AdminUsers can login as admins. User objects just store information about people who reported their observations.

# Install

This will attempt to create a postgis enabled database on localhost, and load
dummy data, etc. You will be prompted for settings if anything needs to be
configured.

    make init

# Run the server

    make
