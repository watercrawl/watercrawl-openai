import json
import warnings
from functools import cached_property
from typing import Type
from . import settings



from openai import OpenAI

from watercrawl_plugin import AbstractInputValidator, AbstractPlugin, BasePipeline


class OpenAIInputValidator(AbstractInputValidator):
    @classmethod
    def get_json_schema(cls):
        return {
            "title": "OpenAI LLM",
            "description": "Extracts information from crawled content using OpenAI's LLM.",
            "type": "object",
            "properties": {
                "llm_model": {
                    "title": "LLM Model",
                    "type": "string",
                    "default": "gpt-4o",
                    "enum": ["gpt-4o", "gpt-4o-mini"],
                    "ui": {
                        "widget": "select",
                        "placeholder": "Select a model",
                        "options": [
                            {"label": "GPT-4O", "value": "gpt-4o"},
                            {"label": "GPT-4O Mini", "value": "gpt-4o-mini"},
                        ]
                    },
                },
                "prompt": {
                    "title": "Prompt",
                    "type": "string",
                    "ui": {
                        "widget": 'textarea',
                        "placeholder": "Transform the above content into structured JSON output."
                    }
                },
                "extractor_schema": {
                    "title": "Extractor Schema",
                    "type": "object",
                    "default": {
                        "$schema": "http://json-schema.org/draft-07/schema#",
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "The main title of the webpage."
                            }
                        },
                        "required": ["title"],
                    },
                    "ui": {
                        "title": "JSON Schema",
                        "widget": "json-editor",
                        "editorHeight": "300px",
                        "fontSize": 14,
                        "editorOptions": {
                            "minimap": {"enabled": False},
                            "lineNumbers": "on",
                            "scrollBeyondLastLine": False,
                            "automaticLayout": True,
                            "folding": True,
                            "formatOnPaste": True,
                            "formatOnType": True
                        },
                    }
                },
            },
            "dependentRequired": {
                "is_active": ["llm_model"]
            }
        }

    def get_model(self):
        return self.data.get('llm_model', 'gpt-4o')

    def get_prompt(self):
        return self.data.get('prompt', self.get_prompt())

    def get_extractor_schema(self):
        return self.data.get('extractor_schema', False)

    def get_is_active(self):
        return self.data.get('is_active', False)


class OpenAIExtractPipeline(BasePipeline):

    @cached_property
    def client(self) -> OpenAI:
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    def get_validator(self, spider) -> OpenAIInputValidator:
        return spider.plugin_validators[OpenAIPlugin.plugin_key()]

    def get_prompt(self, validator: OpenAIInputValidator):
        schema = validator.get_extractor_schema()
        if schema:
            return ("Transform the above content into structured JSON "
                    "output based on the following schema:\n ```{prompt}```").format(
                prompt=schema
            )
        return "Transform the above content into structured JSON output."

    def get_system_prompt(self):
        if hasattr(settings, 'EXTRACT_SYSTEM_PROMPT') and settings.EXTRACT_SYSTEM_PROMPT:
            return settings.EXTRACT_SYSTEM_PROMPT
        return ("You are a helpful assistant that extracts information from crawled content."
                "You will extract information based on the user request."
                "You will only respond with the JSON output. Nothing else.")

    def process_item(self, item, spider):
        """
        Processes an item by calling the OpenAI API and updating the item's fields.
        """
        validator = self.get_validator(spider)
        if not validator:
            return item

        if not validator.data or not validator.get_is_active():
            return item

        markdown = item.get('markdown')
        if not markdown:
            warnings.warn("Item must contain a 'markdown' key with content.")
            return item

        # Call the OpenAI API for each task
        try:
            extraction_response = self.client.chat.completions.create(
                model=validator.get_model(),
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": self.get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self.get_url_and_metadata(item),
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": markdown}],
                    },
                    {
                        "role": "user",
                        "content": self.get_prompt(validator),
                    },
                ]
            )

            # Update the item with the responses
            item['extraction'] = json.loads(extraction_response.choices[0].message.content)

        except Exception as e:
            raise RuntimeError(f"Error processing item with OpenAI: {e}")

        return item

    def get_url_and_metadata(self, item):
        return f"URL: {item.get('url')}\nMetadata: {json.dumps(item.get('metadata'))}"


class OpenAIPlugin(AbstractPlugin):
    @classmethod
    def get_spider_middleware_classes(cls) -> dict:
        return {}

    @classmethod
    def get_downloader_middleware_classes(cls) -> dict:
        return {}

    @classmethod
    def plugin_key(cls) -> str:
        return "openai_extract"

    @classmethod
    def get_pipeline_classes(cls) -> dict:
        return {
            'watercrawl_openai.plugins.OpenAIExtractPipeline': 500,
        }

    @classmethod
    def get_input_validator(cls) -> Type[OpenAIInputValidator]:
        return OpenAIInputValidator

    @classmethod
    def extended_fields(cls):
        return ["extraction"]

    @classmethod
    def get_author(cls) -> str:
        return "AmirMohsen Asaran (https://github.com/amirasaran)"

    @classmethod
    def get_version(cls) -> str:
        return "1.0.0"

    @classmethod
    def get_name(cls) -> str:
        return "OpenAIExtractPipeline"

    @classmethod
    def get_description(cls) -> str:
        return "Extracts information from crawled content using OpenAI's LLM."
