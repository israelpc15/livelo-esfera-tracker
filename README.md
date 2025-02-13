
# Rastreador de pontos para Livelo e Esfera

Projeto que realiza integração com API's públicas da Livelo e do Esfera, em busca de promoções referentes a pontos disponibilizados a cada real gasto. Quando encontra a pontuação desejada, envia e-mail com aviso utilizando a plataforma sendInBlue.


## Stack utilizada


**Back-end:** Python, Docker


## Rodando localmente

Dependências: docker

Crie uma conta no sendInBlue (em caso de enviar e-mails)
Obtenha uma API Key

Clone o projeto

```bash
  git clone https://github.com/israelpc15/livelo-esfera-tracker
```

Entre no diretório do projeto

```bash
  cd livelo-esfera-tracker
```

Rode o docker-compose

```bash
  docker-compose up --build -d
  docker run -it livelo-esfera-tracker-crawler
```



Rode o script (livelo)
```bash
python3 crawler-livelo.py
```
ou 

Rode o script (esfera)
```bash
python3 crawler-esfera.py
```
