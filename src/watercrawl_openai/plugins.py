import json
from typing import Type
from . import settings

from openai import OpenAI
from openai._compat import cached_property

from watercrawl_plugin import AbstractPipelinePlugin, AbstractInputValidator, AbstractPlugin


class OpenAIInputValidator(AbstractInputValidator):
    def validate(self):
        """
        Validates the input options for the OpenAIExtractWithLLM plugin.

        Verifies that the following options are present in the CrawlRequest's options:
        - page_options.llm_model
        - page_options.extractor_schema

        If any of these are missing, an error is added to the validator.
        """
        assert settings.OPENAI_API_KEY, "OPENAI_API_KEY is not set in the environment"
        options = self.crawl_request.options
        if not options.get('page_options', {}).get('llm_model', False):
            self.add_error("page_options", "llm_model is required")
        if not options.get('page_options', {}).get('extractor_schema', False):
            self.add_error("page_options", "extractor_schema is required")


class OpenAIExtractPipeline(AbstractPipelinePlugin):

    @cached_property
    def client(self) -> OpenAI:
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
        )

    @property
    def model(self):
        return self.plugin_inputs.get('llm_model')

    def get_prompt(self):
        schema = self.plugin_inputs.get('extractor_schema', False)
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

    def process_item(self):
        """
        Processes an item by calling the OpenAI API and updating the item's fields.
        """
        if not self.model:
            return self.item

        markdown = self.item.get('markdown')
        if not markdown:
            raise ValueError("Item must contain a 'markdown' key with content.")

        # Call the OpenAI API for each task
        try:
            extraction_response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content": self.get_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": self.get_url_and_metadata(),
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": markdown}],
                    },
                    {
                        "role": "user",
                        "content": self.get_prompt(),
                    },
                ]
            )

            # Update the item with the responses
            self.item['extraction'] = json.loads(extraction_response.choices[0].message.content)

        except Exception as e:
            raise RuntimeError(f"Error processing item with OpenAI: {e}")

        return self.item

    def get_url_and_metadata(self):
        return f"URL: {self.item.get('url')}\nMetadata: {json.dumps(self.item.get('metadata'))}"


class OpenAIPlugin(AbstractPlugin):
    @classmethod
    def get_pipeline_class(cls) -> Type[OpenAIExtractPipeline]:
        return OpenAIExtractPipeline

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
