import os
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
from fastmcp import FastMCP
from .loader import TemplateLoader
from .models import Template

import logging
logger = logging.getLogger(__name__)


def _create_tool_function(template: Template):
    ''' factory function to create tool with proper closure '''
    def tool_func() -> Dict[str, Any]:
        result = {'instructions': template.instructions}
        if template.template is not None:
            result['template'] = template.template
        return result
    tool_func.__name__ = template.tool_name
    tool_func.__doc__ = template.description
    return tool_func


def run():
    ''' entrypoint for template-mcp CLI command '''
    # configure basic logging to console
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[logging.StreamHandler()]
    )

    # instantiate server
    mcp = FastMCP('template MCP')
    logger.info("starting template MCP server")

    # register get_current_date utility tool
    @mcp.tool()
    def get_current_date() -> Dict[str, str]:
        """Get the current date, time, and timezone"""
        now = datetime.now().astimezone()
        return {
            'datetime': now.isoformat(),
            'timezone': now.tzname() or str(now.tzinfo),
            'formatted': now.strftime('%Y-%m-%d %H:%M:%S %Z')
        }
    logger.info("registered tool: get_current_date")

    # load templates
    templates_path = os.environ.get('TEMPLATE_MCP_PATH', '/templates')
    templates = TemplateLoader(templates_path).load_templates()

    # register each template as a tool
    for tmpl in templates:
        tool_func = _create_tool_function(tmpl)
        mcp.tool(tool_func)
        logger.info(f"registered tool: {tool_func.__name__}")

    # run the server
    mcp.run()
