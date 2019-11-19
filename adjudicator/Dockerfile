FROM crossbario/autobahn-python:cpy3

RUN pip install --upgrade autobahn
RUN pip install --upgrade requests
RUN pip install --upgrade google-auth
RUN pip install --upgrade PyMySQL
RUN pip install --upgrade PyYAML

ENV MYSQL_HOST db

WORKDIR /app
COPY . /app

ENV CBURL ws://crossbar:80/ws
ENV CBREALM realm1

ENTRYPOINT ./wait-for-it.sh crossbar:80 -t 120 -- python /app/game_gen.py
