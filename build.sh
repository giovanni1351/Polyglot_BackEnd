#!/bin/bash

# Atualiza os pacotes do sistema e instala as dependências
apt-get update
apt-get install -y python3.12-dev gcc libpq-dev

# (Adicione aqui outras libs que seu projeto possa precisar, ex: build-essential)

# Continua com a instalação normal do pip
pip install -r requirements.txt