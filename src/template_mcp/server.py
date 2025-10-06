from typing import Optional, Dict, Any
from fastmcp import FastMCP

import logging
logger = logging.getLogger(__name__)


mcp = FastMCP('template MCP')


import template_mcp.template_content.weekly_linear_project_update as weekly_linear_project_update

@mcp.tool
def get_weekly_linear_project_update_template() -> Dict[str, Any]:
    ''' Return instructions and template for generating weekly linear project updates '''
    return {
        'instructions': weekly_linear_project_update.INSTRUCTIONS,
        'template': weekly_linear_project_update.TEMPLATE,
    }
