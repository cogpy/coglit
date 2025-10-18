#!/usr/bin/env python3
"""
OpenCog Autonomous Orchestrator Example for OpenLit

This example demonstrates how to use OpenCog as an autonomous orchestrator
for LLM applications with OpenLit observability.
"""

import os
import time
from typing import Dict, Any

# Import OpenLit with OpenCog orchestration
import openlit

# Import OpenCog orchestration functions
from openlit.instrumentation.opencog.opencog import (
    orchestrate_llm_call,
    plan_workflow,
    get_global_orchestrator
)


def example_basic_orchestration():
    """
    Example of basic LLM call orchestration using OpenCog.
    """
    print("🤖 OpenCog Basic Orchestration Example")
    print("=" * 50)
    
    # Example: Chat completion orchestration
    chat_decision = orchestrate_llm_call(
        operation="chat",
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "What is AI?"}],
        max_tokens=100
    )
    
    print(f"Chat Decision: {chat_decision}")
    print(f"Selected Agent: {chat_decision['selected_agent']}")
    print(f"Cost Optimized: {chat_decision['cost_optimized']}")
    print(f"Confidence: {chat_decision['confidence']}")
    print()
    
    # Example: Embedding orchestration
    embed_decision = orchestrate_llm_call(
        operation="embedding",
        model="text-embedding-ada-002",
        input="This is a test document"
    )
    
    print(f"Embedding Decision: {embed_decision}")
    print(f"Selected Agent: {embed_decision['selected_agent']}")
    print()


def example_workflow_orchestration():
    """
    Example of multi-step workflow orchestration using OpenCog.
    """
    print("🧠 OpenCog Workflow Orchestration Example")
    print("=" * 50)
    
    # Define a complex workflow
    workflow_definition = {
        "name": "ai-research-workflow",
        "description": "Research AI topics and generate a summary",
        "steps": [
            {
                "operation": "chat",
                "model": "gpt-4",
                "parameters": {
                    "messages": [{"role": "user", "content": "Research current AI trends"}],
                    "max_tokens": 500
                }
            },
            {
                "operation": "embedding", 
                "model": "text-embedding-ada-002",
                "parameters": {
                    "input": "AI trends research results"
                }
            },
            {
                "operation": "completion",
                "model": "claude-3",
                "parameters": {
                    "prompt": "Summarize the AI research findings",
                    "max_tokens": 200
                }
            }
        ]
    }
    
    # Get orchestration plan
    execution_plan = plan_workflow(workflow_definition)
    
    print(f"Workflow Plan: {execution_plan}")
    print(f"Execution Order: {execution_plan['execution_order']}")
    print(f"Estimated Cost: ${execution_plan['estimated_cost']:.4f}")
    print(f"Optimization: {execution_plan['optimization_applied']}")
    print()


def example_cost_optimization():
    """
    Example showing cost optimization through OpenCog reasoning.
    """
    print("💰 OpenCog Cost Optimization Example")
    print("=" * 50)
    
    # Compare orchestration for expensive vs cheaper models
    expensive_decision = orchestrate_llm_call(
        operation="chat",
        model="gpt-4",
        messages=[{"role": "user", "content": "Simple question"}]
    )
    
    cheaper_decision = orchestrate_llm_call(
        operation="chat", 
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Simple question"}]
    )
    
    print("Expensive Model (GPT-4):")
    print(f"  - Cost Optimized: {expensive_decision['cost_optimized']}")
    print(f"  - Confidence: {expensive_decision['confidence']}")
    print()
    
    print("Cheaper Model (GPT-3.5):")
    print(f"  - Cost Optimized: {cheaper_decision['cost_optimized']}")
    print(f"  - Confidence: {cheaper_decision['confidence']}")
    print()


def example_with_hyperon():
    """
    Example showing enhanced capabilities when OpenCog Hyperon is available.
    """
    print("🧮 OpenCog Hyperon Integration Example")
    print("=" * 50)
    
    orchestrator = get_global_orchestrator()
    
    if orchestrator and orchestrator._runner:
        print("✓ OpenCog Hyperon is available - using cognitive reasoning")
        
        # This would use OpenCog's cognitive architecture for decision making
        decision = orchestrator._cognitive_orchestration(
            "chat",
            "gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Complex reasoning task"}]
        )
        
        print(f"Cognitive Decision: {decision}")
        print(f"Reasoning Method: {decision['reasoning_method']}")
        
    else:
        print("ℹ️ OpenCog Hyperon not available - using basic rule-based orchestration")
        print("To enable cognitive reasoning, install: pip install hyperon")
        
        # Falls back to basic orchestration
        decision = orchestrate_llm_call(
            "chat",
            "gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Complex reasoning task"}]
        )
        
        print(f"Basic Decision: {decision}")
        print(f"Reasoning Method: {decision['reasoning_method']}")
    
    print()


def example_autonomous_agent_simulation():
    """
    Simulate an autonomous agent making decisions about LLM usage.
    """
    print("🤖 Autonomous Agent Simulation")
    print("=" * 50)
    
    # Simulate different scenarios the agent might encounter
    scenarios = [
        {
            "name": "User Query Processing",
            "operation": "chat",
            "model": "gpt-3.5-turbo",
            "context": "Interactive user support"
        },
        {
            "name": "Document Summarization", 
            "operation": "completion",
            "model": "claude-3",
            "context": "Batch processing task"
        },
        {
            "name": "Semantic Search",
            "operation": "embedding",
            "model": "text-embedding-ada-002", 
            "context": "Information retrieval"
        },
        {
            "name": "Creative Writing",
            "operation": "text-generation",
            "model": "gpt-4",
            "context": "Creative content generation"
        }
    ]
    
    for scenario in scenarios:
        print(f"Scenario: {scenario['name']}")
        
        decision = orchestrate_llm_call(
            operation=scenario["operation"],
            model=scenario["model"],
            context=scenario["context"]
        )
        
        print(f"  Agent Decision: {decision['selected_agent']}")
        print(f"  Cost Optimized: {decision['cost_optimized']}")
        print(f"  Confidence: {decision['confidence']:.1f}")
        print(f"  Reasoning: {decision['reasoning_method']}")
        print()


def main():
    """
    Main function demonstrating OpenCog autonomous orchestration with OpenLit.
    """
    print("🚀 OpenCog Autonomous Orchestrator for OpenLit")
    print("=" * 60)
    print()
    
    # Initialize OpenLit with OpenCog instrumentation enabled
    # OpenCog will be automatically instrumented if available
    openlit.init(
        environment="opencog-example",
        application_name="opencog-autonomous-orchestrator-demo",
        # OpenCog instrumentation is enabled by default when hyperon is available
        disabled_instrumentors=[],  # Don't disable any instrumentors
        detailed_tracing=True,  # Enable detailed tracing for better observability
    )
    
    print("✓ OpenLit initialized with OpenCog autonomous orchestration")
    print()
    
    # Run examples
    try:
        example_basic_orchestration()
        time.sleep(1)
        
        example_workflow_orchestration()
        time.sleep(1)
        
        example_cost_optimization()
        time.sleep(1)
        
        example_with_hyperon()
        time.sleep(1)
        
        example_autonomous_agent_simulation()
        
        print("🎉 OpenCog Autonomous Orchestration Demo Completed!")
        print()
        print("Key Benefits:")
        print("• Intelligent LLM model selection")
        print("• Automated cost optimization")
        print("• Workflow planning and optimization")
        print("• Cognitive reasoning (with Hyperon)")
        print("• Full observability with OpenLit")
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()