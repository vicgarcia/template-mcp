import os
import yaml
from pathlib import Path
from typing import Dict, Any, List

import logging
logger = logging.getLogger(__name__)


class TemplateLoader:
    """loads YAML template files and creates MCP tools dynamically"""

    def __init__(self, templates_path: str):
        self.templates_path = Path(templates_path).expanduser().resolve()

    def load_templates(self) -> List[Dict[str, Any]]:
        """
        load all YAML templates from the configured path

        returns:
            list of dicts with 'name', 'description', 'instructions', 'template'
        """
        if not self.templates_path.exists():
            logger.warning(f"templates path does not exist: {self.templates_path}")
            return []

        if not self.templates_path.is_dir():
            logger.error(f"templates path is not a directory: {self.templates_path}")
            return []

        templates = []

        for yaml_file in self.templates_path.glob("*.yml"):
            try:
                template_data = self._load_yaml_file(yaml_file)
                if template_data:
                    templates.append(template_data)
            except Exception as e:
                logger.error(f"failed to load template {yaml_file.name}: {e}")

        for yaml_file in self.templates_path.glob("*.yaml"):
            try:
                template_data = self._load_yaml_file(yaml_file)
                if template_data:
                    templates.append(template_data)
            except Exception as e:
                logger.error(f"failed to load template {yaml_file.name}: {e}")

        logger.info(f"loaded {len(templates)} templates from {self.templates_path}")
        return templates

    def _load_yaml_file(self, yaml_file: Path) -> Dict[str, Any]:
        """load and validate a single YAML template file"""
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            logger.error(f"template {yaml_file.name} is not a valid YAML dict")
            return None

        # validate required fields
        required_fields = ['description', 'instructions', 'template']
        for field in required_fields:
            if field not in data:
                logger.error(f"template {yaml_file.name} missing required field: {field}")
                return None

        # extract template name from filename (remove .yml/.yaml extension)
        template_name = yaml_file.stem

        return {
            'name': template_name,
            'description': data['description'],
            'instructions': data['instructions'],
            'template': data['template'],
        }
