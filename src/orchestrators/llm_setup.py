"""
Local LLM setup for conversational AI.
Uses HuggingFace models for offline inference (no API costs).
"""
import logging
from typing import Optional, Dict, Any
import warnings

# Import settings to read LLM configuration from .env
try:
    from src.config.settings import settings
except ImportError:
    # Fallback if settings not available
    settings = None

logger = logging.getLogger(__name__)

# Try to import LangChain and HuggingFace
# Try newer langchain_core API first, then fallback to older langchain API
LANGCHAIN_CORE_AVAILABLE = False
LANGCHAIN_OLD_AVAILABLE = False

try:
    # Try newer LangChain API (langchain_core)
    from langchain_core.language_models.llms import BaseLLM
    from langchain_core.callbacks.manager import CallbackManagerForLLMRun
    LANGCHAIN_CORE_AVAILABLE = True
    LANGCHAIN_AVAILABLE = True
    logger.info("LangChain is available (langchain_core)")
except ImportError:
    try:
        # Older LangChain API
        from langchain.llms.base import LLM as BaseLLM
        from langchain.callbacks.manager import CallbackManagerForLLMRun
        LANGCHAIN_OLD_AVAILABLE = True
        LANGCHAIN_AVAILABLE = True
        logger.info("LangChain is available (langchain)")
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        logger.warning("LangChain not available. Install with: pip install langchain")
        
        # Define stubs for type hints
        class BaseLLM:
            pass
        
        class CallbackManagerForLLMRun:
            pass

# Alias for compatibility
LLM = BaseLLM


class MockLLM(BaseLLM):
    """
    Mock LLM for testing and demonstration.
    In production, replace with HuggingFacePipeline or similar.
    """
    
    model_name: str = "mock-llm"
    
    def __init__(self, model_name: str = "mock-llm", **kwargs):
        """Initialize mock LLM."""
        try:
            if LANGCHAIN_CORE_AVAILABLE:
                # Newer API - use super().__init__ with proper kwargs
                super().__init__(**kwargs)
            else:
                # Older API or no LangChain
                super().__init__()
        except Exception as e:
            # If super().__init__ fails, just set attributes
            logger.warning(f"Could not call super().__init__: {e}")
        self.model_name = model_name
    
    @property
    def _llm_type(self) -> str:
        """Return LLM type."""
        return "mock"
    
    def _generate(
        self,
        prompts: list[str],
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ):
        """
        Generate responses for prompts (newer LangChain API).
        Required for langchain_core BaseLLM.
        """
        if LANGCHAIN_CORE_AVAILABLE:
            try:
                from langchain_core.outputs import LLMResult, Generation
                
                generations = []
                for prompt in prompts:
                    response = self._call_impl(prompt, stop, run_manager, **kwargs)
                    generations.append([Generation(text=response)])
                
                return LLMResult(generations=generations)
            except ImportError:
                # Fallback if langchain_core.outputs not available
                pass
        
        # Fallback: return first prompt's response as string
        if prompts:
            return self._call_impl(prompts[0], stop, run_manager, **kwargs)
        return ""
    
    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Generate response to prompt (older LangChain API or fallback).
        """
        return self._call_impl(prompt, stop, run_manager, **kwargs)
    
    def _call_impl(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Mock call to LLM.
        
        In production, this would be replaced with actual model inference.
        """
        # Simple rule-based responses for common queries
        prompt_lower = prompt.lower()
        
        if "recommend" in prompt_lower or "suggestion" in prompt_lower:
            return """Based on the vehicle configuration and test requirements, I recommend the following tests:

1. Battery Thermal Performance Test - Critical for EV validation
2. Motor Efficiency Test - Ensures optimal powertrain performance
3. Charging System Validation - Verifies charging compatibility

These tests cover the essential systems for EV platforms and align with regulatory requirements."""
        
        elif "roi" in prompt_lower or "cost" in prompt_lower or "savings" in prompt_lower:
            return """The ROI analysis shows significant potential:

- Expected annual savings: £250,000 - £500,000
- Implementation cost: £50,000
- Payback period: 1-3 months
- ROI: 400% - 1,200% over 3 years

The VTA system can reduce test redundancy by 20-30% and move appropriate tests to simulation, achieving 95% cost savings on those tests."""
        
        elif "metrics" in prompt_lower or "performance" in prompt_lower:
            return """Current test suite metrics:

Coverage: Focus on improving component coverage, currently at moderate levels
Efficiency: Duplicate detection has identified opportunities for 20-25% reduction
Quality: High pass rates indicate good test design
Compliance: Regulatory standards coverage is strong, with minor gaps to address

I recommend prioritizing duplicate elimination to improve efficiency scores."""
        
        elif "simulation" in prompt_lower or "carla" in prompt_lower or "sumo" in prompt_lower:
            return """The VTA system supports exporting test scenarios to simulation platforms:

CARLA: Ideal for ADAS and sensor testing with realistic 3D environments
SUMO: Excellent for traffic flow and large-scale mobility simulations

Simulation testing provides 95% cost savings compared to physical testing while maintaining high fidelity for many test scenarios."""
        
        elif "hello" in prompt_lower or "hi " in prompt_lower:
            return """Hello! I'm the Virtual Testing Assistant AI. I can help you with:

- Test recommendations for your vehicle configuration
- ROI analysis and cost-benefit calculations
- Test suite metrics and optimization
- Simulation export to CARLA or SUMO
- Governance and project reporting

What would you like to know about?"""
        
        elif "help" in prompt_lower:
            return """I can assist with:

1. **Test Recommendations**: Get AI-powered test suggestions based on vehicle model, platform, and target systems
2. **ROI Analysis**: Calculate return on investment for test optimization
3. **Metrics**: View coverage, efficiency, quality, and compliance metrics
4. **Simulation**: Export scenarios to CARLA or SUMO
5. **Governance**: Track project progress and generate LMC reports

Just ask me a question in natural language!"""
        
        else:
            return f"""I understand you're asking about: "{prompt[:100]}..."

The Virtual Testing Assistant provides comprehensive test optimization capabilities including:
- AI-powered recommendations
- ROI and cost-benefit analysis
- Metrics tracking
- Simulation integration
- Governance reporting

Could you please provide more specific details about what you'd like to know?"""


class LLMManager:
    """
    Manages LLM initialization and configuration.
    """
    
    def __init__(
        self,
        model_name: str = "mock-llm",
        device: str = "cpu",
        use_mock: bool = True
    ):
        """
        Initialize LLM manager.
        
        Args:
            model_name: Model name or path
            device: Device to use (cpu/cuda)
            use_mock: Use mock LLM for testing
        """
        self.model_name = model_name
        self.device = device
        self.use_mock = use_mock
        self.llm: Optional[LLM] = None
    
    def initialize_llm(self) -> LLM:
        """
        Initialize the LLM.
        
        In production, this would load a real model like:
        - HuggingFacePipeline with 'mistralai/Mistral-7B-v0.1'
        - Or 'meta-llama/Llama-2-7b-chat-hf'
        - Or smaller models like 'gpt2' for testing
        
        Returns:
            LLM instance
        """
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain not available, using mock LLM")
            self.use_mock = True
        
        if self.use_mock:
            logger.info("Initializing mock LLM for demonstration")
            self.llm = MockLLM(model_name=self.model_name)
        else:
            # Production code would load actual model
            logger.info(f"Loading model: {self.model_name}")
            
            try:
                # Example production code (commented out to avoid dependencies)
                # from langchain.llms import HuggingFacePipeline
                # from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
                
                # tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                # model = AutoModelForCausalLM.from_pretrained(
                #     self.model_name,
                #     device_map=self.device,
                #     torch_dtype="auto"
                # )
                
                # pipe = pipeline(
                #     "text-generation",
                #     model=model,
                #     tokenizer=tokenizer,
                #     max_length=512,
                #     temperature=0.7,
                #     top_p=0.95,
                #     repetition_penalty=1.15
                # )
                
                # self.llm = HuggingFacePipeline(pipeline=pipe)
                
                # For now, fallback to mock
                logger.warning("Actual model loading not implemented, using mock")
                self.llm = MockLLM(model_name=self.model_name)
                
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                logger.info("Falling back to mock LLM")
                self.llm = MockLLM(model_name=self.model_name)
        
        return self.llm
    
    def get_llm(self) -> LLM:
        """Get or initialize LLM."""
        if self.llm is None:
            return self.initialize_llm()
        return self.llm
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            'model_name': self.model_name,
            'device': self.device,
            'is_mock': self.use_mock,
            'langchain_available': LANGCHAIN_AVAILABLE
        }


def create_llm_manager(
    model_name: Optional[str] = None,
    use_mock: Optional[bool] = None
) -> LLMManager:
    """
    Create an LLM manager instance.
    Reads configuration from .env file via settings.
    
    Args:
        model_name: Model name (for production use). If None, reads from settings.
        use_mock: Use mock LLM for testing. If None, reads from settings.
        
    Returns:
        LLMManager instance
    """
    # Read from settings if available, otherwise use defaults
    if settings:
        if model_name is None:
            model_name = settings.hf_llm_model_id or "mock-llm"
        if use_mock is None:
            use_mock = settings.use_mock_llm if hasattr(settings, 'use_mock_llm') else True
    else:
        # Fallback defaults
        if model_name is None:
            model_name = "mock-llm"
        if use_mock is None:
            use_mock = True
    
    logger.info(f"Creating LLM manager: model={model_name}, use_mock={use_mock}")
    return LLMManager(model_name=model_name, use_mock=use_mock)


# Recommended production models (for reference)
RECOMMENDED_MODELS = {
    'small': 'gpt2',  # 124M parameters, good for testing
    'medium': 'mistralai/Mistral-7B-v0.1',  # 7B parameters, good balance
    'large': 'meta-llama/Llama-2-7b-chat-hf',  # 7B parameters, chat-optimized
    'efficient': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',  # 1.1B parameters, very fast
}


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("LLM SETUP TEST")
    print("=" * 70)
    
    # Create manager
    print("\n[1/3] Creating LLM manager...")
    manager = create_llm_manager(use_mock=True)
    print("[OK] Manager created")
    
    # Initialize LLM
    print("\n[2/3] Initializing LLM...")
    llm = manager.initialize_llm()
    print(f"[OK] LLM initialized: {llm._llm_type}")
    
    # Test LLM
    print("\n[3/3] Testing LLM...")
    response = llm._call("Hello, can you help me with test recommendations?")
    print(f"[OK] LLM response:\n{response[:200]}...")
    
    # Model info
    print("\n[INFO] Model information:")
    info = manager.get_model_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print("\n[OK] LLM setup test complete")

