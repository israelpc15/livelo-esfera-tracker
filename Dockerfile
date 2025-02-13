FROM ubuntu:20.04

# atribuindo o caminho da pasta principal em uma constante
ENV MAIN_DIR=/home/main

# Criando a pasta para a aplicação utilizando a constante
RUN mkdir "${MAIN_DIR}"

# definindo a pasta de trabalho oficial utilizando a constante
WORKDIR "${MAIN_DIR}"

# instalando as libs genéricas necessárias para as execuções dos jobs
RUN apt-get update
RUN apt-get install -y python3.9 
RUN apt-get install -y python3.9-dev 
RUN apt-get install -y pip

# comandos adicionais de upgrade
RUN pip install --upgrade pip
RUN pip install --upgrade cython
RUN pip install --upgrade lxml requests beautifulsoup4 pypika pytest
# RUN pip install pandas

# instalando as libs específicas
# ADD docker-imports.txt .
# RUN pip install -r docker-imports.txt
