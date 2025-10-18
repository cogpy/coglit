"""
Tests for OpenCog Autonomous Orchestrator Integration
"""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import openlit
from openlit.instrumentation.opencog.opencog import (
    OpenCogOrchestrator, 
    OpenCogInstrumentor,
    orchestrate_llm_call,
    plan_workflow
)
from openlit.instrumentation.opencog.utils import (
    validate_workflow_definition,
    estimate_operation_cost,
    optimize_workflow_execution_order
)


class TestOpenCogOrchestrator:
    """Test OpenCog Orchestrator functionality"""
    
    def setup_method(self):
        """Set up test configuration"""
        self.config = {
            "tracer": Mock(),
            "environment": "test",
            "application_name": "test-app",
            "pricing_info": {},
            "capture_message_content": True,
            "metrics_dict": {},
            "disable_metrics": False
        }
    
    def test_orchestrator_initialization_without_hyperon(self):
        """Test orchestrator initialization when hyperon is not available"""
        orchestrator = OpenCogOrchestrator(self.config)
        
        assert orchestrator.config == self.config
        assert orchestrator.environment == "test"
        assert orchestrator.application_name == "test-app"
        assert orchestrator._runner is None  # Should be None when hyperon not available
    
    def test_basic_orchestration(self):
        """Test basic orchestration without cognitive reasoning"""
        orchestrator = OpenCogOrchestrator(self.config)
        
        result = orchestrator._basic_orchestration("chat", "gpt-3.5-turbo")
        
        assert result["selected_agent"] == "openai-agent"
        assert result["confidence"] == 0.6
        assert result["reasoning_method"] == "basic_rules"
        assert result["cost_optimized"] is True  # gpt-4 not in model name
    
    def test_orchestrate_llm_call_basic(self):
        """Test LLM call orchestration in basic mode"""
        orchestrator = OpenCogOrchestrator(self.config)
        
        result = orchestrator.orchestrate_llm_call("completion", "claude-3")
        
        assert "selected_agent" in result
        assert "confidence" in result
        assert "reasoning_method" in result
        assert result["reasoning_method"] == "basic_rules"
    
    def test_basic_workflow_planning(self):
        """Test basic workflow planning"""
        orchestrator = OpenCogOrchestrator(self.config)
        
        workflow_def = {
            "name": "test-workflow",
            "steps": [
                {"operation": "chat", "model": "gpt-3.5-turbo"},
                {"operation": "completion", "model": "claude-3"}
            ]
        }
        
        result = orchestrator._basic_workflow_planning(workflow_def)
        
        assert result["execution_order"] == [0, 1]
        assert result["estimated_cost"] == 0.2  # 0.1 * 2 steps
        assert result["optimization_applied"] == "basic_sequential"


class TestOpenCogInstrumentor:
    """Test OpenCog Instrumentor"""
    
    def test_instrumentor_initialization(self):
        """Test instrumentor can be initialized"""
        instrumentor = OpenCogInstrumentor()
        
        assert instrumentor.instrumentation_dependencies() == ("hyperon >= 0.1.0",)
    
    def test_instrument_method(self):
        """Test the _instrument method"""
        instrumentor = OpenCogInstrumentor()
        
        # Mock configuration
        config = {
            "tracer": Mock(),
            "environment": "test",
            "application_name": "test-app",
            "pricing_info": {},
            "capture_message_content": True,
            "metrics_dict": {},
            "disable_metrics": False
        }
        
        # Should not raise an exception
        instrumentor._instrument(**config)
        
        # Should have created an orchestrator
        orchestrator = instrumentor.get_orchestrator()
        assert orchestrator is not None
        assert orchestrator.environment == "test"
    
    def test_uninstrument_method(self):
        """Test the _uninstrument method"""
        instrumentor = OpenCogInstrumentor()
        
        # First instrument
        config = {
            "tracer": Mock(),
            "environment": "test",
            "application_name": "test-app",
            "pricing_info": {},
            "capture_message_content": True,
            "metrics_dict": {},
            "disable_metrics": False
        }
        instrumentor._instrument(**config)
        
        # Then uninstrument
        instrumentor._uninstrument()
        
        # Orchestrator should be removed
        orchestrator = instrumentor.get_orchestrator()
        assert orchestrator is None


class TestOpenCogUtils:
    """Test OpenCog utility functions"""
    
    def test_validate_workflow_definition_valid(self):
        """Test workflow validation with valid definition"""
        workflow_def = {
            "name": "test-workflow",
            "steps": [
                {"operation": "chat", "model": "gpt-3.5-turbo"},
                {"operation": "completion", "model": "claude-3"}
            ]
        }
        
        assert validate_workflow_definition(workflow_def) is True
    
    def test_validate_workflow_definition_invalid(self):
        """Test workflow validation with invalid definition"""
        # Missing name
        workflow_def1 = {
            "steps": [{"operation": "chat"}]
        }
        assert validate_workflow_definition(workflow_def1) is False
        
        # Missing steps
        workflow_def2 = {
            "name": "test"
        }
        assert validate_workflow_definition(workflow_def2) is False
        
        # Steps not a list
        workflow_def3 = {
            "name": "test",
            "steps": "not-a-list"
        }
        assert validate_workflow_definition(workflow_def3) is False
    
    def test_estimate_operation_cost(self):
        """Test operation cost estimation"""
        # Basic chat operation
        cost1 = estimate_operation_cost("chat", "gpt-3.5-turbo")
        assert cost1 == 0.002
        
        # More expensive GPT-4
        cost2 = estimate_operation_cost("chat", "gpt-4")
        assert cost2 == 0.02  # 0.002 * 10
        
        # Embedding operation
        cost3 = estimate_operation_cost("embedding", "text-embedding-ada-002")
        assert cost3 == 0.0001
    
    def test_optimize_workflow_execution_order(self):
        """Test workflow execution order optimization"""
        steps = [
            {"operation": "chat", "model": "gpt-4"},  # Expensive
            {"operation": "embedding", "model": "ada"},  # Cheap
            {"operation": "completion", "model": "gpt-3.5"}  # Medium
        ]
        
        optimized_order = optimize_workflow_execution_order(steps)
        
        # Should prioritize cheaper operations first
        # embedding (index 1) should come first
        assert optimized_order[0] == 1


class TestGlobalFunctions:
    """Test global convenience functions"""
    
    def test_orchestrate_llm_call_no_orchestrator(self):
        """Test global orchestrate function when no orchestrator is set"""
        # Ensure no global orchestrator is set
        from openlit.instrumentation.opencog.opencog import set_global_orchestrator
        set_global_orchestrator(None)
        
        result = orchestrate_llm_call("chat", "gpt-3.5-turbo")
        
        assert result["selected_agent"] == "default-agent"
        assert result["confidence"] == 0.1
        assert result["reasoning_method"] == "none"
    
    def test_plan_workflow_no_orchestrator(self):
        """Test global plan_workflow function when no orchestrator is set"""
        from openlit.instrumentation.opencog.opencog import set_global_orchestrator
        set_global_orchestrator(None)
        
        workflow_def = {
            "name": "test",
            "steps": [{"operation": "chat"}]
        }
        
        result = plan_workflow(workflow_def)
        
        assert result["execution_order"] == [0]
        assert result["optimization_applied"] == "none"


class TestIntegrationWithOpenLit:
    """Test integration with OpenLit SDK"""
    
    def test_opencog_in_instrumentor_map(self):
        """Test that OpenCog is properly registered in the instrumentor map"""
        from openlit._instrumentors import MODULE_NAME_MAP, INSTRUMENTOR_MAP
        
        assert "opencog" in MODULE_NAME_MAP
        assert MODULE_NAME_MAP["opencog"] == "hyperon"
        
        assert "opencog" in INSTRUMENTOR_MAP
        assert INSTRUMENTOR_MAP["opencog"] == "openlit.instrumentation.opencog.OpenCogInstrumentor"
    
    @patch('openlit.instrumentation.opencog.opencog.logger')
    def test_opencog_instrumentor_with_openlit_init(self, mock_logger):
        """Test that OpenCog instrumentor works with OpenLit init"""
        # This would be tested in integration, but we can test the basic flow
        from openlit._instrumentors import get_instrumentor_class
        
        # Should be able to get the OpenCog instrumentor class
        opencog_class = get_instrumentor_class("opencog")
        assert opencog_class is not None
        
        # Should be able to instantiate it
        instrumentor = opencog_class()
        assert instrumentor is not None


if __name__ == "__main__":
    pytest.main([__file__])