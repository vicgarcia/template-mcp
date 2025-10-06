# Product Requirements Document: Template MCP Server

## Project Overview

A lightweight MCP (Model Context Protocol) server that provides structured markdown templates with usage instructions for AI agents. Each template contains placeholder fields defined with curly braces that describe the data to be inserted (e.g., `{total revenue for quarter}`). The server exposes templates as individual MCP tools that return both **instructions** on how to use the template and the **template** itself.

**Key Philosophy**: Ultra-minimal design - no external dependencies beyond FastMCP, no configuration, no state management. Pure template + instruction delivery system.

## Technical Specifications

### Technology Stack
- **Framework**: [FastMCP](https://github.com/jlowin/fastmcp) - Python framework for building MCP servers
- **Python Version**: >=3.12
- **Transport**: STDIO (for Claude Desktop compatibility)
- **External Dependencies**: None beyond FastMCP

### Project Structure

```
template-mcp/
├── src/
│   └── template_mcp/
│       ├── __init__.py          # Package initialization and server startup
│       ├── server.py            # MCP server + tool function definitions
│       └── template_content/
│           ├── weekly_linear_project_update.py
│           ├── quarterly_report.py
│           └── meeting_notes.py
├── pyproject.toml              # Python project configuration
├── Dockerfile                  # Container configuration
├── .dockerignore              # Docker ignore patterns
├── .gitignore                 # Git ignore patterns
├── README.md                  # Project documentation
├── CLAUDE.md                  # Developer guidance for Claude Code
└── PRD.md                     # This file
```

### Architecture

**Server Layer** (`src/template_mcp/server.py`):
- Initializes FastMCP server instance
- Imports template content modules
- Defines tool functions decorated with `@mcp.tool`
- Each tool function returns `{'instructions': str, 'template': str}`

**Template Content Layer** (`src/template_mcp/template_content/*.py`):
- Each file contains two module-level constants:
  - `INSTRUCTIONS`: String describing how to use the template
  - `TEMPLATE`: Markdown string with curly-brace placeholders
- Templates are pure data - no functions, no logic
- Separation of content from server logic

**Template Format**:
- Pure markdown strings with curly-brace placeholders
- Placeholder format: `{descriptive name of data to insert}`
- Example: `Total Revenue: {total revenue for quarter}`
- No preprocessing, no variable substitution - raw markdown delivery

## Core Features

### Template Delivery System

**Server Pattern** (`server.py`):
```python
from typing import Dict, Any
from fastmcp import FastMCP
import logging

logger = logging.getLogger(__name__)

mcp = FastMCP('template MCP')

# Import template content
import template_mcp.template_content.weekly_linear_project_update as weekly_linear_project_update

@mcp.tool
def get_weekly_linear_project_update_template() -> Dict[str, Any]:
    ''' Return instructions and template for generating weekly linear project updates '''
    return {
        'instructions': weekly_linear_project_update.INSTRUCTIONS,
        'template': weekly_linear_project_update.TEMPLATE,
    }
```

**Template Content Pattern** (`template_content/example.py`):
```python
TEMPLATE = '''# Example Template: {title}

## Section 1

{content goes here}

## Section 2

**Metric**: {metric value}
'''

INSTRUCTIONS = '''Generate an example document by following these steps:

1. Identify the title from context
2. Gather relevant content for section 1
3. Calculate or retrieve the metric value
4. Populate the template with all gathered information
5. Return the completed markdown document
'''
```

### Response Format

All tools return a consistent structure:
```python
{
    'instructions': str,  # Step-by-step guide for the AI agent
    'template': str       # Raw markdown template with placeholders
}
```

**Key Design Decision**: The `instructions` field guides the AI agent on:
- What data to gather
- How to process or calculate values
- What tools or methods to use
- How to populate the template
- Expected output format

This allows templates to be more than passive forms - they become **guided workflows** for AI agents.

## Implementation Details

### Adding New Templates

To add a new template:

1. **Create template content file** in `src/template_mcp/template_content/new_template.py`:
```python
TEMPLATE = '''# Your Template Here

{placeholder values}
'''

INSTRUCTIONS = '''Steps to generate this document:

1. Step one
2. Step two
3. Populate template and return
'''
```

2. **Add tool function** in `src/template_mcp/server.py`:
```python
import template_mcp.template_content.new_template as new_template

@mcp.tool
def get_new_template() -> Dict[str, Any]:
    ''' Return instructions and template for new template '''
    return {
        'instructions': new_template.INSTRUCTIONS,
        'template': new_template.TEMPLATE,
    }
```

That's it. No registration, no configuration files, no complex setup.

### Package Configuration

**`pyproject.toml`**:
```toml
[project]
name = "template-mcp"
version = "0.1.0"
description = "MCP server for structured markdown templates with instructions"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=0.9.0"
]

[project.scripts]
template-mcp = "template_mcp:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### Docker Configuration

**`Dockerfile`**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

USER nobody

CMD ["template-mcp"]
```

## Usage & Integration

### Local Development

```bash
# Clone and install
git clone https://github.com/[username]/template-mcp
cd template-mcp
pip install -e .

# Run server
template-mcp
```

### Docker Deployment

```bash
# Build image
docker build -t template-mcp:local .

# Run server
docker run -i --rm template-mcp:local
```

### Claude Desktop Integration

Add to Claude Desktop MCP settings:
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

### Example User Interactions

**Scenario**: User asks for a weekly project update

1. Claude calls `get_weekly_linear_project_update_template` tool
2. Receives:
   - `instructions`: "Use tools to get the total revenue. Generate an update using the template."
   - `template`: Markdown with `{total revenue for month}` placeholder
3. Claude follows instructions to gather data
4. Populates template with gathered information
5. Returns formatted markdown report to user

**Key Benefit**: The agent knows exactly what data to gather and how to use it, rather than guessing from the template alone.

## Design Decisions

### Why Separate Instructions from Template?

**Clarity**: Agent knows exactly what actions to take, not just what the output should look like
**Flexibility**: Instructions can guide complex multi-step workflows
**Reusability**: Same template can have different instruction sets for different contexts
**Debugging**: Clear separation makes it easier to refine agent behavior

### Why Module Constants Instead of Functions?

**Simplicity**: Templates are pure data - no logic needed
**Performance**: Zero overhead - no function calls
**Clarity**: Obvious separation between content and code
**Maintainability**: Easy to edit templates without touching Python logic

### Why Tool Functions in server.py?

**Single Source of Truth**: All MCP tool definitions in one place
**Easy Discovery**: Developer can see all available tools at a glance
**Minimal Boilerplate**: Import + return pattern is 5 lines per tool
**FastMCP Pattern**: Follows FastMCP's decorator-based registration

### Why No Validation/Processing?

**Simplicity**: Templates are static strings - no logic needed
**Trust**: Agent handles all data gathering and population
**Performance**: Zero overhead - instant template retrieval
**Reliability**: No failure modes - always returns template + instructions

## Constraints & Limitations

### Deliberate Constraints
- **No State**: Server is stateless - no data storage or persistence
- **No Parameters**: Tools take no arguments (templates are fixed)
- **No Validation**: No placeholder validation or schema enforcement
- **No Processing**: No template rendering or substitution server-side
- **No Configuration**: No external config files or environment variables

### Technical Limitations
- Templates are static - cannot be modified without code changes
- No template versioning or variant selection
- No placeholder type checking or validation
- No template composition or inheritance

### Security Considerations
- No authentication (runs locally via Claude Desktop)
- No external network access required
- No file system access beyond code directory
- No user input validation needed (no user input accepted)

## Example Templates

### Weekly Linear Project Update

**Template Content** (`template_content/weekly_linear_project_update.py`):
```python
TEMPLATE = '''## Weekly Update

Total revenue for month: {total revenue for month}
'''

INSTRUCTIONS = '''Use tools to get the total revenue.

Generate an update using the template.
'''
```

### Quarterly Report

```python
TEMPLATE = '''# Q{quarter number} {year} Revenue Report

## Executive Summary

**Total Revenue**: {total revenue for quarter}
**Growth**: {revenue growth percentage} vs. previous quarter

## Performance Highlights

**Top Performing Product**: {top performing product}

## Key Insights

{key insights}
'''

INSTRUCTIONS = '''Generate a quarterly revenue report by following these steps:

1. Identify the quarter number (Q1-Q4) and year from context
2. Retrieve or calculate total revenue for the quarter
3. Calculate revenue growth percentage vs. previous quarter
4. Identify the top performing product
5. Analyze key trends and insights
6. Populate the template with all gathered information
7. Return the completed markdown report
'''
```

### Meeting Notes

```python
TEMPLATE = '''# Meeting Notes: {meeting title}

**Date**: {meeting date}
**Attendees**: {attendee names}

## Agenda

{agenda items}

## Discussion

{discussion notes}

## Decisions Made

{decisions}

## Action Items

{action items with owners and due dates}
'''

INSTRUCTIONS = '''Generate structured meeting notes by following these steps:

1. Extract meeting title or topic from context
2. Identify the meeting date
3. List all attendees
4. Document agenda items discussed
5. Summarize key discussion points
6. List all decisions made
7. Create action items with owners and due dates
8. Populate the template with all information
9. Return the completed markdown meeting notes
'''
```

## Success Metrics

### Development
- ✅ All tools return valid `{'instructions': str, 'template': str}`
- ✅ Each template content file is <50 lines
- ✅ Zero external dependencies beyond FastMCP
- ✅ Docker image builds successfully
- ✅ Server starts and registers all tools

### User Experience
- ✅ Tools discoverable in Claude Desktop
- ✅ Instructions clearly guide agent behavior
- ✅ Templates render correctly as markdown
- ✅ Placeholders are self-explanatory
- ✅ Agent successfully follows instructions and populates templates

## Future Enhancements (Out of Scope for v0.1)

### Potential Features
- Template variants with different instruction sets
- Structured placeholder metadata (types, examples, validation rules)
- Template categories/tags for discovery
- Multi-step workflow templates with branching logic
- Template composition (combining multiple templates)

### Not Planned
- User-defined templates (security risk)
- Template storage/database (adds complexity)
- Server-side template rendering (agent's responsibility)
- Multi-language support (English markdown only)

## References & Documentation

### FastMCP Resources
- **GitHub**: https://github.com/jlowin/fastmcp
- **Documentation**: https://github.com/jlowin/fastmcp/blob/main/README.md

### Model Context Protocol
- **Specification**: https://spec.modelcontextprotocol.io/
- **Documentation**: https://modelcontextprotocol.io/

### Related Tools
- **Claude Desktop**: https://claude.ai/download
- **MCP Servers List**: https://github.com/modelcontextprotocol/servers

---

**Document Version**: 2.0
**Last Updated**: 2025-10-05
**Status**: Reflects New Architecture with Instructions + Template Pattern
