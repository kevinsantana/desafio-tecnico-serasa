# order-api

Order-api is a microservice for maintaining orders, where it is possible to register, list, update, search and delete an order.

The application was built on a [microservice](https://martinfowler.com/articles/microservices.html) architecture, in which each container makes up part of the whole, they are:

* `order_api`: It is the API that exposes and allows the manipulation of orders.
* `db_orders`: It is the Elasticsearch database responsible for maintaining orders;
* `redis`: This is the application cache.

The API was built with [FastApi](https://fastapi.tiangolo.com/), which has excellent type validation, both input and output from the API, using [Pydantic](https://pydantic-docs .helpmanual.io/). Furthermore `FastApi` automatically documents the API using [OpenAPI](https://github.com/OAI/OpenAPI-Specification).

The project was documented using [Sphinx](https://www.sphinx-doc.org/en/master/), the documentation can be accessed at [Docs](http://localhost:3090/)

## Prerequisites

You need to configure [docker](https://docs.docker.com/) and [docker-compose](https://docs.docker.com/compose/) to consume the project.

The environment variables used by containers are configured in the [docker-compose.yml](docker-compose.yml) file, and are exactly the same as those configured in the [config.py](order-api/order_api/config.py) file. containing the connection variables with the database and `redis`.

### Installation and Execution

Clone the project repository, and in the `order-api` folder, follow the instructions below.

The project has a [Makefile](https://en.wikipedia.org/wiki/Make_(software)#Makefile) to automate project execution. To run the project use the following command:

```bash
make run
```

Using this command it is possible to _build_ the images and run the project.

With the application live, simply access [ReDoc](http://localhost:3090/v1/docs) to learn how to use each of the *endpoints* and to use the *endpoints* access [Swagger](http: //localhost:3090/v1/swagger).
## Running tests

Application tests validate the application's business logic, checking whether the functions and modules behave as expected.

Ideally, the tests should be executed in a _dockerized_ way, to do so, the API and database _containers_ must be running, which can be done by following the instructions in [Installation and Execution]().

With the API container named `order-api`, run:

```bash
docker container exec -it order-api pytest -v
```

### Code style

This code follows the PEP8 standard and can be tested with the [PyLama](https://github.com/klen/pylama) library as in the following example

```bash
make lint
```

### Autoformatter

The project has [Black](https://github.com/psf/black) which is an `autoformatter`, formatting the code if there is any piece of code that does not follow PEP8. To run it, just run the following command in the terminal:

```bash
makeup black
```

## Deploy

With the application _dockerized_ and tested, it is possible to _deploy_ in a _container orchestrator_ such as [Kubernetes](https://kubernetes.io/pt/), or even with the native Docker orchestrator [Swarm](https ://docs.docker.com/engine/swarm/).

## Built With

* [black](https://github.com/psf/black)
* [loguru](https://github.com/Delgan/loguru)
* [Elasticsearch](https://www.elastic.co/elasticsearch/)
* [pydantic](https://pydantic-docs.helpmanual.io)
* [fastapi](https://fastapi.tiangolo.com)
* [uvicorn](https://www.uvicorn.org)
* [gunicorn](https://gunicorn.org)
* [requests](https://requests.readthedocs.io/en/master/)
* [sphinx](https://www.sphinx-doc.org/en/master/)

## Versioning

Versioning follows the [Semantic Versioning](http://semver.org/) standard.

## License

All rights are reserved to the author Kevin de Santana Araujo.

## Other information

* If you have any questions regarding the project, or want to contribute with suggestions or criticisms, open an [issue]() or contact the developer via email at kevin_santana.araujo@hotmail.com
