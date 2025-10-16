#!/usr/bin/env python3
"""
Test script for Gemini API functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.core.gemini_client import create_gemini_client_from_config, GeminiConfig
from backend.core.config import get_settings

def test_gemini_client():
    """Test Gemini client initialization and basic functionality"""
    print("Testing Gemini Client...")
    
    # Get settings
    settings = get_settings()
    print(f"Settings loaded: {type(settings)}")
    
    # Create client
    try:
        gemini_client = create_gemini_client_from_config(settings)
        print(f"Gemini client created: {type(gemini_client)}")
        print(f"Is available: {gemini_client.is_available()}")
        
        if not gemini_client.is_available():
            print("❌ Gemini client is not available")
            return False
            
        # Test basic generation
        print("Testing text generation...")
        test_prompt = "Hello, can you respond with a simple greeting?"
        response = gemini_client.generate_text(test_prompt, temperature=0.7, max_tokens=100)
        
        if response:
            print(f"✅ Gemini response: {response}")
            return True
        else:
            print("❌ No response from Gemini")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting Configuration...")
    
    try:
        settings = get_settings()
        print(f"Settings type: {type(settings)}")
        
        # Check if settings has dict-like access
        if hasattr(settings, 'get'):
            gemini_config = settings.get('llm', {}).get('gemini', {})
        else:
            gemini_config = getattr(settings, 'llm', {}).get('gemini', {})
            
        print(f"Gemini config: {gemini_config}")
        
        api_key = gemini_config.get('api_key')
        if api_key:
            print(f"✅ API key found: {api_key[:10]}...{api_key[-10:]}")
        else:
            print("❌ No API key found in config")
            
        return api_key is not None
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("GEMINI API TEST")
    print("=" * 50)
    
    config_ok = test_config()
    gemini_ok = test_gemini_client()
    
    print("\n" + "=" * 50)
    if config_ok and gemini_ok:
        print("✅ All tests passed - Gemini is working!")
    else:
        print("❌ Some tests failed - Gemini needs fixing")
    print("=" * 50)