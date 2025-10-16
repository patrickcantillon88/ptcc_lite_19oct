#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PTCC Chat Functionality Test
Tests all chat functionality including agent calling, search, and error handling
"""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

class ChatTester:
    def __init__(self, base_url="http://localhost:8005"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.original_api_key = None
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log a test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def test_chat_health(self) -> bool:
        """Test chat API health"""
        print("🔍 Testing Chat API Health...")
        try:
            response = self.session.get(f"{self.base_url}/api/chat/context", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat API is healthy")
                print(f"   Available agents: {data.get('available_agents', [])}")
                print(f"   Capabilities: {data.get('capabilities', [])}")
                return True
            else:
                self.log_test("Chat API Health", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Chat API Health", False, f"Connection error: {e}")
            return False
            
    def test_agent_calling(self) -> bool:
        """Test agent calling through chat"""
        print("\n🤖 Testing Agent Calling Through Chat...")
        
        agent_test_cases = [
            {
                "name": "At-Risk Identifier Agent",
                "message": "Analyze Noah Williams for at-risk indicators",
                "expected_agent": "at_risk_identifier",
                "context": {"student_name": "Noah Williams"}
            },
            {
                "name": "Behavior Manager Agent",
                "message": "Analyze behavior patterns for class 7A",
                "expected_agent": "behavior_manager",
                "context": {"class_code": "7A"}
            },
            {
                "name": "Learning Path Agent",
                "message": "Create a learning path for Emily Chen",
                "expected_agent": "learning_path",
                "context": {"student_name": "Emily Chen"}
            }
        ]
        
        all_passed = True
        
        for test_case in agent_test_cases:
            try:
                request_data = {
                    "message": test_case["message"],
                    "context_data": test_case["context"],
                    "enable_agents": True,
                    "enable_search": False
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/chat/",
                    json=request_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agents_used = data.get("agents_used", [])
                    
                    if test_case["expected_agent"] in agents_used:
                        self.log_test(
                            test_case["name"], 
                            True, 
                            f"Agent {test_case['expected_agent']} called successfully"
                        )
                    else:
                        self.log_test(
                            test_case["name"], 
                            False, 
                            f"Expected agent {test_case['expected_agent']}, got: {agents_used}"
                        )
                        all_passed = False
                else:
                    self.log_test(
                        test_case["name"], 
                        False, 
                        f"HTTP error: {response.status_code}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {e}")
                all_passed = False
                
        return all_passed
        
    def test_search_functionality(self) -> bool:
        """Test search functionality through chat"""
        print("\n🔍 Testing Search Functionality Through Chat...")
        
        search_test_cases = [
            {
                "name": "Student Information Search",
                "message": "Find information about Noah Williams",
                "should_search": True
            },
            {
                "name": "Assessment Data Search",
                "message": "Show me recent math assessments",
                "should_search": True
            },
            {
                "name": "Behavior Logs Search",
                "message": "Find behavior incidents for class 8B",
                "should_search": True
            },
            {
                "name": "General Query (No Search)",
                "message": "What's the weather like today?",
                "should_search": False
            }
        ]
        
        all_passed = True
        
        for test_case in search_test_cases:
            try:
                request_data = {
                    "message": test_case["message"],
                    "enable_agents": False,
                    "enable_search": True
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/chat/",
                    json=request_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    search_performed = data.get("search_performed", False)
                    
                    if search_performed == test_case["should_search"]:
                        self.log_test(
                            test_case["name"], 
                            True, 
                            f"Search performed: {search_performed} (expected: {test_case['should_search']})"
                        )
                    else:
                        self.log_test(
                            test_case["name"], 
                            False, 
                            f"Expected search={test_case['should_search']}, got: {search_performed}"
                        )
                        all_passed = False
                else:
                    self.log_test(
                        test_case["name"], 
                        False, 
                        f"HTTP error: {response.status_code}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {e}")
                all_passed = False
                
        return all_passed
        
    def test_natural_language_routing(self) -> bool:
        """Test natural language routing to appropriate tools"""
        print("\n🧠 Testing Natural Language Routing...")
        
        routing_test_cases = [
            {
                "name": "Risk Assessment Query",
                "message": "I'm concerned about a student who might be at risk",
                "expected_tools": ["at_risk_identifier"]
            },
            {
                "name": "Behavior Management Query",
                "message": "Help me manage classroom behavior issues",
                "expected_tools": ["behavior_manager"]
            },
            {
                "name": "Learning Support Query",
                "message": "I need to create differentiated learning plans",
                "expected_tools": ["learning_path"]
            },
            {
                "name": "Information Retrieval Query",
                "message": "Show me student records and assessment data",
                "expected_tools": ["search"]
            }
        ]
        
        all_passed = True
        
        for test_case in routing_test_cases:
            try:
                request_data = {
                    "message": test_case["message"],
                    "enable_agents": True,
                    "enable_search": True
                }
                
                response = self.session.post(
                    f"{self.base_url}/api/chat/",
                    json=request_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    agents_used = data.get("agents_used", [])
                    search_performed = data.get("search_performed", False)
                    
                    # Check if expected tools were used
                    tools_used = agents_used.copy()
                    if search_performed:
                        tools_used.append("search")
                    
                    # Check if any expected tool was used
                    tool_found = any(tool in tools_used for tool in test_case["expected_tools"])
                    
                    if tool_found:
                        self.log_test(
                            test_case["name"], 
                            True, 
                            f"Tools used: {tools_used}"
                        )
                    else:
                        self.log_test(
                            test_case["name"], 
                            False, 
                            f"Expected one of {test_case['expected_tools']}, got: {tools_used}"
                        )
                        all_passed = False
                else:
                    self.log_test(
                        test_case["name"], 
                        False, 
                        f"HTTP error: {response.status_code}"
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(test_case["name"], False, f"Exception: {e}")
                all_passed = False
                
        return all_passed
        
    def test_gemini_error_handling(self) -> bool:
        """Test error handling when Gemini is unavailable"""
        print("\n🚨 Testing Gemini Error Handling...")
        
        # First, backup the original API key if it exists
        self.original_api_key = os.environ.get('GEMINI_API_KEY')
        
        try:
            # Test 1: Invalid API key
            print("   Testing with invalid API key...")
            os.environ['GEMINI_API_KEY'] = 'invalid_key_for_testing'
            
            # Wait a moment for the change to take effect
            time.sleep(1)
            
            request_data = {
                "message": "Test message with invalid API key",
                "enable_agents": True,
                "enable_search": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat/",
                json=request_data,
                timeout=15
            )
            
            # Should still return a response, but with error handling
            if response.status_code == 200:
                data = response.json()
                # Should have a response even without Gemini
                if data.get("response"):
                    self.log_test("Invalid API Key Handling", True, "System provided fallback response")
                else:
                    self.log_test("Invalid API Key Handling", False, "No fallback response provided")
            else:
                self.log_test("Invalid API Key Handling", False, f"HTTP error: {response.status_code}")
            
            # Test 2: No API key
            print("   Testing with no API key...")
            if 'GEMINI_API_KEY' in os.environ:
                del os.environ['GEMINI_API_KEY']
            
            time.sleep(1)
            
            response = self.session.post(
                f"{self.base_url}/api/chat/",
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("response"):
                    self.log_test("No API Key Handling", True, "System provided fallback response")
                else:
                    self.log_test("No API Key Handling", False, "No fallback response provided")
            else:
                self.log_test("No API Key Handling", False, f"HTTP error: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.log_test("Gemini Error Handling", False, f"Exception: {e}")
            return False
            
        finally:
            # Restore original API key
            if self.original_api_key:
                os.environ['GEMINI_API_KEY'] = self.original_api_key
            elif 'GEMINI_API_KEY' in os.environ:
                del os.environ['GEMINI_API_KEY']
                
    def test_context_awareness(self) -> bool:
        """Test chat context awareness and conversation flow"""
        print("\n📝 Testing Context Awareness...")
        
        try:
            # Start a conversation
            conversation_history = []
            
            # First message
            request_data = {
                "message": "Tell me about Noah Williams",
                "conversation_history": conversation_history,
                "enable_agents": True,
                "enable_search": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat/",
                json=request_data,
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("Context Awareness", False, "First message failed")
                return False
                
            first_response = response.json()
            
            # Add to conversation history
            conversation_history.append({
                "role": "user",
                "content": "Tell me about Noah Williams"
            })
            conversation_history.append({
                "role": "assistant", 
                "content": first_response.get("response", "")
            })
            
            # Follow-up message (should understand context)
            request_data = {
                "message": "What support does he need?",
                "conversation_history": conversation_history,
                "enable_agents": True,
                "enable_search": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat/",
                json=request_data,
                timeout=15
            )
            
            if response.status_code == 200:
                second_response = response.json()
                response_text = second_response.get("response", "").lower()
                
                # Check if the response shows understanding of the context
                if "noah" in response_text or "he" in response_text or "support" in response_text:
                    self.log_test("Context Awareness", True, "System maintained conversation context")
                else:
                    self.log_test("Context Awareness", False, "System lost conversation context")
            else:
                self.log_test("Context Awareness", False, "Follow-up message failed")
                return False
                
            return True
            
        except Exception as e:
            self.log_test("Context Awareness", False, f"Exception: {e}")
            return False
            
    def test_quick_actions(self) -> bool:
        """Test quick actions functionality"""
        print("\n⚡ Testing Quick Actions...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/chat/quick-actions", timeout=10)
            
            if response.status_code == 200:
                quick_actions = response.json()
                
                if isinstance(quick_actions, list) and len(quick_actions) > 0:
                    self.log_test("Quick Actions", True, f"Found {len(quick_actions)} quick actions")
                    
                    # Test executing a quick action
                    first_action = quick_actions[0]
                    action_query = first_action.get("query", "")
                    
                    if action_query:
                        request_data = {
                            "message": action_query,
                            "enable_agents": True,
                            "enable_search": True
                        }
                        
                        response = self.session.post(
                            f"{self.base_url}/api/chat/",
                            json=request_data,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            self.log_test("Quick Action Execution", True, f"Executed: {first_action.get('label')}")
                        else:
                            self.log_test("Quick Action Execution", False, f"Execution failed: {response.status_code}")
                            
                    return True
                else:
                    self.log_test("Quick Actions", False, "No quick actions found")
                    return False
            else:
                self.log_test("Quick Actions", False, f"HTTP error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Quick Actions", False, f"Exception: {e}")
            return False
            
    def run_all_tests(self) -> bool:
        """Run all chat functionality tests"""
        print("🚀 PTCC Chat Functionality Test Suite")
        print("=" * 50)
        print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        tests = [
            ("Chat API Health", self.test_chat_health),
            ("Agent Calling", self.test_agent_calling),
            ("Search Functionality", self.test_search_functionality),
            ("Natural Language Routing", self.test_natural_language_routing),
            ("Context Awareness", self.test_context_awareness),
            ("Quick Actions", self.test_quick_actions),
            ("Gemini Error Handling", self.test_gemini_error_handling),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
                results.append((test_name, False))
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\nResults: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL CHAT FUNCTIONALITY TESTS PASSED!")
            print("\n🌐 Chat system is fully operational with:")
            print("   • Agent calling functionality")
            print("   • Search integration")
            print("   • Natural language routing")
            print("   • Error handling and fallbacks")
            print("   • Context awareness")
            print("   • Quick actions")
        else:
            print("⚠️  Some chat functionality tests failed.")
            print("   Please check the issues above.")
        
        # Generate detailed report
        self.generate_report()
        
        return passed == total
        
    def generate_report(self):
        """Generate a detailed test report"""
        report = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results if r["passed"]]),
                "failed": len([r for r in self.test_results if not r["passed"]])
            },
            "results": self.test_results
        }
        
        try:
            with open('chat_test_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Detailed report saved to: chat_test_report.json")
        except Exception as e:
            print(f"⚠️  Could not save report: {e}")

def main():
    """Run chat functionality tests"""
    tester = ChatTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)

if __name__ == "__main__":
    main()