from typing import Annotated, Optional
from pydantic import BaseModel
from pydantic.types import StringConstraints


NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]


class Template(BaseModel):
    ''' represents a single template loaded from YAML '''

    name: NonEmptyStr
    description: NonEmptyStr
    instructions: NonEmptyStr
    template: Optional[NonEmptyStr] = None

    @property
    def tool_name(self) -> str:
        ''' generate the MCP tool function name '''
        return f"get_{self.name}_template"
