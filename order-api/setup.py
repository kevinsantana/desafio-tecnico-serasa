# Source: https://packaging.python.org/guides/distributing-packages-using-setuptools/

from os import path
from order_api import __version__
from setuptools import find_packages, setup

run_requirements = [
    "loguru==0.5.3",
    "pydantic==1.8.2",
    "fastapi==0.68.0",
    "uvloop==0.16.0",
    "uvicorn==0.15.0",
    "gunicorn==20.1.0",
    "aiofiles==0.7.0",
    "requests==2.23.0",
    "sphinx-rtd-theme==0.5.2",
    "recommonmark==0.7.1",
    "Jinja2==3.0.1",
    "Sphinx==4.1.2",
    "starlette==0.14.2",
    "pytest==6.2.4",
    "sphinx-autobuild==0.7.1",
    "elasticsearch==7.14.0"
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="Order Api",
    version=__version__,
    author="Kevin de Santana Araujo",
    author_email="kevin_santana.araujo@hotmail.com",
    packages=find_packages(exclude=["docs", "tests"]),
    url="https://github.com/SelecaoSerasaConsumidor/BE-KevinAraujo",
    description="API para manter pedidos",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=run_requirements,
    python_requires=">=3.8",
)
