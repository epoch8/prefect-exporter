FROM python:3.8
ENV POETRY_VERSION=1.1.11
WORKDIR /app

RUN apt-get -qy update && apt-get install --no-install-recommends -y git

RUN pip install pip --upgrade
RUN pip install poetry==$POETRY_VERSION

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY poetry.lock pyproject.toml ./

# Disable virtualenv creation for poetry
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction

COPY . .

CMD python prometheus_exporter.py
