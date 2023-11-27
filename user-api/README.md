# user-api

User Api is a microservice for maintaining users, where you can register, list, update, search for and delete a user.

The application was built in a [microservice](https://martinfowler.com/articles/microservices.html) architecture, in which each container makes up a part of the whole:

* `user_api`: API that exposes and allows users to be maintained.
* `db_user`: PostgreSQL database responsible for maintaining users;
* `pgadmin_userapi`: Gui for querying and manipulating the database.

The API was built with [FastApi](https://fastapi.tiangolo.com/), which has excellent type validation, both for input and output of the API, using [Pydantic](https://pydantic-docs.helpmanual.io/). In addition, `FastApi` automatically documents the API using [OpenAPI](https://github.com/OAI/OpenAPI-Specification).

The project was documented using [Sphinx](https://www.sphinx-doc.org/en/master/), the documentation can be accessed at [Docs](http://localhost:4090/)

## Prerequisites

For the project to work, you need to generate an asymmetric cryptographic key. To do this, you can use the [generate_key](user-api/user_api/utlis/cryptography.py) function and export the key as an environment variable with the name `SECRET_KEY in the terminal that will run it

You need to configure [docker](https://docs.docker.com/) and [docker-compose](https://docs.docker.com/compose/) to consume the project.

The environment variables used by the containers are configured in the file [docker-compose.yml](docker-compose.yml), and are exactly the same as those configured in the file [config.py](user-api/user_api/config.py) containing the database connection variables and the `SECRET_KEY` to encrypt the data before writing it to the database.

### Installation and Execution

Clone the project repository, and in the `user-api` folder, follow the instructions below.

The project has a [Makefile](https://en.wikipedia.org/wiki/Make_(software)#Makefile) to automate the execution of the project. To run the project, use the following command:

```bash
make run
```

With this command you can _build_ the images and run the project.

Once the application is live, simply go to [ReDoc](http://localhost:4090/v1/docs) to find out how to use each of the *endpoints* and to use the *endpoints* go to [Swagger](http://localhost:4090/v1/swagger).

## Running tests

Application tests validate the application's business logic, checking that functions and modules behave as expected.

Ideally, tests should be run in a _dockerized_ way, so the API and database _containers_ need to be running, which can be done by following the instructions in [Installation and Execution]().

With the API container named `user-api`, run:

```bash
docker container exec -it user-api pytest -v
```

### Code style

This code follows the PEP8 standard and can be tested with the [PyLama](https://github.com/klen/pylama) library as in the following example

```bash
make lint
```

### Autoformatter

The project has [Black](https://github.com/psf/black) which is an `autoformatter`, formatting the code if there is any piece of code that does not follow PEP8. To run it, just run the following command in the terminal:

```bash
make black
```

## Deploy

Once the application has been _dockerized_ and tested, you can _deploy_ it to a _container_ orchestrator such as [Kubernetes](https://kubernetes.io/pt/), or even to the native Docker [Swarm] orchestrator(https://docs.docker.com/engine/swarm/).

## Built with

* [black](https://github.com/psf/black)
* [loguru](https://github.com/Delgan/loguru)
* [PostgreSQL](https://www.postgresql.org/)
* [pydantic](https://pydantic-docs.helpmanual.io)
* [fastapi](https://fastapi.tiangolo.com)
* [uvicorn](https://www.uvicorn.org)
* [gunicorn](https://gunicorn.org)
* [requests](https://requests.readthedocs.io/en/master/)
* [sphinx](https://www.sphinx-doc.org/en/master/)

## Versioning

Versioning follows the standard of [Semantic Versioning](http://semver.org/).

## License

All rights are reserved to the author Kevin de Santana Araujo.

## Other information

* If you have any questions about the project, or would like to contribute suggestions or criticism, please open an [issue]() or contact the developer at kevin_santana.araujo@hotmail.com.
