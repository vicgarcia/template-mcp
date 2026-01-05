# Template MCP Server

A dynamic MCP (Model Context Protocol) server for Claude Desktop that loads markdown templates from YAML files. Drop a YAML file in a folder, restart Claude Desktop, and your template becomes available as an MCP tool.

## Features

- **Zero-Code Template Management**: Add/edit templates without touching Python code
- **Dynamic Discovery**: YAML files automatically loaded at startup
- **Type-Safe Validation**: Pydantic models ensure template data integrity
- **Flexible Templates**: Support instruction-only workflows or instruction + template combos
- **Preserved Formatting**: Multi-line templates with exact whitespace preservation
- **Agent Guidance**: Each template includes step-by-step instructions for Claude
- **Built-in Utilities**: `get_current_date()` tool provides current datetime/timezone
- **Docker-First**: Designed for Claude Desktop with Docker deployment

## Quick Start

### 1. Create Template Directory

```bash
mkdir -p ~/.template-mcp/templates
```

### 2. Create Your First Template

Create `~/.template-mcp/templates/weekly_update.yml`:

```yaml
description: Return instructions and template for generating weekly project updates

instructions: |
  Generate a weekly project update by following these steps:

  1. Use the Linear MCP to find the project by name or ID
  2. Use the Linear MCP to query issues completed this week (filter by status and updated date)
  3. Use the Linear MCP to query issues currently in progress
  4. Identify any blockers or at-risk issues
  5. Calculate key metrics (completed vs planned, velocity, etc.)
  6. Populate the template with all gathered information
  7. Return the completed markdown document

template: |
  # Weekly Update: {project name} - {week ending date}

  ## Summary
  {one paragraph executive summary of the week}

  ## Completed This Week
  {bulleted list of completed issues with Linear links}

  ## In Progress
  {bulleted list of active issues with assignees}

  ## Blockers & Risks
  {any issues blocking progress or at risk}

  ## Metrics
  - Issues Completed: {number}
  - Issues In Progress: {number}
  - On Track: {yes/no with brief explanation}

  ## Next Week
  {planned work and focus areas}
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

Each template file requires two fields and optionally supports a third:

```yaml
description: Brief description (becomes tool docstring)

instructions: |
  Multi-line step-by-step guide for Claude.
  Use the pipe (|) to preserve formatting.

template: |  # OPTIONAL - omit for instruction-only workflows
  # Markdown Template

  {use curly braces for placeholders}
  All whitespace is preserved exactly.
```

**Required fields**: `description` and `instructions`
**Optional field**: `template` (omit for pure workflow orchestration)

### Instruction-Only Example

For workflows that don't need structured output:

```yaml
description: Orchestrate standup data collection from Linear and Slack

instructions: |
  Collect standup data by following these steps:

  1. Use the Linear MCP to query issues updated in the last 7 days
  2. Use the Slack MCP to fetch recent messages from #engineering
  3. Summarize updates, blockers, and upcoming work
  4. Return a concise summary in bullet points
```

No `template` field needed - Claude will just follow the instructions.

## Built-in Utility Tools

The server provides utility tools:

- **`get_current_date()`**: Returns current datetime in ISO format, timezone name, and formatted string. Useful for templates that need date/time context.

## Adding More Templates

**Zero code required**:

1. Create a `.yml` or `.yaml` file in `~/.template-mcp/templates/`
2. Add required fields: `description` and `instructions`
3. Optionally add `template` field if structured output is needed
4. Restart Claude Desktop

The filename becomes the tool name:
- `weekly_update.yml` → `get_weekly_update_prompt()` tool
- `meeting_notes.yml` → `get_meeting_notes_prompt()` tool
- `standup_workflow.yml` → `get_standup_workflow_prompt()` tool

## How It Works

When you ask Claude to "generate a weekly update":

1. Claude calls `get_weekly_update_prompt` tool
2. Receives `instructions` with step-by-step guidance
3. Receives `template` with `{placeholder}` fields (if provided)
4. Follows instructions to gather data from Linear MCP (or other MCP tools)
5. Populates the template with real data (if template exists)
6. Returns formatted markdown document or summary

The `instructions` field turns templates into **guided workflows** that can orchestrate multiple MCP tools, not just passive forms.

## Template Writing Guidelines

### description
- One-line summary
- Format: "Return instructions and template for generating [document type]"

### instructions
- Always use `|` for multi-line strings
- Start with "Generate a [type] by following these steps:"
- Use numbered lists with specific actions
- Reference MCP tools when applicable (e.g., "Use the Linear MCP to...", "Use the GitHub MCP to...")
- Be specific about data gathering and filtering
- End with "Populate the template and return the completed markdown document"

### template (optional)
- Omit entirely for instruction-only workflows
- Include when you want structured markdown output
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

The server uses four main components:

- **models.py**: Pydantic `Template` model for type-safe validation
- **loader.py**: Discovers and validates YAML templates from filesystem
- **server.py**: Instantiates FastMCP and dynamically registers tools in `run()` method
- **Docker container**: Mounts host directory to `/templates` for template access

### How It Works

1. Docker container starts with `/templates` mount point
2. Server reads `TEMPLATE_MCP_PATH` (defaults to `/templates`)
3. `TemplateLoader` scans for `.yml` and `.yaml` files
4. Each file is validated against the Pydantic `Template` model
5. Valid templates become MCP tools dynamically registered with FastMCP
6. Server exits if no valid templates are found
7. Server communicates with Claude Desktop via STDIO

## Requirements

- Docker
- Claude Desktop
- Template directory with `.yml` files

## License

MIT
