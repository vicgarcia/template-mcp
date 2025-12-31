FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

RUN mkdir -p /templates

USER nobody

ENV TZ=America/New_York

ENV TEMPLATE_MCP_PATH=/templates

CMD ["template-mcp"]
