FROM python:3.8-slim as builder
COPY . .
RUN pip install poetry && rm -rf dist && poetry build -f wheel


FROM python:3.8-alpine
COPY --from=builder /dist /dist
RUN pip install /dist/*
ENTRYPOINT ["gitlab-mirror-maker"]