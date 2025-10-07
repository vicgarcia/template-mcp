import os
from typing import Dict, Any
from fastmcp import FastMCP
from .loader import TemplateLoader

import logging
logger = logging.getLogger(__name__)


mcp = FastMCP('template MCP')


def _register_templates():
    """load YAML templates and register them as MCP tools dynamically"""
    templates_path = os.environ.get('TEMPLATE_MCP_PATH', '/templates')
    logger.info(f"loading templates from: {templates_path}")

    loader = TemplateLoader(templates_path)
    templates = loader.load_templates()

    for template_data in templates:
        _register_template_tool(template_data)

    logger.info(f"registered {len(templates)} template tools")


def _register_template_tool(template_data: Dict[str, Any]):
    """register a single template as an MCP tool"""
    name = template_data['name']
    description = template_data['description']
    instructions = template_data['instructions']
    template = template_data['template']

    # create tool function with closure to capture template data
    def tool_func() -> Dict[str, Any]:
        return {
            'instructions': instructions,
            'template': template,
        }

    # set function name and docstring
    tool_func.__name__ = f"get_{name}_template"
    tool_func.__doc__ = description

    # register with FastMCP
    mcp.tool(tool_func)
    logger.debug(f"registered tool: {tool_func.__name__}")


# load and register templates on module import
_register_templates()


def run():
    """entrypoint for template-mcp CLI command"""
    # configure basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    logger.info("starting template MCP server...")
    mcp.run()
