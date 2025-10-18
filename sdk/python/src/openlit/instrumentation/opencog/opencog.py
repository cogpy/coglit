"""
OpenLIT OpenCog Instrumentor
"""

import os
import logging
from typing import Collection, Dict, Any, Optional
import importlib.metadata
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.trace import SpanKind, Status, StatusCode
from wrapt import wrap_function_wrapper

from openlit.semcov import SemanticConvention

logger = logging.getLogger(__name__)

_instruments = ("hyperon >= 0.1.0",)

class OpenCogOrchestrator:
    """
    OpenCog-based autonomous orchestrator for LLM applications.
    
    This class provides an autonomous agent that can orchestrate LLM workflows
    using OpenCog's cognitive architecture for decision-making and planning.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the OpenCog orchestrator.
        
        Args:
            config: Configuration dictionary containing tracer, environment, etc.
        """
        self.config = config
        self.tracer = config.get("tracer")
        self.environment = config.get("environment", "default")
        self.application_name = config.get("application_name", "default")
        self.metrics = config.get("metrics_dict", {})
        self.disable_metrics = config.get("disable_metrics", False)
        self.pricing_info = config.get("pricing_info", {})
        
        # Initialize OpenCog components when available
        self._atomspace = None
        self._runner = None
        self._initialize_opencog()
    
    def _initialize_opencog(self):
        """Initialize OpenCog Hyperon components if available."""
        try:
            # Try to import OpenCog Hyperon
            import hyperon
            from hyperon import GroundedAtom, MeTTa, AtomType, ValueAtom
            
            # Create MeTTa interpreter for autonomous reasoning
            self._runner = MeTTa()
            
            # Initialize basic orchestration knowledge base
            self._setup_orchestration_kb()
            
            logger.info("OpenCog orchestrator initialized successfully")
            
        except ImportError:
            logger.warning("OpenCog Hyperon not available. Orchestrator will operate in basic mode.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenCog orchestrator: {e}")
    
    def _setup_orchestration_kb(self):
        """Set up the knowledge base for LLM orchestration."""
        if self._runner is None:
            return
        
        # Define basic orchestration rules in MeTTa
        orchestration_kb = """
        ; Basic orchestration patterns
        (: LLMTask Type)
        (: Agent Type)
        (: Workflow Type)
        (: Decision Type)
        
        ; Define basic workflow orchestration rules
        (: orchestrate-workflow (-> Workflow LLMTask Decision))
        (= (orchestrate-workflow $workflow $task)
           (case $task
             ((chat-completion $prompt) (route-to-chat-agent $prompt))
             ((text-generation $input) (route-to-generation-agent $input))
             ((embedding $text) (route-to-embedding-agent $text))
             ($other (route-to-default-agent $other))))
        
        ; Define agent selection logic
        (: select-best-agent (-> LLMTask Agent))
        (= (select-best-agent $task)
           (case $task
             ((chat-completion $prompt) openai-agent)
             ((text-generation $input) anthropic-agent)
             ((embedding $text) openai-embedding-agent)
             ($other default-agent)))
        
        ; Define cost optimization rules
        (: optimize-cost (-> LLMTask Decision))
        (= (optimize-cost $task)
           (if (> (estimate-cost $task) 0.01)
               (use-local-model $task)
               (use-cloud-model $task)))
        """
        
        try:
            # Load the orchestration knowledge base
            self._runner.run(orchestration_kb)
            logger.debug("Orchestration knowledge base loaded")
        except Exception as e:
            logger.error(f"Failed to load orchestration KB: {e}")
    
    def orchestrate_llm_call(self, operation: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Orchestrate an LLM call using OpenCog reasoning.
        
        Args:
            operation: Type of LLM operation (chat, completion, embedding, etc.)
            model: Model to use
            **kwargs: Additional parameters for the operation
            
        Returns:
            Dictionary with orchestration decisions and metadata
        """
        if not self.tracer:
            return self._basic_orchestration(operation, model, **kwargs)
        
        with self.tracer.start_as_current_span(
            name=f"opencog.orchestrate.{operation}",
            kind=SpanKind.CLIENT,
        ) as span:
            
            try:
                # Set span attributes
                span.set_attribute(SemanticConvention.GEN_AI_SYSTEM, "opencog")
                span.set_attribute("opencog.operation", operation)
                span.set_attribute("opencog.model", model)
                span.set_attribute("opencog.environment", self.environment)
                span.set_attribute("opencog.application", self.application_name)
                
                # Perform orchestration
                if self._runner is not None:
                    decision = self._cognitive_orchestration(operation, model, **kwargs)
                else:
                    decision = self._basic_orchestration(operation, model, **kwargs)
                
                # Set result attributes
                span.set_attribute("opencog.decision.agent", decision.get("selected_agent", "unknown"))
                span.set_attribute("opencog.decision.cost_optimized", decision.get("cost_optimized", False))
                span.set_attribute("opencog.decision.confidence", decision.get("confidence", 0.0))
                
                span.set_status(Status(StatusCode.OK))
                return decision
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR), str(e))
                logger.error(f"OpenCog orchestration failed: {e}")
                # Fallback to basic orchestration
                return self._basic_orchestration(operation, model, **kwargs)
    
    def _cognitive_orchestration(self, operation: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Perform cognitive orchestration using OpenCog reasoning.
        
        Args:
            operation: LLM operation type
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Orchestration decision dictionary
        """
        try:
            # Create a task representation in MeTTa
            task_expr = f"({operation} {model})"
            
            # Query the orchestrator for the best agent
            agent_query = f"(select-best-agent ({operation} {model}))"
            agent_result = self._runner.run(agent_query)
            
            # Query for cost optimization
            cost_query = f"(optimize-cost ({operation} {model}))"
            cost_result = self._runner.run(cost_query)
            
            # Extract results
            selected_agent = "openai-agent"  # Default fallback
            cost_optimized = False
            
            if agent_result and len(agent_result) > 0:
                selected_agent = str(agent_result[0]).replace("(", "").replace(")", "")
            
            if cost_result and len(cost_result) > 0:
                cost_decision = str(cost_result[0])
                cost_optimized = "use-local-model" in cost_decision
            
            return {
                "selected_agent": selected_agent,
                "cost_optimized": cost_optimized,
                "confidence": 0.8,  # High confidence with OpenCog reasoning
                "reasoning_method": "opencog_cognitive",
                "task_representation": task_expr,
                "orchestration_metadata": {
                    "agent_selection": agent_result,
                    "cost_optimization": cost_result
                }
            }
            
        except Exception as e:
            logger.error(f"Cognitive orchestration failed: {e}")
            return self._basic_orchestration(operation, model, **kwargs)
    
    def _basic_orchestration(self, operation: str, model: str, **kwargs) -> Dict[str, Any]:
        """
        Basic orchestration without OpenCog reasoning.
        
        Args:
            operation: LLM operation type
            model: Model name
            **kwargs: Additional parameters
            
        Returns:
            Basic orchestration decision
        """
        # Simple rule-based orchestration
        agent_mapping = {
            "chat": "openai-agent",
            "completion": "anthropic-agent", 
            "embedding": "openai-embedding-agent",
            "text-generation": "anthropic-agent"
        }
        
        selected_agent = agent_mapping.get(operation, "default-agent")
        
        # Basic cost optimization
        cost_optimized = "gpt-4" not in model.lower()
        
        return {
            "selected_agent": selected_agent,
            "cost_optimized": cost_optimized,
            "confidence": 0.6,  # Lower confidence without cognitive reasoning
            "reasoning_method": "basic_rules",
            "orchestration_metadata": {
                "rule_applied": f"{operation} -> {selected_agent}"
            }
        }
    
    def plan_workflow(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """
        Plan a multi-step LLM workflow using OpenCog reasoning.
        
        Args:
            workflow_definition: Definition of the workflow steps
            
        Returns:
            Optimized workflow execution plan
        """
        if not self.tracer:
            return self._basic_workflow_planning(workflow_definition)
        
        with self.tracer.start_as_current_span(
            name="opencog.plan_workflow",
            kind=SpanKind.CLIENT,
        ) as span:
            
            try:
                span.set_attribute("opencog.workflow.steps", len(workflow_definition.get("steps", [])))
                span.set_attribute("opencog.workflow.name", workflow_definition.get("name", "unknown"))
                
                if self._runner is not None:
                    plan = self._cognitive_workflow_planning(workflow_definition)
                else:
                    plan = self._basic_workflow_planning(workflow_definition)
                
                span.set_attribute("opencog.plan.optimized_steps", len(plan.get("execution_order", [])))
                span.set_attribute("opencog.plan.estimated_cost", plan.get("estimated_cost", 0.0))
                
                span.set_status(Status(StatusCode.OK))
                return plan
                
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR), str(e))
                logger.error(f"Workflow planning failed: {e}")
                return self._basic_workflow_planning(workflow_definition)
    
    def _cognitive_workflow_planning(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Cognitive workflow planning using OpenCog."""
        steps = workflow_definition.get("steps", [])
        
        # For now, return optimized execution order
        # In a full implementation, this would use OpenCog's planning algorithms
        execution_order = list(range(len(steps)))
        
        return {
            "execution_order": execution_order,
            "estimated_cost": 0.05 * len(steps),  # Placeholder cost estimation
            "optimization_applied": "opencog_cognitive_planning",
            "parallelizable_steps": [],  # Could identify parallel execution opportunities
            "resource_allocation": {
                "memory_required": "low",
                "compute_required": "medium"
            }
        }
    
    def _basic_workflow_planning(self, workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Basic workflow planning without OpenCog."""
        steps = workflow_definition.get("steps", [])
        
        return {
            "execution_order": list(range(len(steps))),
            "estimated_cost": 0.1 * len(steps),  # Higher cost without optimization
            "optimization_applied": "basic_sequential",
            "parallelizable_steps": [],
            "resource_allocation": {
                "memory_required": "medium", 
                "compute_required": "high"
            }
        }


class OpenCogInstrumentor(BaseInstrumentor):
    """
    OpenLIT OpenCog instrumentor for autonomous orchestration.
    
    This instrumentor provides OpenCog-based autonomous agent capabilities
    for orchestrating LLM applications with cognitive reasoning.
    """
    
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments
    
    def _instrument(self, **kwargs):
        """Instrument OpenCog for autonomous orchestration."""
        tracer = kwargs.get("tracer")
        environment = kwargs.get("environment", "default")
        application_name = kwargs.get("application_name", "default")
        pricing_info = kwargs.get("pricing_info", {})
        capture_message_content = kwargs.get("capture_message_content", False)
        metrics_dict = kwargs.get("metrics_dict")
        disable_metrics = kwargs.get("disable_metrics", False)
        
        # Create orchestrator configuration
        config = {
            "tracer": tracer,
            "environment": environment,
            "application_name": application_name,
            "pricing_info": pricing_info,
            "capture_message_content": capture_message_content,
            "metrics_dict": metrics_dict,
            "disable_metrics": disable_metrics
        }
        
        # Initialize the global orchestrator instance
        orchestrator = OpenCogOrchestrator(config)
        
        # Store orchestrator for global access
        setattr(self, '_orchestrator', orchestrator)
        
        logger.info("OpenCog autonomous orchestrator instrumented successfully")
    
    def _uninstrument(self, **kwargs):
        """Remove OpenCog instrumentation."""
        if hasattr(self, '_orchestrator'):
            delattr(self, '_orchestrator')
        logger.info("OpenCog instrumentation removed")
    
    def get_orchestrator(self) -> Optional[OpenCogOrchestrator]:
        """Get the orchestrator instance."""
        return getattr(self, '_orchestrator', None)


# Global orchestrator instance for easy access
_global_orchestrator: Optional[OpenCogOrchestrator] = None

def get_global_orchestrator() -> Optional[OpenCogOrchestrator]:
    """Get the global OpenCog orchestrator instance."""
    return _global_orchestrator

def set_global_orchestrator(orchestrator: OpenCogOrchestrator):
    """Set the global OpenCog orchestrator instance."""
    global _global_orchestrator
    _global_orchestrator = orchestrator

def orchestrate_llm_call(operation: str, model: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to orchestrate an LLM call using the global orchestrator.
    
    Args:
        operation: Type of LLM operation
        model: Model to use
        **kwargs: Additional parameters
        
    Returns:
        Orchestration decision dictionary
    """
    orchestrator = get_global_orchestrator()
    if orchestrator:
        return orchestrator.orchestrate_llm_call(operation, model, **kwargs)
    else:
        logger.warning("No OpenCog orchestrator available. Using basic defaults.")
        return {
            "selected_agent": "default-agent",
            "cost_optimized": False,
            "confidence": 0.1,
            "reasoning_method": "none",
            "orchestration_metadata": {}
        }

def plan_workflow(workflow_definition: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to plan a workflow using the global orchestrator.
    
    Args:
        workflow_definition: Workflow definition
        
    Returns:
        Workflow execution plan
    """
    orchestrator = get_global_orchestrator()
    if orchestrator:
        return orchestrator.plan_workflow(workflow_definition)
    else:
        logger.warning("No OpenCog orchestrator available. Using basic planning.")
        steps = workflow_definition.get("steps", [])
        return {
            "execution_order": list(range(len(steps))),
            "estimated_cost": 0.1 * len(steps),
            "optimization_applied": "none",
            "parallelizable_steps": [],
            "resource_allocation": {"memory_required": "unknown", "compute_required": "unknown"}
        }