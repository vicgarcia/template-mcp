# Template MCP Server

A dynamic MCP (Model Context Protocol) server for Claude Desktop that loads markdown templates from YAML files. Drop a YAML file in a folder, restart Claude Desktop, and your template becomes available as an MCP tool.

## Features

- **Zero-Code Template Management**: Add/edit templates without touching Python code
- **Dynamic Discovery**: YAML files automatically loaded at startup
- **Preserved Formatting**: Multi-line templates with exact whitespace preservation
- **Agent Guidance**: Each template includes step-by-step instructions for Claude
- **Docker-First**: Designed for Claude Desktop with Docker deployment

## Quick Start

### 1. Create Template Directory

```bash
mkdir -p ~/.template-mcp/templates
```

### 2. Add Example Templates

Three templates are included in this repo. Copy them to your template directory:

```bash
cp ~/.template-mcp/templates/*.yml ~/.template-mcp/templates/
```

Or create your own. Example `~/.template-mcp/templates/status_update.yml`:

```yaml
description: Return instructions and template for generating status updates

instructions: |
  Generate a status update by following these steps:

  1. Identify the project name from context
  2. Determine current status (on track, at risk, blocked)
  3. Summarize progress made since last update
  4. List upcoming tasks and next steps
  5. Populate the template with all information
  6. Return the completed markdown document

template: |
  # Status Update: {project name}

  **Status**: {current status}

  ## Progress
  {progress details}

  ## Next Steps
  {upcoming tasks}
```

### 3. Build Docker Image

```bash
docker build -t template-mcp .
```

### 4. Configure Claude Desktop

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "templates": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/Users/yourname/.template-mcp/templates:/templates",
        "template-mcp"
      ]
    }
  }
}
```

**Important**: Replace `/Users/yourname/` with your actual home directory path.

### 5. Restart Claude Desktop

Your templates are now available as MCP tools!

## YAML Template Format

Each template file has three required fields:

```yaml
description: Brief description (becomes tool docstring)

instructions: |
  Multi-line step-by-step guide for Claude.
  Use the pipe (|) to preserve formatting.

template: |
  # Markdown Template

  {use curly braces for placeholders}
  All whitespace is preserved exactly.
```

## Included Templates

Three example templates are included:

- **weekly_linear_project_update.yml** - Weekly project updates with Linear integration
- **quarterly_business_review.yml** - Quarterly business reviews with metrics
- **meeting_notes.yml** - Structured meeting notes with action items

These are created in `~/.template-mcp/templates/` when you first set up the server.

## Adding Templates

**Zero code required**:

1. Create a `.yml` or `.yaml` file in `~/.template-mcp/templates/`
2. Add the three required fields: `description`, `instructions`, `template`
3. Restart Claude Desktop

The filename becomes the tool name:
- `meeting_notes.yml` → `get_meeting_notes_template()` tool
- `status_update.yml` → `get_status_update_template()` tool

## How It Works

When you ask Claude to "generate a weekly update":

1. Claude calls `get_weekly_linear_project_update_template` tool
2. Receives `instructions` with step-by-step guidance
3. Receives `template` with `{placeholder}` fields
4. Follows instructions to gather data (using other MCP tools, APIs, etc.)
5. Populates the template
6. Returns formatted markdown

The `instructions` field turns templates into **guided workflows**, not just passive forms.

## Template Writing Guidelines

### description
- One-line summary
- Format: "Return instructions and template for generating [document type]"

### instructions
- Always use `|` for multi-line strings
- Start with "Generate a [type] by following these steps:"
- Use numbered lists
- Be specific about data gathering
- End with "Populate the template and return the completed markdown document"

### template
- Always use `|` for multi-line strings
- Use markdown formatting
- Use natural language placeholders: `{total revenue for quarter}` not `{rev_q1}`
- All whitespace preserved exactly

## Development

### Local Development (Without Docker)

```bash
# Clone and install
git clone https://github.com/[username]/template-mcp
cd template-mcp
pip install -e .

# Create local templates (for testing)
mkdir -p /tmp/templates
# Add .yml files...

# Run with custom path
TEMPLATE_MCP_PATH=/tmp/templates template-mcp
```

### Building Docker Image

```bash
docker build -t template-mcp .
```

### Testing Docker Image

```bash
# Create test templates
mkdir -p /tmp/test-templates
echo 'description: Test
instructions: |
  Test instructions
template: |
  # Test {name}' > /tmp/test-templates/test.yml

# Run container
docker run -i --rm -v /tmp/test-templates:/templates template-mcp
```

## Architecture

The server uses three main components:

- **loader.py**: Discovers and loads YAML templates from `/templates`
- **server.py**: Dynamically registers tools with FastMCP at startup
- **Docker container**: Mounts host directory to `/templates` for template access

### How It Works

1. Docker container starts with `/templates` mount point
2. Server reads `TEMPLATE_MCP_PATH` (defaults to `/templates`)
3. `TemplateLoader` scans for `.yml` and `.yaml` files
4. Each valid YAML file becomes an MCP tool
5. Server communicates with Claude Desktop via STDIO

## Requirements

- Docker
- Claude Desktop
- Template directory with `.yml` files

## License

MIT
