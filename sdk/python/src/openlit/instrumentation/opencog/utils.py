"""
OpenCog Instrumentation Utilities
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

def validate_workflow_definition(workflow_def: Dict[str, Any]) -> bool:
    """
    Validate a workflow definition structure.
    
    Args:
        workflow_def: Workflow definition to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["name", "steps"]
    
    for field in required_fields:
        if field not in workflow_def:
            logger.error(f"Missing required field '{field}' in workflow definition")
            return False
    
    steps = workflow_def.get("steps", [])
    if not isinstance(steps, list):
        logger.error("Workflow steps must be a list")
        return False
    
    for i, step in enumerate(steps):
        if not isinstance(step, dict):
            logger.error(f"Workflow step {i} must be a dictionary")
            return False
        
        if "operation" not in step:
            logger.error(f"Workflow step {i} missing 'operation' field")
            return False
    
    return True

def estimate_operation_cost(operation: str, model: str, **kwargs) -> float:
    """
    Estimate the cost of an LLM operation.
    
    Args:
        operation: Type of operation
        model: Model name
        **kwargs: Additional parameters
        
    Returns:
        Estimated cost in USD
    """
    # Basic cost estimation - in practice this would use pricing_info
    base_costs = {
        "chat": 0.002,
        "completion": 0.002,
        "embedding": 0.0001,
        "text-generation": 0.002,
        "image-generation": 0.02
    }
    
    base_cost = base_costs.get(operation, 0.001)
    
    # Model-specific multipliers
    if "gpt-4" in model.lower():
        base_cost *= 10
    elif "gpt-3.5" in model.lower():
        base_cost *= 1
    elif "claude" in model.lower():
        base_cost *= 5
    
    # Token count estimation from kwargs
    token_multiplier = 1.0
    if "messages" in kwargs:
        # Rough token estimation for chat
        message_count = len(kwargs["messages"])
        token_multiplier = max(1.0, message_count * 0.1)
    elif "prompt" in kwargs:
        # Rough token estimation for prompt
        prompt_length = len(str(kwargs["prompt"]))
        token_multiplier = max(1.0, prompt_length / 1000)
    
    return base_cost * token_multiplier

def format_opencog_query(operation: str, model: str, parameters: Dict[str, Any]) -> str:
    """
    Format parameters into an OpenCog MeTTa query.
    
    Args:
        operation: LLM operation type
        model: Model name
        parameters: Operation parameters
        
    Returns:
        Formatted MeTTa query string
    """
    # Simple parameter serialization for MeTTa
    param_str = ""
    for key, value in parameters.items():
        if isinstance(value, str):
            param_str += f' ({key} "{value}")'
        elif isinstance(value, (int, float)):
            param_str += f' ({key} {value})'
        elif isinstance(value, bool):
            param_str += f' ({key} {str(value).lower()})'
    
    return f'(llm-task ({operation} "{model}"){param_str})'

def extract_decision_from_metta_result(result: Any) -> Dict[str, Any]:
    """
    Extract decision information from MeTTa query result.
    
    Args:
        result: Result from MeTTa query execution
        
    Returns:
        Extracted decision dictionary
    """
    if not result:
        return {"agent": "default", "confidence": 0.0}
    
    # Simple parsing - in practice this would be more sophisticated
    result_str = str(result[0]) if len(result) > 0 else "default"
    
    # Extract agent name
    agent = "default-agent"
    if "openai" in result_str:
        agent = "openai-agent"
    elif "anthropic" in result_str:
        agent = "anthropic-agent"
    elif "embedding" in result_str:
        agent = "openai-embedding-agent"
    
    return {
        "agent": agent,
        "confidence": 0.8 if agent != "default-agent" else 0.1,
        "raw_result": result_str
    }

def optimize_workflow_execution_order(steps: List[Dict[str, Any]]) -> List[int]:
    """
    Optimize the execution order of workflow steps.
    
    Args:
        steps: List of workflow step definitions
        
    Returns:
        Optimized execution order as list of indices
    """
    # Simple optimization - prioritize by estimated cost (cheapest first)
    step_costs = []
    for i, step in enumerate(steps):
        operation = step.get("operation", "unknown")
        model = step.get("model", "unknown")
        cost = estimate_operation_cost(operation, model, **step.get("parameters", {}))
        step_costs.append((i, cost))
    
    # Sort by cost (ascending)
    sorted_steps = sorted(step_costs, key=lambda x: x[1])
    
    return [step[0] for step in sorted_steps]

def identify_parallelizable_steps(steps: List[Dict[str, Any]]) -> List[List[int]]:
    """
    Identify which workflow steps can be executed in parallel.
    
    Args:
        steps: List of workflow step definitions
        
    Returns:
        List of groups of step indices that can run in parallel
    """
    # Simple heuristic - steps with no dependencies can run in parallel
    # In practice, this would analyze data dependencies between steps
    
    parallel_groups = []
    independent_steps = []
    
    for i, step in enumerate(steps):
        # Check if step has dependencies on previous steps
        has_dependencies = False
        step_params = step.get("parameters", {})
        
        # Look for references to previous step outputs
        for param_value in step_params.values():
            if isinstance(param_value, str) and "step_" in param_value:
                has_dependencies = True
                break
        
        if not has_dependencies:
            independent_steps.append(i)
        else:
            # Start a new group if we have independent steps
            if independent_steps:
                parallel_groups.append(independent_steps)
                independent_steps = []
            # Dependent steps must run sequentially
            parallel_groups.append([i])
    
    # Add remaining independent steps
    if independent_steps:
        parallel_groups.append(independent_steps)
    
    return parallel_groups

def calculate_workflow_metrics(workflow_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate metrics for a workflow execution plan.
    
    Args:
        workflow_plan: Workflow execution plan
        
    Returns:
        Calculated metrics dictionary
    """
    execution_order = workflow_plan.get("execution_order", [])
    parallelizable_steps = workflow_plan.get("parallelizable_steps", [])
    estimated_cost = workflow_plan.get("estimated_cost", 0.0)
    
    # Calculate parallelization efficiency
    total_steps = len(execution_order)
    parallel_step_count = sum(len(group) for group in parallelizable_steps if len(group) > 1)
    parallelization_efficiency = parallel_step_count / total_steps if total_steps > 0 else 0.0
    
    # Estimate execution time savings
    sequential_time = total_steps * 1.0  # Assume 1 time unit per step
    parallel_time = len(parallelizable_steps) * 1.0  # One time unit per group
    time_savings = max(0.0, (sequential_time - parallel_time) / sequential_time)
    
    return {
        "total_steps": total_steps,
        "parallelizable_steps_count": parallel_step_count,
        "parallelization_efficiency": parallelization_efficiency,
        "estimated_sequential_time": sequential_time,
        "estimated_parallel_time": parallel_time,
        "time_savings_percentage": time_savings * 100,
        "estimated_cost": estimated_cost,
        "cost_per_step": estimated_cost / total_steps if total_steps > 0 else 0.0
    }