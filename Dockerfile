FROM python:3.12-slim

WORKDIR /app

# copy package files
COPY pyproject.toml ./
COPY src/ ./src/

# install package
RUN pip install --no-cache-dir -e .

# create templates directory
RUN mkdir -p /templates

# run as non-root user
USER nobody

# set default template path
ENV TEMPLATE_MCP_PATH=/templates

# run server on STDIO (for Claude Desktop MCP)
CMD ["template-mcp"]
