# Test Strategy Planner
from llama_cpp import Llama
import json
from typing import Dict, List
from pathlib import Path

class TestPlanner:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_gpu_layers: int = 0):
        print(f"Loading LLaMA 3 model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=4,  # Use 4 CPU threads
            verbose=False
        )
        print("✓ Model loaded successfully")
        
        # Load prompts
        prompts_dir = Path(__file__).parent.parent / "prompts"
        with open(prompts_dir / "ui_analysis.txt", "r", encoding="utf-8") as f:
            self.ui_analysis_prompt = f.read()
        with open(prompts_dir / "test_generation.txt", "r", encoding="utf-8") as f:
            self.test_generation_prompt = f.read()
    
    def analyze_page(self, page_info: Dict) -> Dict:
        """Phân tích trang web và xác định mục đích"""
        # Limit data sent to LLM
        dom_structure = page_info.get("dom_structure", "")[:800]  # Reduced from 1000
        visible_text = page_info.get("visible_text", "")[:300]    # Reduced from 500
        elements = str(page_info.get("interactive_elements", []))[:800]  # Reduced from 1000
        
        prompt = self.ui_analysis_prompt.format(
            url=page_info.get("url", ""),
            title=page_info.get("title", ""),
            dom_structure=dom_structure,
            visible_text=visible_text,
            interactive_elements=elements
        )
        
        print("   Sending to LLM for analysis...")
        response = self._generate(prompt, max_tokens=512)  # Reduced from 1024
        print("   Parsing LLM response...")
        return self._parse_json_response(response)
    
    def generate_test_cases(self, page_analysis: Dict, elements: List[Dict]) -> List[Dict]:
        """Sinh test cases dựa trên phân tích"""
        # If page analysis failed, generate basic tests from elements
        if page_analysis.get("error"):
            print("⚠️ Page analysis failed, generating basic tests from elements...")
            return self._generate_basic_tests(elements)
        
        prompt = self.test_generation_prompt.format(
            page_analysis=json.dumps(page_analysis, indent=2),
            elements=json.dumps(elements[:20], indent=2)
        )
        
        response = self._generate(prompt)
        result = self._parse_json_response(response)
        
        test_cases = result.get("test_cases", [])
        
        # If no test cases generated, create basic ones
        if not test_cases:
            print("⚠️ No test cases from LLM, generating basic tests...")
            return self._generate_basic_tests(elements)
        
        return test_cases
    
    def _generate_basic_tests(self, elements: List[Dict]) -> List[Dict]:
        """Generate basic test cases from elements when LLM fails"""
        test_cases = []
        
        # Find buttons
        buttons = [e for e in elements if e.get('tag') == 'button' or e.get('type') == 'submit']
        if buttons:
            for i, btn in enumerate(buttons[:3], 1):
                selector = f"button:nth-of-type({i})"
                if btn.get('id'):
                    selector = f"#{btn['id']}"
                
                test_cases.append({
                    "name": f"Test click button: {btn.get('text', 'Button')[:30]}",
                    "priority": "high",
                    "steps": [
                        {
                            "action": "click",
                            "selector": selector,
                            "expected": "page response"
                        },
                        {
                            "action": "wait",
                            "value": "2"
                        }
                    ]
                })
        
        # Find inputs
        inputs = [e for e in elements if e.get('tag') == 'input' and e.get('type') in ['text', 'email', 'password']]
        if inputs:
            for i, inp in enumerate(inputs[:2], 1):
                selector = f"input[type='{inp.get('type')}']:nth-of-type({i})"
                if inp.get('id'):
                    selector = f"#{inp['id']}"
                elif inp.get('name'):
                    selector = f"input[name='{inp['name']}']"
                
                test_cases.append({
                    "name": f"Test input field: {inp.get('type', 'text')}",
                    "priority": "medium",
                    "steps": [
                        {
                            "action": "type",
                            "selector": selector,
                            "value": "Test input",
                            "expected": "input accepted"
                        }
                    ]
                })
        
        # Find links
        links = [e for e in elements if e.get('tag') == 'a']
        if links and len(test_cases) < 5:
            link = links[0]
            test_cases.append({
                "name": f"Test link: {link.get('text', 'Link')[:30]}",
                "priority": "low",
                "steps": [
                    {
                        "action": "click",
                        "selector": "a:first-of-type",
                        "expected": "navigation"
                    }
                ]
            })
        
        return test_cases if test_cases else [
            {
                "name": "Basic page load test",
                "priority": "high",
                "steps": [
                    {
                        "action": "wait",
                        "value": "2",
                        "expected": "page loaded"
                    }
                ]
            }
        ]
    
    def _generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response from LLaMA"""
        full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are an expert QA automation engineer. You MUST respond with ONLY valid JSON, no markdown, no explanation, no code blocks.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}

IMPORTANT: Return ONLY the JSON object, starting with {{ and ending with }}. Do not include markdown code blocks or any other text.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""
        
        output = self.llm(
            full_prompt,
            max_tokens=max_tokens,
            temperature=0.3,  # Lower temperature for more focused output
            top_p=0.9,
            top_k=40,
            repeat_penalty=1.1,
            stop=["<|eot_id|>", "\n\n\n"],
            echo=False
        )
        
        response = output["choices"][0]["text"].strip()
        
        # Ensure response starts with { if not already
        if not response.startswith("{"):
            response = "{" + response
        
        return response
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from LLM response"""
        try:
            # Remove markdown code blocks if present
            response = response.replace("```json", "").replace("```", "")
            
            # Try to find JSON in response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                
                # Try to parse
                parsed = json.loads(json_str)
                return parsed
                
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse error: {e}")
            print(f"Response preview: {response[:200]}...")
            
            # Try to extract key information manually
            try:
                return self._fallback_parse(response)
            except:
                pass
        
        return {"error": "Failed to parse response", "raw": response[:500]}
    
    def _fallback_parse(self, response: str) -> Dict:
        """Fallback parser when JSON parsing fails"""
        # Extract page_type
        page_type = "other"
        if "login" in response.lower():
            page_type = "login"
        elif "form" in response.lower():
            page_type = "form"
        elif "search" in response.lower():
            page_type = "search"
        
        return {
            "page_type": page_type,
            "main_purpose": "Interactive web page",
            "user_actions": ["Click buttons", "Navigate"],
            "test_scenarios": [
                {
                    "name": "Basic interaction test",
                    "priority": "high",
                    "steps": ["Click interactive elements", "Verify page response"]
                }
            ]
        }
