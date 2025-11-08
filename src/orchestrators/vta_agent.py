"""
VTA Conversational Agent using LangChain.
Combines LLM, tools, and conversation memory for interactive assistance.
"""
import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

from src.orchestrators.llm_setup import create_llm_manager, LLMManager
from src.orchestrators.conversation_chain import create_conversation_chain, VTAConversationChain
from src.orchestrators.vta_tools import get_vta_tools


class VTAAgent:
    """
    Conversational agent for Virtual Testing Assistant.
    
    This agent:
    - Understands natural language queries
    - Determines when to use tools
    - Manages conversation context
    - Provides intelligent responses
    """
    
    def __init__(
        self,
        llm_manager: Optional[LLMManager] = None,
        use_mock: Optional[bool] = None
    ):
        """
        Initialize VTA agent.
        Reads LLM configuration from .env file via settings.
        
        Args:
            llm_manager: Optional LLM manager (creates default if None)
            use_mock: Use mock LLM for testing. If None, reads from settings.
        """
        # Initialize LLM (will read from settings if use_mock is None)
        if llm_manager is None:
            llm_manager = create_llm_manager(use_mock=use_mock)
        
        self.llm_manager = llm_manager
        self.llm = llm_manager.get_llm()
        
        # Initialize conversation chain
        self.conversation_chain = create_conversation_chain(self.llm)
        
        # Initialize tools
        self.tools = get_vta_tools()
        self.tool_map = {tool.name: tool for tool in self.tools}
        
        logger.info(f"VTA Agent initialized with {len(self.tools)} tools")
    
    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            user_input: User's natural language query
            
        Returns:
            Dictionary with response, tool_used, and metadata
        """
        try:
            # Detect if a tool should be used
            tool_name, tool_params = self._detect_tool_usage(user_input)
            
            if tool_name and tool_name in self.tool_map:
                # Use tool
                logger.info(f"Using tool: {tool_name} with params: {tool_params}")
                tool_response = self._execute_tool(tool_name, tool_params)
                
                # Generate conversational response
                response = self.conversation_chain.predict(user_input)
                
                return {
                    "response": tool_response,
                    "conversational_response": response,
                    "tool_used": tool_name,
                    "tool_params": tool_params,
                    "status": "success"
                }
            else:
                # Just conversation
                response = self.conversation_chain.predict(user_input)
                
                return {
                    "response": response,
                    "conversational_response": response,
                    "tool_used": None,
                    "tool_params": {},
                    "status": "success"
                }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "conversational_response": None,
                "tool_used": None,
                "tool_params": {},
                "status": "error",
                "error": str(e)
            }
    
    def _detect_tool_usage(self, user_input: str) -> tuple:
        """
        Detect if a tool should be used based on user input.
        
        Args:
            user_input: User's query
            
        Returns:
            Tuple of (tool_name, tool_params)
        """
        user_lower = user_input.lower()
        
        # Recommendation tool - Enhanced detection
        if any(word in user_lower for word in [
            'recommend', 'suggestion', 'test for', 'should i test', 
            'which test', 'what test', 'validate', 'tests for', 
            'test scenarios', 'battery safety', 'unece', 'standard'
        ]):
            # Try to extract parameters
            params = {}
            
            # Vehicle models
            models = ['ariya', 'leaf', 'qashqai', 'x-trail', 'juke', 'micra']
            for model in models:
                if model in user_lower:
                    params['vehicle_model'] = model.capitalize()
                    break
            
            # Platforms
            if 'ev' in user_lower or 'electric' in user_lower:
                params['platform'] = 'EV'
            elif 'hev' in user_lower or 'hybrid' in user_lower:
                params['platform'] = 'HEV'
            elif 'ice' in user_lower or 'combustion' in user_lower:
                params['platform'] = 'ICE'
            
            # Systems
            systems = []
            if 'battery' in user_lower:
                systems.append('Battery')
            if 'powertrain' in user_lower or 'motor' in user_lower:
                systems.append('Powertrain')
            if 'adas' in user_lower:
                systems.append('ADAS')
            if 'chassis' in user_lower:
                systems.append('Chassis')
            if 'thermal' in user_lower:
                systems.append('Thermal')
            if 'safety' in user_lower:
                systems.append('Safety')
            
            if systems:
                params['systems'] = ','.join(systems)
            
            # Extract standards (e.g., UNECE R100)
            import re
            standards = re.findall(r'(UNECE\s*R?\d+|ISO\s*\d+|SAE\s*[A-Z]\d+)', user_input, re.IGNORECASE)
            if standards:
                params['standards'] = standards
            
            # Defaults
            if 'vehicle_model' not in params:
                params['vehicle_model'] = 'Ariya'
            if 'platform' not in params:
                params['platform'] = 'EV'
            if 'systems' not in params:
                params['systems'] = 'Battery,Powertrain'
            
            params['top_k'] = 5
            
            return ('get_recommendations', params)
        
        # ROI tool
        elif any(word in user_lower for word in ['roi', 'cost', 'saving', 'payback', 'return on investment']):
            params = {
                'baseline_count': 100,
                'optimization_rate': 0.25
            }
            
            # Try to extract numbers
            numbers = re.findall(r'\d+', user_input)
            if numbers:
                params['baseline_count'] = int(numbers[0])
            
            return ('calculate_roi', params)
        
        # Metrics tool
        elif any(word in user_lower for word in ['metric', 'performance', 'coverage', 'efficiency', 'quality']):
            params = {
                'num_scenarios': 50
            }
            
            return ('get_metrics', params)
        
        # Search tool
        elif any(word in user_lower for word in ['search', 'find', 'list', 'show', 'browse']):
            params = {
                'limit': 10
            }
            
            # Platform filter
            if 'ev' in user_lower:
                params['platform'] = 'EV'
            elif 'hev' in user_lower:
                params['platform'] = 'HEV'
            elif 'ice' in user_lower:
                params['platform'] = 'ICE'
            
            # Test type filter
            test_types = ['performance', 'durability', 'safety', 'regulatory', 'adas', 'emissions']
            for test_type in test_types:
                if test_type in user_lower:
                    params['test_type'] = test_type
                    break
            
            return ('search_scenarios', params)
        
        return (None, {})
    
    def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool
            params: Tool parameters
            
        Returns:
            Tool response as string
        """
        try:
            tool = self.tool_map[tool_name]
            
            # Handle standards filter for recommendation tool
            if tool_name == 'get_recommendations' and 'standards' in params:
                # Store standards filter for the tool to use
                tool._standards_filter = params.pop('standards', [])
            
            return tool._run(**params)
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool: {str(e)}"
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names."""
        return list(self.tool_map.keys())
    
    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_chain.reset()
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information."""
        return {
            "llm_info": self.llm_manager.get_model_info(),
            "num_tools": len(self.tools),
            "available_tools": self.get_available_tools(),
            "conversation_turns": len(self.conversation_chain.memory.history)
        }


def create_vta_agent(use_mock: Optional[bool] = None) -> VTAAgent:
    """
    Create a VTA agent instance.
    Reads LLM configuration from .env file via settings.
    
    Args:
        use_mock: Use mock LLM for testing. If None, reads from settings.
        
    Returns:
        VTAAgent instance
    """
    return VTAAgent(use_mock=use_mock)


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("VTA AGENT TEST")
    print("=" * 70)
    
    # Create agent
    print("\n[1/4] Creating VTA agent...")
    agent = create_vta_agent(use_mock=True)
    print("[OK] Agent created")
    
    # Show status
    print("\n[2/4] Agent status:")
    status = agent.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test queries
    print("\n[3/4] Testing agent with queries...")
    
    test_queries = [
        "Hello, what can you help me with?",
        "I need test recommendations for Ariya EV battery and powertrain",
        "What's the ROI for optimizing 100 tests?",
        "Show me the current metrics",
        "List some EV performance tests"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i} ---")
        print(f"User: {query}")
        
        result = agent.process_query(query)
        
        print(f"Tool Used: {result['tool_used']}")
        print(f"Response:\n{result['response'][:300]}...")
        
        if result['status'] == 'error':
            print(f"Error: {result.get('error')}")
    
    # Final status
    print("\n[4/4] Final agent status:")
    status = agent.get_status()
    print(f"Conversation turns: {status['conversation_turns']}")
    
    print("\n[OK] VTA agent test complete")

