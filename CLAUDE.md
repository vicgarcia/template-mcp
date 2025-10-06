# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Template MCP is a lightweight MCP (Model Context Protocol) server that provides structured markdown templates with usage instructions for AI agents. Each tool returns two values:
- **`instructions`**: Step-by-step guide telling the AI agent how to use the template
- **`template`**: Markdown string with curly-brace placeholders (e.g., `{total revenue for quarter}`)

**Core Philosophy**: Ultra-minimal design - no external dependencies beyond FastMCP, no configuration, no state management. Templates are pure data, tools are simple wrappers.

## Technology Stack

- **Framework**: FastMCP (Python framework for building MCP servers)
- **Python Version**: >=3.12
- **Transport**: STDIO (for Claude Desktop compatibility)
- **Package Manager**: pip with pyproject.toml
- **Deployment**: Docker

## Development Commands

### Local Development
```bash
# Install in editable mode
pip install -e .

# Run the server
template-mcp
```

### Docker
```bash
# Build image
docker build -t template-mcp:local .

# Run server
docker run -i --rm template-mcp:local
```

## Architecture

### Two-Layer Pattern

**Layer 1: Template Content** (`src/template_mcp/template_content/*.py`)
- Each file contains two module-level string constants:
  - `INSTRUCTIONS`: Multi-line string with step-by-step guidance
  - `TEMPLATE`: Markdown template with `{placeholder}` syntax
- Pure data - no functions, no classes, no logic
- Keep files under 50 lines total

**Layer 2: Server Tools** (`src/template_mcp/server.py`)
- Initializes FastMCP instance: `mcp = FastMCP('template MCP')`
- Imports template content modules
- Defines tool functions decorated with `@mcp.tool`
- Each tool returns `{'instructions': str, 'template': str}`

### Example: Complete Template Implementation

**Step 1**: Create `src/template_mcp/template_content/example.py`:
```python
TEMPLATE = '''# Example Document: {title}

## Overview
{description}

## Metrics
- Total: {total value}
- Growth: {growth percentage}
'''

INSTRUCTIONS = '''Generate an example document by following these steps:

1. Extract the title from user context
2. Write a brief description (2-3 sentences)
3. Calculate or retrieve the total value
4. Calculate growth percentage vs. previous period
5. Populate the template with all information
6. Return the completed markdown document
'''
```

**Step 2**: Add tool function to `src/template_mcp/server.py`:
```python
import template_mcp.template_content.example as example

@mcp.tool
def get_example_template() -> Dict[str, Any]:
    ''' Return instructions and template for generating example documents '''
    return {
        'instructions': example.INSTRUCTIONS,
        'template': example.TEMPLATE,
    }
```

That's it. No registration, no `__init__.py` updates, no configuration.

## Adding New Templates

1. Create `src/template_mcp/template_content/your_template.py` with `TEMPLATE` and `INSTRUCTIONS` constants
2. Add import and tool function to `src/template_mcp/server.py`
3. Tool function name should be descriptive: `get_{template_name}_template`
4. Docstring should briefly describe what the template generates

## Template Writing Guidelines

### TEMPLATE Constant
- Use triple-quoted strings for multi-line templates
- Use markdown formatting (headers, lists, bold, etc.)
- Placeholders use curly braces: `{descriptive name of data}`
- Placeholder names should be natural language: `{total revenue for quarter}` not `{revenue_q}`
- Keep templates focused on structure, not instructions

### INSTRUCTIONS Constant
- Start with "Generate a [type of document] by following these steps:"
- Use numbered lists for step-by-step workflows
- Be specific about what data to gather
- Mention if the agent should use tools or calculations
- End with "Populate the template and return the completed markdown document"
- Keep instructions concise but clear

## Project Structure

```
src/template_mcp/
├── __init__.py              # Entrypoint: exports mcp and main()
├── server.py                # FastMCP init + all tool functions
└── template_content/
    ├── weekly_linear_project_update.py
    ├── quarterly_report.py
    └── meeting_notes.py
```

## Key Patterns

### Tool Function Pattern
```python
@mcp.tool
def get_TEMPLATE_NAME_template() -> Dict[str, Any]:
    ''' Brief description of what this template generates '''
    return {
        'instructions': module_name.INSTRUCTIONS,
        'template': module_name.TEMPLATE,
    }
```

### Import Pattern
```python
import template_mcp.template_content.module_name as module_name
```

### Response Format
```python
{
    'instructions': str,  # Step-by-step guide for AI agent
    'template': str       # Markdown with {placeholders}
}
```

## Design Constraints (DO NOT VIOLATE)

- **No parameters**: Tool functions take no arguments
- **No state**: Server is completely stateless
- **No validation**: No placeholder checking or schema enforcement
- **No processing**: No server-side template rendering or substitution
- **No configuration**: No config files, environment variables, or external data sources
- **Pure data**: Template content files contain only string constants

## Common Tasks

### Adding a New Template
1. Create template content file with `TEMPLATE` and `INSTRUCTIONS`
2. Import in `server.py`
3. Add `@mcp.tool` function that returns the dict

### Modifying an Existing Template
1. Edit the `TEMPLATE` or `INSTRUCTIONS` constant in the content file
2. No code changes needed in `server.py`

### Testing Locally
```bash
pip install -e .
template-mcp
# Server runs on STDIO - use MCP inspector or Claude Desktop
```

## Package Configuration

The `pyproject.toml` uses:
- Package name: `template-mcp`
- CLI entrypoint: `template-mcp` → `template_mcp:main`
- Single dependency: `fastmcp>=0.9.0`
- Build backend: Hatchling

## Claude Desktop Integration

Users add this to their MCP settings:
```json
{
  "mcpServers": {
    "templates": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "template-mcp:local"]
    }
  }
}
```

## Why This Architecture?

**Separation of Concerns**: Content (templates) is separate from code (tools)
**Easy Maintenance**: Edit templates without touching Python logic
**Discoverability**: All tools visible in one file (`server.py`)
**Minimal Boilerplate**: 5 lines of code per template tool
**Agent Guidance**: Instructions tell agents exactly what to do with templates
**Zero Magic**: No auto-discovery, no registration, explicit imports
