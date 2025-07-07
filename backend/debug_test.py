#!/usr/bin/env python3
"""
Debug test script to isolate the issue
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_environment():
    """Test if environment variables are loaded correctly"""
    logger.debug("🔍 Testing environment variables...")
    
    load_dotenv()
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_CHAT_DEPLOYMENT_NAME',
        'AZURE_OPENAI_API_VERSION',
        'AZURE_OPENAI_API_KEY',
        'SHOPIFY_SHOP_NAME',
        'SHOPIFY_API_VERSION',
        'SHOPIFY_ACCESS_TOKEN'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            logger.debug(f"✅ {var}: {value[:10]}..." if len(value) > 10 else f"✅ {var}: {value}")
        else:
            logger.error(f"❌ {var}: NOT SET")
    
    return all(os.getenv(var) for var in required_vars)

def test_imports():
    """Test if all imports work correctly"""
    logger.debug("🔍 Testing imports...")
    
    try:
        from langchain.agents import initialize_agent, Tool
        logger.debug("✅ langchain.agents imported")
    except ImportError as e:
        logger.error(f"❌ Failed to import langchain.agents: {e}")
        return False
    
    try:
        from langchain_openai import AzureChatOpenAI
        logger.debug("✅ langchain_openai imported")
    except ImportError as e:
        logger.error(f"❌ Failed to import langchain_openai: {e}")
        return False
    
    try:
        from langchain_experimental.tools.python.tool import PythonAstREPLTool
        logger.debug("✅ langchain_experimental imported")
    except ImportError as e:
        logger.error(f"❌ Failed to import langchain_experimental: {e}")
        return False
    
    try:
        from shopify_tool import get_shopify_data
        logger.debug("✅ shopify_tool imported")
    except ImportError as e:
        logger.error(f"❌ Failed to import shopify_tool: {e}")
        return False
    
    return True

def test_azure_openai():
    """Test Azure OpenAI connection"""
    logger.debug("🔍 Testing Azure OpenAI connection...")
    
    try:
        from langchain_openai import AzureChatOpenAI
        
        llm = AzureChatOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        response = llm.invoke("Hello, this is a test message.")
        logger.debug(f"✅ Azure OpenAI response: {response}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Azure OpenAI test failed: {e}")
        return False

def test_shopify_tool():
    """Test Shopify tool directly"""
    logger.debug("🔍 Testing Shopify tool...")
    
    try:
        from shopify_tool import get_shopify_data
        
        # Test with simple parameters
        result = get_shopify_data("orders", {"limit": 1})
        logger.debug(f"✅ Shopify tool result type: {type(result)}")
        logger.debug(f"✅ Shopify tool result length: {len(result) if isinstance(result, list) else 'N/A'}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Shopify tool test failed: {e}")
        return False

def test_tool_wrapper():
    """Test the Shopify tool wrapper"""
    logger.debug("🔍 Testing Shopify tool wrapper...")
    
    try:
        from agent import get_shopify_data_tool
        
        # Test different input formats
        test_inputs = [
            {"resource": "orders"},
            '{"resource": "orders"}',
            "orders",
            {"resource": "products", "params": {"limit": 1}}
        ]
        
        for i, test_input in enumerate(test_inputs):
            logger.debug(f"🧪 Test {i+1}: {test_input}")
            result = get_shopify_data_tool(test_input)
            logger.debug(f"✅ Result type: {type(result)}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Tool wrapper test failed: {e}")
        return False

def test_agent_creation():
    """Test agent creation"""
    logger.debug("🔍 Testing agent creation...")
    
    try:
        from agent import agent
        logger.debug("✅ Agent created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent creation failed: {e}")
        return False

def test_simple_agent_call():
    """Test a simple agent call"""
    logger.debug("🔍 Testing simple agent call...")
    
    try:
        from agent import run_agent
        
        result = run_agent("Get me 1 order from the store")
        logger.debug(f"✅ Agent call result: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent call failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.debug("🚀 Starting comprehensive debugging...")
    
    tests = [
        ("Environment Variables", test_environment),
        ("Imports", test_imports),
        ("Azure OpenAI", test_azure_openai),
        ("Shopify Tool", test_shopify_tool),
        ("Tool Wrapper", test_tool_wrapper),
        ("Agent Creation", test_agent_creation),
        ("Simple Agent Call", test_simple_agent_call)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.debug(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    logger.debug(f"\n{'='*50}")
    logger.debug("📊 TEST RESULTS:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        logger.debug(f"{status}: {test_name}")
    
    failed_tests = [name for name, passed in results.items() if not passed]
    if failed_tests:
        logger.error(f"\n❌ Failed tests: {', '.join(failed_tests)}")
        return 1
    else:
        logger.debug("\n🎉 All tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())