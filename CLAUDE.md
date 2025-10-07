# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Template MCP is a lightweight, dynamic MCP (Model Context Protocol) server for Claude Desktop that loads markdown templates from YAML files. Templates are automatically discovered and registered as MCP tools at server startup. Each tool returns two values:
- **`instructions`**: step-by-step guide telling the AI agent how to use the template
- **`template`**: markdown string with curly-brace placeholders (e.g., `{total revenue for quarter}`)

**Core Philosophy**: dynamic configuration via YAML files outside the codebase, Docker-first deployment, zero-code template management.

## Technology Stack

- **Framework**: FastMCP (Python framework for building MCP servers)
- **Python Version**: >=3.12
- **Transport**: STDIO (for Claude Desktop via Docker)
- **Package Manager**: pip with pyproject.toml
- **Dependencies**: FastMCP, PyYAML
- **Deployment**: Docker

## Development Commands

### Docker (Recommended)
```bash
# build image
docker build -t template-mcp .

# test with volume mount
docker run -i --rm -v ~/.template-mcp/templates:/templates template-mcp
```

### Local Development (Testing)
```bash
# install in editable mode
pip install -e .

# run with custom template path
TEMPLATE_MCP_PATH=/tmp/templates template-mcp
```

## Architecture

### Dynamic YAML-Based System

**Template Files** (mounted at `/templates` in Docker)
- YAML files automatically discovered at startup
- each YAML file becomes an MCP tool
- filename (without extension) becomes the tool name
- supports multi-line strings with preserved whitespace

**Server Components**:
- `loader.py`: discovers and validates YAML templates from filesystem
- `server.py`: dynamically registers tools with FastMCP at runtime
- `__init__.py`: minimal (just a comment)
- no hardcoded templates, no imports needed

### YAML Template Schema

Each template file must contain three fields:

```yaml
description: Brief description of what this template generates (becomes tool docstring)

instructions: |
  Multi-line step-by-step guide for the AI agent.

  Use the pipe (|) character to preserve line breaks and formatting.
  This tells the agent exactly how to use the template.

template: |
  # Markdown Template

  Use {curly braces} for placeholders.
  {descriptive placeholder names are best}

  All whitespace and formatting is preserved.
```

### Example Template File

`~/.template-mcp/templates/weekly_status.yml`:
```yaml
description: Return instructions and template for generating weekly status reports

instructions: |
  Generate a weekly status report by following these steps:

  1. Gather completed tasks from project management tools
  2. List current in-progress work items
  3. Identify any blockers or risks
  4. Calculate key metrics for the week
  5. Populate the template with all information
  6. Return the completed markdown document

template: |
  # Weekly Status - {week ending date}

  ## Completed
  {bulleted list of completed items}

  ## In Progress
  {current work items with owners}

  ## Blockers
  {any issues blocking progress}

  ## Metrics
  - Tasks Completed: {number}
  - On Track: {yes/no}
```

## Adding New Templates

**Zero code required**:

1. Create a `.yml` or `.yaml` file in your templates directory
2. Add `description`, `instructions`, and `template` fields
3. Restart Claude Desktop

The filename becomes the tool name. For example:
- `meeting_notes.yml` → `get_meeting_notes_template()` tool
- `quarterly_review.yml` → `get_quarterly_review_template()` tool

## Template Writing Guidelines

### Description Field
- brief one-line summary of what the template generates
- becomes the tool's docstring in MCP
- format: "Return instructions and template for generating [document type]"

### Instructions Field
- always use `|` for multi-line strings to preserve formatting
- start with "Generate a [type] by following these steps:"
- use numbered lists for step-by-step workflows
- be specific about what data to gather
- mention if the agent should use specific tools or APIs
- end with "Populate the template and return the completed markdown document"

### Template Field
- always use `|` for multi-line strings to preserve formatting
- use markdown formatting (headers, lists, bold, etc.)
- placeholders use curly braces: `{descriptive name}`
- use natural language: `{total revenue for quarter}` not `{rev_q1}`
- keep templates focused on structure, not instructions
- all whitespace and line breaks are preserved exactly

## Configuration

### Environment Variable

`TEMPLATE_MCP_PATH`: path to directory containing YAML template files
- default: `/templates` (for Docker deployment)
- can be absolute or relative path
- tilde expansion supported (`~/templates`) for local development

### Template Directory Setup

```bash
# create default directory
mkdir -p ~/.template-mcp/templates

# add your first template
cat > ~/.template-mcp/templates/example.yml << 'EOF'
description: Return instructions and template for example documents

instructions: |
  Generate an example document by following these steps:

  1. Extract key information from user context
  2. Populate the template
  3. Return the completed markdown

template: |
  # Example: {title}

  {content goes here}
EOF
```

## Project Structure

```
src/template_mcp/
├── __init__.py              # minimal (just a comment)
├── server.py                # dynamic tool registration + run() entrypoint
├── loader.py                # YAML template discovery and loading
└── template_content/        # (deprecated - kept for reference)

~/.template-mcp/templates/   # user's template directory (mounted to /templates in Docker)
├── weekly_linear_project_update.yml
├── quarterly_business_review.yml
└── meeting_notes.yml
```

## Design Constraints

- **no parameters**: tool functions take no arguments
- **no state**: server is completely stateless
- **no validation**: no placeholder checking or schema enforcement
- **no processing**: no server-side template rendering or substitution
- **dynamic loading**: templates loaded at startup from filesystem
- **environment configuration**: single env var for template path
- **pure YAML data**: templates contain only strings, no logic
- **Docker-first**: designed for Docker deployment with volume mounts

## Common Tasks

### Adding a New Template
1. Create `.yml` file in templates directory
2. Add `description`, `instructions`, `template` fields
3. Restart Claude Desktop

### Modifying an Existing Template
1. Edit the YAML file
2. Restart Claude Desktop to pick up changes

### Using a Custom Template Directory
```bash
# set environment variable
export TEMPLATE_MCP_PATH=/my/custom/path

# run server
template-mcp
```

### Testing Locally
```bash
# install with dependencies
pip install -e .

# create test template
mkdir -p /tmp/templates
# ... add YAML files ...

# run server
TEMPLATE_MCP_PATH=/tmp/templates template-mcp
```

## Package Configuration

The `pyproject.toml` uses:
- package name: `template-mcp`
- CLI entrypoint: `template-mcp` → `template_mcp.server:run`
- dependencies: `fastmcp>=0.9.0`, `pyyaml>=6.0`
- build backend: Hatchling

## Claude Desktop Integration

### Docker Setup (Recommended)

Build the Docker image:
```bash
docker build -t template-mcp .
```

Add to Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "templates": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/Users/yourname/.template-mcp/templates:/templates",
        "template-mcp"
      ]
    }
  }
}
```

The container defaults to `/templates` as the template path, so no environment variable needed when using the volume mount shown above.

**Important**: Replace `/Users/yourname/` with your actual home directory path.

## Why This Architecture?

**Zero-Code Template Management**: add/edit templates without touching Python code
**Dynamic Discovery**: new templates automatically available on restart
**External Configuration**: templates live outside the codebase, easy to share/version
**Preserved Formatting**: YAML literal blocks preserve all whitespace and line breaks
**Simple Deployment**: mount template directory in Docker, configure path via env var
**No Magic**: explicit YAML loading, clear tool registration, straightforward flow
**Easy Sharing**: share template YAML files across teams without code changes
**Docker-First**: designed for Claude Desktop with containerized deployment
