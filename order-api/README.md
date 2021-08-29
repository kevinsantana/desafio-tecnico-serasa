# order-api

Order-api é um microsserviço para manter pedidos, onde é possível cadastrar, listar, atualizar, buscar e deletar um pedido.

A aplicação foi construída em uma arquitetura de [microsserviço](https://martinfowler.com/articles/microservices.html), em que cada container compõe um parte do todo, são eles:

* `order_api`: É a API que expõe e permite a manipulação dos pedidos.
* `db_orders`: É o banco de dados Elasticsearch responsável por manter os pedidos;
* `redis`: É o cache da aplicação.

A API foi construída com [FastApi](https://fastapi.tiangolo.com/), que possuí uma excelente validação de tipos, tanto de entrada como de saída da API, usando [Pydantic](https://pydantic-docs.helpmanual.io/). Além disso `FastApi` documenta automaticamente a API utlizando [OpenAPI](https://github.com/OAI/OpenAPI-Specification).

O projeto foi documentado utilizando [Sphinx](https://www.sphinx-doc.org/en/master/), a documentação pode ser acessada em [Docs](http://localhost:8000/)

## Pré-requisitos

É preciso configurar o [docker](https://docs.docker.com/) e o [docker-compose](https://docs.docker.com/compose/) para consumir o projeto.

As variáveis de ambiente utilizadas pelos containers estão configuradas no arquivo [docker-compose.yml](docker-compose.yml), e são exatamente as mesmas configuradas no arquivo [config.py](order-api/order_api/config.py) contendo as variáveis de conexão com o banco de dados e com o `redis`.

### Instalação e Execução

Clone o repositório do projeto, e na pasta `order-api`, siga as instruções abaixo.

O projeto conta com um [Makefile](https://en.wikipedia.org/wiki/Make_(software)#Makefile) para automatizar a execução do projeto. Para executar o projeto utilize o seguinte comando:

```bash
make run
```

Através deste comando é possível _buildar_ as imagens e executar o projeto.

Com a aplicação no ar, basta acessar o [ReDoc](http://localhost:8000/v1/docs) para saber como utilizar cada um dos *endpoints* e para utilizar os *endpoints* acesse o [Swagger](http://localhost:8000/v1/swagger).

## Executando testes

Os testes da aplicação realizam a validação da lógica negocial da aplicação, verificando se as funções e módulos se comportam conforme esperado.

O ideal é que os testes sejam executados de forma _dockerizada_, para tanto,  é preciso que os _containers_ da API e do banco de dados estejam em execução, o que pode ser feito seguindo as instruções em [Instalação e Execução]().

Com o container da API nomeado como `order-api`, execute:

```bash
docker container exec -it order-api pytest -v
```

### Estilo de código

Esse código segue o padrão PEP8 e pode ser testado com a biblioteca [PyLama](https://github.com/klen/pylama) como no exemplo a seguir

```bash
make lint
```

### Autoformatter

O projeto conta com o [Black](https://github.com/psf/black) que é um `autoformatter`, formatando o código caso exista algum trecho de código que não siga a PEP8. Para executá-lo basta rodar o seguinte comando no terminal:

```bash
make black
```

## Deploy

Com a aplicação _dockerizada_ e testada, é possível efetuar o _deploy_ em um orquestrador de _containers_ a exemplo do [Kubernetes](https://kubernetes.io/pt/), ou mesmo, com o orquestrador nativo do Docker [Swarm](https://docs.docker.com/engine/swarm/).

## Construído Com

* [black](https://github.com/psf/black)
* [loguru](https://github.com/Delgan/loguru)
* [Elasticsearch](https://www.elastic.co/elasticsearch/)
* [pydantic](https://pydantic-docs.helpmanual.io)
* [fastapi](https://fastapi.tiangolo.com)
* [uvicorn](https://www.uvicorn.org)
* [gunicorn](https://gunicorn.org)
* [requests](https://requests.readthedocs.io/en/master/)
* [sphinx](https://www.sphinx-doc.org/en/master/)

## Versionamento

O versionamento segue o padrão do [Versionamento Semântico](http://semver.org/).

## License

Todos os direitos são reservados ao autor Kevin de Santana Araujo.

## Outras informações

* Caso tenha alguma dúvida em relação ao projeto, ou queira contribuir com sugestões ou críticas, abra uma [issue]() ou procure o desenvolvedor através do email kevin_santana.araujo@hotmail.com
