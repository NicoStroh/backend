# gits_backend
Local dev environment setup for the GITS project. Should not be used in production environments.

## Cloning

This repository uses git submodules to be able to retrieve the repositories of all services into this repository when cloning. To do this, do the following:

1. As with any repo, clone it using `git clone https://github.com/IT-Rex-Platform/gits_backend.git`
2. Move into the repository (`cd gits_backend`)
3. Initialize the submodules using `git submodule init`
4. Pull the submodules using `git submodule update`

## Deployment

The local deployment of the backend is done in a few simple steps:
1. Start docker (desktop)
2. Create a network for the dapr sidecars to communicate: `docker network create dapr-network`
3. Execute the .bat or .sh file found under ./gits_backend/compose.bat using `compose.bat up --build` (re-builds the containers) or `compose.bat up` (starts the containers without re-building if they already exist). 

# Debugging Services

To facilitate easy debugging of services, the docker containers are set up to expose all important ports to the host machine. This can easily be seen in Docker Desktop. Port mappings can also be found [on the wiki](https://gits-enpro.readthedocs.io/en/latest/dev-manuals/architecture/Ports.html).

This makes it possible for you to start a service in your favorite IDE (where you can set breakpoints etc.) and for that service to hook into the rest of the system.

## Some Hints/Limitations

* Firstly, start the whole backend as described above. Then you can stop the docker container of the service you want to debug (the database container needs to continue running!). You can then start the service you wish to debug on your host machine
* Make sure when you execute the service you wish to debug that it is being run in the "dev" profile. In IntelliJ the profile can be set in the "Run Configurations". Alternatively the profile can be set in the application.properties file
* Dapr PubSub Events do not work when debugging in this way
