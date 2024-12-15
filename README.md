# Watercrawl-OpenAI Plugin

__version__: 0.0.1
__author__: Watercrawl

[![PyPI version](https://badge.fury.io/py/watercrawl-openai.svg)](https://badge.fury.io/py/watercrawl-openai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


## Description
This plugin allows you to use OpenAI's LLM to extract information from crawled content.


## Installation

You can install this plugin using pip:

```bash
pip install watercrawl-openai
```

## Usage
To use this plugin in your Watercrawl project, import it as follows:

In the WaterCrawl project environments add the following:
```python
WATER_CRAWL_PLUGINS="watercrawl_openai.OpenAIPlugin,...rest_of_plugins"
```

## Configuration

Make sure to set the following environment variables:

```env
OPENAI_API_KEY="Your OpenAI API key"
EXTRACT_SYSTEM_PROMPT="Your system prompt"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Links

GitHub: https://github.com/watercrawl/watercrawl-openai

