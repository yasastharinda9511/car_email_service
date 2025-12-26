import os
from pathlib import Path


class TemplateRenderer:
    def __init__(self, template_dir="templates"):
        self.template_dir = Path(__file__).parent.parent / template_dir

    def load_template(self, template_name: str) -> str:
        """Load HTML template from file"""
        template_path = self.template_dir / template_name
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def render_template(self, template_content: str, **kwargs) -> str:
        """Replace template placeholders with actual values"""
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            template_content = template_content.replace(placeholder, str(value) if value else "")
        return template_content

    def build_section(self, condition, content: str) -> str:
        """Return content if condition is True, empty string otherwise"""
        return content if condition else ""
