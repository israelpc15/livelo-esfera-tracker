FROM python:3.9-alpine3.13

# atribuindo o caminho da pasta principal em uma constante
ENV MAIN_DIR=/home/main

# Criando a pasta para a aplicação utilizando a constante
RUN mkdir "${MAIN_DIR}"

# definindo a pasta de trabalho oficial utilizando a constante
WORKDIR "${MAIN_DIR}"

# instalando as libs genéricas necessárias para as execuções dos jobs
RUN apk add --no-cache --update \
    python3 python3-dev gcc \
    gfortran musl-dev g++ \
    libffi-dev openssl-dev \
    libxml2 libxml2-dev \
    libxslt libxslt-dev \
    libjpeg-turbo-dev zlib-dev

# comandos adicionais de upgrade
RUN pip install --upgrade pip
RUN pip install --upgrade cython
RUN pip install --upgrade lxml requests beautifulsoup4 pypika pytest
# RUN pip install pandas

# instalando as libs específicas
# ADD docker-imports.txt .
# RUN pip install -r docker-imports.txt
