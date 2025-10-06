# Template MCP Server

A lightweight MCP (Model Context Protocol) server that provides structured markdown templates with usage instructions for AI agents. Each template includes step-by-step guidance and curly-brace placeholders (e.g., `{total revenue for quarter}`).

## Key Features

Each tool returns:
- **`instructions`**: Step-by-step guide for the AI agent on how to use the template
- **`template`**: Markdown string with placeholder fields

This dual approach allows AI agents to understand not just the output format, but the entire workflow for generating documents.

## Installation

### Local Development

```bash
# Clone the repository
git clone https://github.com/[username]/template-mcp
cd template-mcp

# Install in editable mode
pip install -e .

# Run the server
template-mcp
```

### Docker

```bash
# Build the image
docker build -t template-mcp:local .

# Run the server
docker run -i --rm template-mcp:local
```

## Claude Desktop Integration

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "templates": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "template-mcp:local"
      ]
    }
  }
}
```

Or for local installation:

```json
{
  "mcpServers": {
    "templates": {
      "command": "template-mcp"
    }
  }
}
```

## Available Templates

### get_weekly_linear_project_update_template
Returns instructions and template for generating weekly project updates with revenue metrics.

**Example Usage**: "Generate a weekly update for our project"

## Usage Example

When Claude Desktop is configured with this MCP server:

**User**: "Generate a weekly project update"

**Claude**:
1. Calls `get_weekly_linear_project_update_template` tool
2. Receives `instructions` (e.g., "Use tools to get the total revenue...")
3. Receives `template` (markdown with `{total revenue for month}` placeholder)
4. Follows instructions to gather data
5. Populates template with gathered information
6. Returns formatted markdown report

The `instructions` field guides Claude through the entire process, making templates more than passive forms—they become **guided workflows**.

## Adding New Templates

### Step 1: Create Template Content File

Create `src/template_mcp/template_content/status_update.py`:

```python
TEMPLATE = '''# Status Update: {project name}

**Status**: {current status}

## Progress

{progress details}

## Next Steps

{upcoming tasks}
'''

INSTRUCTIONS = '''Generate a status update by following these steps:

1. Identify the project name from context
2. Determine the current status (on track, at risk, blocked)
3. Summarize progress made since last update
4. List upcoming tasks and next steps
5. Populate the template with all information
6. Return the completed markdown status update
'''
```

### Step 2: Add Tool Function

Add to `src/template_mcp/server.py`:

```python
import template_mcp.template_content.status_update as status_update

@mcp.tool
def get_status_update_template() -> Dict[str, Any]:
    ''' Return instructions and template for generating status updates '''
    return {
        'instructions': status_update.INSTRUCTIONS,
        'template': status_update.TEMPLATE,
    }
```

That's it! No configuration files, no registration, no complex setup.

## Architecture

The server uses a simple two-layer architecture:

1. **Template Content Layer** (`template_content/*.py`): Pure data files with `INSTRUCTIONS` and `TEMPLATE` constants
2. **Server Layer** (`server.py`): FastMCP tool functions that return the instructions and template

This separation allows you to:
- Edit templates without touching Python logic
- See all available tools in one file (`server.py`)
- Keep template content simple and maintainable

## Requirements

- Python >=3.12
- FastMCP >=0.9.0

## Design Philosophy

**Ultra-minimal**: No external dependencies beyond FastMCP, no configuration, no state management

**Separation of concerns**: Content (templates) is separate from code (tools)

**Agent-friendly**: Instructions guide AI agents through complex workflows

**Zero magic**: Explicit imports, no auto-discovery, predictable behavior

## License

MIT
