from itertools import chain
from pathlib import Path
from typing import List, Optional
import yaml

from .models import Template

import logging
logger = logging.getLogger(__name__)


class TemplateLoader:
    ''' loads YAML template files and creates MCP tools dynamically '''

    def __init__(self, templates_path: str):
        self.templates_path = Path(templates_path).expanduser().resolve()

    def load_templates(self) -> List[Template]:
        '''
        load all YAML templates from the configured path

        returns:
            list of Template objects
        '''
        if not self.templates_path.exists():
            logger.warning(f"templates path does not exist: {self.templates_path}")
            return []

        if not self.templates_path.is_dir():
            logger.error(f"templates path is not a directory: {self.templates_path}")
            return []

        templates = []

        # load both .yml and .yaml files
        for yaml_file in chain(self.templates_path.glob("*.yml"), self.templates_path.glob("*.yaml")):
            template = self._load_yaml_file(yaml_file)
            if template:
                templates.append(template)

        logger.info(f"loaded {len(templates)} templates from {self.templates_path}")
        return templates

    def _load_yaml_file(self, yaml_file: Path) -> Optional[Template]:
        ''' load and validate a single YAML template file '''
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            logger.error(f"template {yaml_file.name} is not a valid YAML dict")
            return None

        # extract template name from filename (remove .yml/.yaml extension)
        template_name = yaml_file.stem

        # pydantic validates required fields and non-empty values
        try:
            return Template(
                name=template_name,
                description=data.get('description', ''),
                instructions=data.get('instructions', ''),
                template=data.get('template', ''),
            )
        except Exception as e:
            logger.error(f"template {yaml_file.name} validation failed: {e}")
            return None
