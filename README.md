<div align="center">

<picture>
  <source media="(prefers-color-scheme: light)" srcset="/docs/logo_tiny_light.svg">
  <img alt="tiny corp logo" src="assets/minigen-logo.svg" width="50%" height="50%">
</picture>

# MiniGen

**A lightweight, intuitive Python framework for building AI agents and multi-agent systems**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-available-brightgreen.svg)](https://d-ev.space/)

<h3>

[🏠 Homepage](https://github.com/devdezzies/minigen) | [📖 Documentation](https://d-ev.space/) | [🚀 Quick Start](#quick-start) | [💡 Examples](#examples)

</h3>

</div>

## Overview

MiniGen is a lightweight, Python-native framework designed to help you learn and build AI agents without getting lost in boilerplate code. It's built for simplicity, experimentation, and understanding the core concepts that make AI agents work.

### Key Features

- 🎯 **Simple & Intuitive**: Minimal boilerplate, maximum functionality
- 🔧 **Tool Integration**: Easily extend agents with custom capabilities
- 🔗 **Workflow Orchestration**: Chain prompts and coordinate multiple agents
- ⚡ **Parallel Execution**: Run agents concurrently for better performance
- 🎭 **Multi-Agent Networks**: Build complex systems with intelligent routing
- 🔌 **Provider Agnostic**: Works with OpenAI, Anthropic, and other LLM providers

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
pip install minigen
```

Or install from source:

```bash
git clone https://github.com/devdezzies/minigen.git
cd minigen
pip install -e .
```

## Quick Start

### 1. Environment Setup

Create a `.env` file in your project root:

```env
# Required: Your API key
OPENAI_API_KEY="your-api-key-here"

# Optional: Specify your preferred model
DEFAULT_MODEL="gpt-4"

# Optional: For non-OpenAI providers
BASE_URL="https://api.anthropic.com"  # Example for Claude
```

### 2. Create Your First Agent

```python
from minigen import Agent

# Create a specialized agent
pirate_agent = Agent(
    name="Captain Sarcasm",
    system_prompt="You are a sarcastic pirate captain. Answer all questions with sarcasm and pirate slang."
)

# Start chatting
response = pirate_agent.chat("How does a computer work?")
print(f"[{pirate_agent.name}]: {response}")
```

## Core Concepts

### Agents

Think of an **Agent** as a specialized AI personality with a specific role. Each agent has:
- A **name** for identification
- A **system prompt** that defines its behavior and expertise
- Optional **tools** for extended capabilities
- **Memory** of the conversation context

### Tools

**Tools** are Python functions that agents can call to interact with the external world:

```python
from minigen import Agent, tool

@tool(description="Convert temperature from Celsius to Fahrenheit")
def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32

@tool(description="Get current weather for a city")
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny and 25°C"

# Create agent with tools
weather_agent = Agent(
    name="Weather Assistant",
    system_prompt="You help users with weather information and temperature conversions.",
    tools=[celsius_to_fahrenheit, get_weather]
)

response = weather_agent.chat("What's the weather in London and convert 25°C to Fahrenheit?")
```

### Chains

**Chains** execute a sequence of prompts, where each step builds on the previous output:

```python
from minigen import Agent, Chain

agent = Agent()
research_chain = Chain(agent=agent, verbose=True)

research_chain \
    .add_step("Generate a comprehensive technical explanation of {input}") \
    .add_step("Simplify the following explanation for a beginner: {input}") \
    .add_step("Create a practical example to illustrate: {input}")

result = research_chain.run("machine learning")
print(result)
```

### Agent Networks

**Agent Networks** coordinate multiple specialized agents to solve complex problems:

```python
from minigen import Agent, AgentNetwork

# Create specialized agents
planner = Agent(
    name="Planner", 
    system_prompt="You excel at breaking down complex tasks into actionable steps."
)

researcher = Agent(
    name="Researcher",
    system_prompt="You find accurate information and cite sources."
)

writer = Agent(
    name="Writer",
    system_prompt="You create well-structured, engaging content."
)

# Build the network
network = AgentNetwork()
network.add_node(planner)
network.add_node(researcher)
network.add_node(writer)

# Set up intelligent routing
from minigen import create_llm_router
router = create_llm_router(network.nodes)
network.set_router(router)
network.set_entry_point("Planner")

# Execute the workflow
result = network.run(
    "Write a blog post about the benefits of renewable energy",
    max_rounds=8
)
```

## Examples

### Example 1: Code Review Agent

```python
from minigen import Agent, tool
import ast

@tool(description="Analyze Python code for potential issues")
def analyze_code(code: str) -> str:
    try:
        ast.parse(code)
        return "Code syntax is valid. Ready for detailed review."
    except SyntaxError as e:
        return f"Syntax error found: {e}"

code_reviewer = Agent(
    name="Code Reviewer",
    system_prompt="""You are an expert Python developer who reviews code for:
    - Best practices and conventions (PEP 8)
    - Performance optimizations
    - Security vulnerabilities
    - Code maintainability
    Provide specific, actionable feedback.""",
    tools=[analyze_code]
)

# Review some code
code_to_review = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

review = code_reviewer.chat(f"Please review this code:\n{code_to_review}")
print(review)
```

### Example 2: Research and Writing Pipeline

```python
from minigen import Agent, AgentNetwork, create_llm_router

# Define specialized agents
fact_checker = Agent(
    name="FactChecker",
    system_prompt="You verify information accuracy and find reliable sources."
)

content_creator = Agent(
    name="ContentCreator", 
    system_prompt="You create engaging, well-structured content based on verified facts."
)

editor = Agent(
    name="Editor",
    system_prompt="You polish content for clarity, flow, and professionalism."
)

# Create the pipeline
pipeline = AgentNetwork()
pipeline.add_node(fact_checker)
pipeline.add_node(content_creator)
pipeline.add_node(editor)

router = create_llm_router(pipeline.nodes)
pipeline.set_router(router)
pipeline.set_entry_point("FactChecker")

# Generate content
final_content = pipeline.run(
    "Create an article about the environmental impact of electric vehicles",
    max_rounds=6
)
```

### Example 3: Parallel Processing

```python
from minigen import Agent, AgentNetwork, Parallel, create_llm_router

# Create domain experts
tech_expert = Agent(
    name="TechExpert",
    system_prompt="You analyze technology trends and innovations."
)

market_expert = Agent(
    name="MarketExpert", 
    system_prompt="You analyze market conditions and business implications."
)

synthesizer = Agent(
    name="Synthesizer",
    system_prompt="You combine different perspectives into comprehensive insights."
)

# Set up parallel processing
parallel_analysis = Parallel(
    name="ParallelAnalysis",
    agent_names=["TechExpert", "MarketExpert"]
)

network = AgentNetwork()
network.add_node(tech_expert)
network.add_node(market_expert)
network.add_node(synthesizer)
network.add_node(parallel_analysis)

router = create_llm_router(network.nodes)
network.set_router(router)
network.set_entry_point("ParallelAnalysis")

# Analyze from multiple perspectives
analysis = network.run(
    "Analyze the potential impact of quantum computing on the cryptocurrency market",
    max_rounds=5
)
```

## Advanced Usage

### Custom Routing Logic

```python
from minigen import AgentNetwork, NetworkState
from typing import Optional

def custom_router(state: NetworkState) -> Optional[str]:
    last_message = state.messages[-1]
    
    # Route based on content keywords
    content = last_message.get('content', '').lower()
    
    if 'research' in content:
        return "Researcher"
    elif 'write' in content or 'draft' in content:
        return "Writer"
    elif 'review' in content or 'edit' in content:
        return "Editor"
    elif 'done' in content or 'complete' in content:
        return None  # End the workflow
    
    return "Planner"  # Default fallback

network.set_router(custom_router)
```

**Parameters:**
- `name`: Agent identifier
- `system_prompt`: Instructions that define agent behavior
- `tools`: List of functions the agent can call
- `model`: LLM model to use (defaults to environment setting)
- `max_retries`: Maximum retry attempts for failed requests
- `timeout`: Request timeout in seconds

**Methods:**
- `chat(message: str) -> str`: Send message and get response
- `get_conversation_history() -> List[Dict]`: Get full conversation
- `clear_memory()`: Clear conversation history
- `add_tool(tool: Callable)`: Add a new tool to the agent

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📚 [Documentation](https://d-ev.space/)
- 🐛 [Issue Tracker](https://github.com/devdezzies/minigen/issues)
- 💬 [Discussions](https://github.com/devdezzies/minigen/discussions)

---

<div align="center">

**Built with ❤️ by the MiniGen community**

</div>