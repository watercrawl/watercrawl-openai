from .plugins import OpenAIPlugin

__all__ = [
    'OpenAIPlugin'
]

__version__ = OpenAIPlugin.get_version()
__title__ = OpenAIPlugin.get_name()
__description__ = OpenAIPlugin.get_description()
__author__ = OpenAIPlugin.get_author()
__url__ = "https://github.com/watercrawl/watercrawl-openai"
