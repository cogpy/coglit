# OpenCog Autonomous Orchestrator for OpenLit

OpenCog integration provides autonomous orchestration capabilities for LLM applications using cognitive reasoning and intelligent decision-making.

## Overview

The OpenCog autonomous orchestrator leverages OpenCog Hyperon's cognitive architecture to make intelligent decisions about:
- LLM model selection
- Cost optimization
- Workflow planning and execution
- Resource allocation
- Multi-step reasoning chains

## Features

### 🤖 Autonomous Agent Capabilities
- **Intelligent Model Selection**: Automatically choose the best LLM for each task
- **Cost Optimization**: Optimize costs through smart model and provider selection
- **Workflow Orchestration**: Plan and execute multi-step LLM workflows
- **Cognitive Reasoning**: Use OpenCog's reasoning engine for complex decisions

### 📊 Full Observability
- **OpenTelemetry Integration**: Native telemetry for all orchestration decisions
- **Decision Tracing**: Track reasoning paths and confidence scores
- **Performance Metrics**: Monitor orchestration effectiveness
- **Cost Tracking**: Track actual vs. predicted costs

## Installation

### Basic Installation (Rule-based Orchestration)
```bash
pip install openlit
```

### Full Installation (Cognitive Orchestration)
```bash
pip install openlit[opencog]
# OR
pip install openlit hyperon
```

## Quick Start

### Basic Usage

```python
import openlit
from openlit.instrumentation.opencog.opencog import orchestrate_llm_call

# Initialize OpenLit with OpenCog
openlit.init(
    environment="production",
    application_name="my-ai-app"
)

# Orchestrate an LLM call
decision = orchestrate_llm_call(
    operation="chat",
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What is AI?"}]
)

print(f"Selected Agent: {decision['selected_agent']}")
print(f"Cost Optimized: {decision['cost_optimized']}")
print(f"Confidence: {decision['confidence']}")
```

### Workflow Orchestration

```python
from openlit.instrumentation.opencog.opencog import plan_workflow

# Define a multi-step workflow
workflow = {
    "name": "research-and-summarize",
    "steps": [
        {
            "operation": "chat",
            "model": "gpt-4",
            "parameters": {
                "messages": [{"role": "user", "content": "Research AI trends"}],
                "max_tokens": 500
            }
        },
        {
            "operation": "completion",
            "model": "claude-3",
            "parameters": {
                "prompt": "Summarize the research",
                "max_tokens": 200
            }
        }
    ]
}

# Get optimized execution plan
plan = plan_workflow(workflow)
print(f"Execution Order: {plan['execution_order']}")
print(f"Estimated Cost: ${plan['estimated_cost']}")
```

## Architecture

### OpenCog Hyperon Integration

When OpenCog Hyperon is available, the orchestrator uses:

1. **MeTTa Language**: For expressing orchestration rules and reasoning
2. **Atomspace**: For storing and retrieving orchestration knowledge
3. **Cognitive Processes**: For making intelligent decisions
4. **Learning**: Adapting orchestration strategies over time

### Fallback Mode

Without OpenCog Hyperon, the orchestrator uses:
- Rule-based decision making
- Static cost optimization
- Sequential workflow execution
- Basic model selection heuristics

## Configuration

### Environment Variables

```bash
# OpenLit configuration
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
export OPENLIT_ENVIRONMENT="production"
export OPENLIT_APPLICATION_NAME="my-ai-app"

# OpenCog-specific configuration  
export OPENCOG_REASONING_DEPTH="5"
export OPENCOG_CONFIDENCE_THRESHOLD="0.7"
```

### Programmatic Configuration

```python
import openlit

openlit.init(
    environment="production",
    application_name="my-ai-app",
    # OpenCog is auto-enabled when hyperon is available
    disabled_instrumentors=[],  # Don't disable OpenCog
    detailed_tracing=True  # Get detailed orchestration traces
)
```

## Orchestration Rules

The OpenCog orchestrator uses the following decision logic:

### Model Selection
- **Chat Operations**: Prefer OpenAI GPT models
- **Text Generation**: Prefer Anthropic Claude models  
- **Embeddings**: Use OpenAI embedding models
- **Code Generation**: Use specialized code models

### Cost Optimization
- **High-cost models** (GPT-4): Use for complex reasoning only
- **Medium-cost models** (GPT-3.5, Claude-3): Use for general tasks
- **Low-cost models** (Embeddings): Use for vector operations

### Workflow Optimization
- **Parallel Execution**: Identify independent steps
- **Cost Ordering**: Execute cheaper operations first
- **Resource Allocation**: Optimize memory and compute usage

## API Reference

### Core Functions

#### `orchestrate_llm_call(operation, model, **kwargs)`
Orchestrate a single LLM operation.

**Parameters:**
- `operation` (str): Type of operation ('chat', 'completion', 'embedding', etc.)
- `model` (str): Model name to use
- `**kwargs`: Additional parameters for the operation

**Returns:**
- `dict`: Orchestration decision with selected agent, confidence, etc.

#### `plan_workflow(workflow_definition)`
Plan the execution of a multi-step workflow.

**Parameters:**
- `workflow_definition` (dict): Workflow definition with name and steps

**Returns:**
- `dict`: Execution plan with order, cost estimates, and optimizations

### Classes

#### `OpenCogOrchestrator`
Main orchestrator class that handles decision-making.

**Methods:**
- `orchestrate_llm_call()`: Orchestrate individual operations
- `plan_workflow()`: Plan multi-step workflows
- `_cognitive_orchestration()`: Use OpenCog reasoning (when available)
- `_basic_orchestration()`: Use rule-based reasoning

#### `OpenCogInstrumentor`
OpenTelemetry instrumentor for integrating with OpenLit.

## Examples

### Cost-Aware Orchestration

```python
from openlit.instrumentation.opencog.opencog import orchestrate_llm_call

# Expensive operation - orchestrator may suggest alternatives
expensive_decision = orchestrate_llm_call(
    operation="chat",
    model="gpt-4",
    messages=[{"role": "user", "content": "Simple question"}]
)

print(f"Cost optimized: {expensive_decision['cost_optimized']}")
# Output: Cost optimized: False

# Cheaper alternative
cheap_decision = orchestrate_llm_call(
    operation="chat", 
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Simple question"}]
)

print(f"Cost optimized: {cheap_decision['cost_optimized']}")
# Output: Cost optimized: True
```

### Autonomous Agent Simulation

```python
from openlit.instrumentation.opencog.opencog import orchestrate_llm_call

# Simulate an autonomous agent processing different types of requests
scenarios = [
    ("User support chat", "chat", "gpt-3.5-turbo"),
    ("Creative writing", "completion", "gpt-4"),
    ("Document search", "embedding", "text-embedding-ada-002"),
]

for scenario_name, operation, model in scenarios:
    decision = orchestrate_llm_call(operation=operation, model=model)
    
    print(f"{scenario_name}:")
    print(f"  Agent: {decision['selected_agent']}")
    print(f"  Confidence: {decision['confidence']}")
    print(f"  Method: {decision['reasoning_method']}")
```

## Monitoring and Observability

### Telemetry Data

The OpenCog orchestrator generates telemetry for:

- **Decision Traces**: Each orchestration decision with reasoning path
- **Performance Metrics**: Decision time, confidence scores, accuracy
- **Cost Metrics**: Predicted vs. actual costs, optimization effectiveness
- **Error Tracking**: Failed decisions and fallback mechanisms

### Dashboard Metrics

Monitor these key metrics in your observability dashboard:

- `opencog.orchestration.decisions_total`: Total decisions made
- `opencog.orchestration.confidence_score`: Average confidence in decisions
- `opencog.orchestration.cost_savings`: Cost savings from optimization
- `opencog.workflow.execution_time`: Workflow execution times
- `opencog.reasoning.method`: Distribution of reasoning methods used

### Alerts

Set up alerts for:
- Low confidence scores (< 0.5)
- High cost operations without optimization
- Orchestration failures or errors
- Workflow execution timeouts

## Troubleshooting

### Common Issues

#### OpenCog Hyperon Not Found
```
ℹ️ OpenCog Hyperon not available - using basic rule-based orchestration
```
**Solution**: Install hyperon with `pip install hyperon`

#### Low Confidence Scores
If orchestration confidence is consistently low:
1. Check if appropriate models are available
2. Verify pricing information is up to date
3. Consider updating orchestration rules

#### High Costs Despite Optimization
If costs remain high despite orchestration:
1. Review model selection rules
2. Check if expensive models are truly necessary
3. Consider implementing custom cost thresholds

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("openlit.instrumentation.opencog").setLevel(logging.DEBUG)

import openlit
openlit.init(detailed_tracing=True)
```

## Contributing

To contribute to OpenCog orchestration:

1. **Knowledge Base**: Add new orchestration rules in MeTTa
2. **Model Support**: Add support for new LLM providers
3. **Optimization**: Improve cost and performance optimization
4. **Testing**: Add test cases for orchestration scenarios

### Development Setup

```bash
git clone https://github.com/openlit/openlit
cd openlit/sdk/python
pip install -e ".[dev,opencog]"
pytest tests/test_opencog.py
```

## License

This OpenCog integration is part of OpenLit and is licensed under the Apache 2.0 License.

## Related Documentation

- [OpenLit Documentation](https://docs.openlit.io/)
- [OpenCog Hyperon](https://hyperon.opencog.org/)
- [OpenTelemetry](https://opentelemetry.io/)
- [MeTTa Language Guide](https://hyperon-tutorials.readthedocs.io/)