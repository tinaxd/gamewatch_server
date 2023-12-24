FROM python:3.10-bookworm

RUN --mount=type=cache,target=/root/.cache/pip pip install pipenv

WORKDIR /app
COPY Pipfile Pipfile.lock /app/
RUN --mount=type=cache,target=/root/.cache/pip pipenv install --system --deploy

COPY . /app

ENV DEBUG=False
EXPOSE 49152/tcp
EXPOSE 49153/tcp

CMD ["docker_start.sh"]
