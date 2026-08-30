FROM python:3.14-slim

WORKDIR /app

ENV DATABASE_URL=postgresql+asyncpg://postgres:admin@administracioncentral-db:5432/administracion_central

COPY pyproject.toml .
RUN pip install .

COPY ./src ./

EXPOSE 8000

CMD ["python", "main.py"]