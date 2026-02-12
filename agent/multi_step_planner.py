"""
Multi-step Planning System
Lập kế hoạch test phức tạp với nhiều bước phụ thuộc
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class StepType(Enum):
    """Loại bước trong test plan"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    WAIT = "wait"
    VERIFY = "verify"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"


class StepStatus(Enum):
    """Trạng thái của bước"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestStep:
    """Một bước trong test plan"""
    id: str
    name: str
    type: StepType
    action: str
    selector: Optional[str] = None
    value: Optional[str] = None
    expected: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)  # IDs của steps phụ thuộc
    status: StepStatus = StepStatus.PENDING
    result: Optional[Dict] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def can_execute(self, completed_steps: Set[str]) -> bool:
        """Kiểm tra xem step có thể execute không"""
        if self.status != StepStatus.PENDING:
            return False
        
        # Check all dependencies are completed
        for dep_id in self.depends_on:
            if dep_id not in completed_steps:
                return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "action": self.action,
            "selector": self.selector,
            "value": self.value,
            "expected": self.expected,
            "depends_on": self.depends_on,
            "status": self.status.value,
            "result": self.result,
            "retry_count": self.retry_count
        }


@dataclass
class TestPlan:
    """Test plan với nhiều steps phụ thuộc"""
    id: str
    name: str
    description: str
    steps: List[TestStep] = field(default_factory=list)
    priority: str = "medium"
    tags: List[str] = field(default_factory=list)
    
    def add_step(self, step: TestStep):
        """Thêm step vào plan"""
        self.steps.append(step)
    
    def get_executable_steps(self, completed_steps: Set[str]) -> List[TestStep]:
        """Lấy các steps có thể execute"""
        return [
            step for step in self.steps
            if step.can_execute(completed_steps)
        ]
    
    def get_step_by_id(self, step_id: str) -> Optional[TestStep]:
        """Lấy step theo ID"""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def is_complete(self) -> bool:
        """Kiểm tra plan đã hoàn thành chưa"""
        return all(
            step.status in [StepStatus.SUCCESS, StepStatus.SKIPPED]
            for step in self.steps
        )
    
    def has_failed(self) -> bool:
        """Kiểm tra plan có bước nào fail không"""
        return any(step.status == StepStatus.FAILED for step in self.steps)
    
    def get_progress(self) -> Dict:
        """Lấy tiến độ thực hiện"""
        total = len(self.steps)
        completed = sum(1 for s in self.steps if s.status == StepStatus.SUCCESS)
        failed = sum(1 for s in self.steps if s.status == StepStatus.FAILED)
        pending = sum(1 for s in self.steps if s.status == StepStatus.PENDING)
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "progress": f"{completed}/{total}",
            "percentage": (completed / total * 100) if total > 0 else 0
        }
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "tags": self.tags,
            "steps": [step.to_dict() for step in self.steps],
            "progress": self.get_progress()
        }


class MultiStepPlanner:
    """
    Multi-step Planning System
    Tạo và quản lý test plans phức tạp
    """
    
    def __init__(self):
        self.plans: List[TestPlan] = []
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load test plan templates"""
        return {
            "login_flow": {
                "name": "Complete Login Flow",
                "description": "Test full login workflow with validation",
                "steps": [
                    {
                        "id": "step1",
                        "name": "Navigate to login page",
                        "type": "navigate",
                        "action": "navigate",
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "name": "Enter username",
                        "type": "type",
                        "action": "type",
                        "selector": "#username",
                        "value": "testuser",
                        "depends_on": ["step1"]
                    },
                    {
                        "id": "step3",
                        "name": "Enter password",
                        "type": "type",
                        "action": "type",
                        "selector": "#password",
                        "value": "testpass",
                        "depends_on": ["step2"]
                    },
                    {
                        "id": "step4",
                        "name": "Click login button",
                        "type": "click",
                        "action": "click",
                        "selector": "#login-btn",
                        "depends_on": ["step3"]
                    },
                    {
                        "id": "step5",
                        "name": "Verify login success",
                        "type": "verify",
                        "action": "verify",
                        "expected": "dashboard",
                        "depends_on": ["step4"]
                    }
                ]
            },
            "form_submission": {
                "name": "Form Submission Flow",
                "description": "Test complete form submission with validation",
                "steps": [
                    {
                        "id": "step1",
                        "name": "Fill first name",
                        "type": "type",
                        "action": "type",
                        "selector": "#first-name",
                        "value": "John",
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "name": "Fill last name",
                        "type": "type",
                        "action": "type",
                        "selector": "#last-name",
                        "value": "Doe",
                        "depends_on": []
                    },
                    {
                        "id": "step3",
                        "name": "Fill email",
                        "type": "type",
                        "action": "type",
                        "selector": "#email",
                        "value": "john@example.com",
                        "depends_on": []
                    },
                    {
                        "id": "step4",
                        "name": "Select country",
                        "type": "select",
                        "action": "select",
                        "selector": "#country",
                        "value": "US",
                        "depends_on": []
                    },
                    {
                        "id": "step5",
                        "name": "Submit form",
                        "type": "click",
                        "action": "click",
                        "selector": "#submit",
                        "depends_on": ["step1", "step2", "step3", "step4"]
                    },
                    {
                        "id": "step6",
                        "name": "Verify submission",
                        "type": "verify",
                        "action": "verify",
                        "expected": "success message",
                        "depends_on": ["step5"]
                    }
                ]
            },
            "search_flow": {
                "name": "Search and Filter Flow",
                "description": "Test search with filters and pagination",
                "steps": [
                    {
                        "id": "step1",
                        "name": "Enter search query",
                        "type": "type",
                        "action": "type",
                        "selector": "#search-input",
                        "value": "test query",
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "name": "Click search button",
                        "type": "click",
                        "action": "click",
                        "selector": "#search-btn",
                        "depends_on": ["step1"]
                    },
                    {
                        "id": "step3",
                        "name": "Wait for results",
                        "type": "wait",
                        "action": "wait",
                        "value": "2",
                        "depends_on": ["step2"]
                    },
                    {
                        "id": "step4",
                        "name": "Apply filter",
                        "type": "click",
                        "action": "click",
                        "selector": "#filter-option",
                        "depends_on": ["step3"]
                    },
                    {
                        "id": "step5",
                        "name": "Verify filtered results",
                        "type": "verify",
                        "action": "verify",
                        "expected": "filtered items",
                        "depends_on": ["step4"]
                    }
                ]
            },
            "e_commerce_checkout": {
                "name": "E-commerce Checkout Flow",
                "description": "Complete checkout process from cart to payment",
                "steps": [
                    {
                        "id": "step1",
                        "name": "Add item to cart",
                        "type": "click",
                        "action": "click",
                        "selector": ".add-to-cart",
                        "depends_on": []
                    },
                    {
                        "id": "step2",
                        "name": "Go to cart",
                        "type": "click",
                        "action": "click",
                        "selector": "#cart-icon",
                        "depends_on": ["step1"]
                    },
                    {
                        "id": "step3",
                        "name": "Proceed to checkout",
                        "type": "click",
                        "action": "click",
                        "selector": "#checkout-btn",
                        "depends_on": ["step2"]
                    },
                    {
                        "id": "step4",
                        "name": "Fill shipping address",
                        "type": "type",
                        "action": "type",
                        "selector": "#address",
                        "value": "123 Main St",
                        "depends_on": ["step3"]
                    },
                    {
                        "id": "step5",
                        "name": "Select shipping method",
                        "type": "click",
                        "action": "click",
                        "selector": "#standard-shipping",
                        "depends_on": ["step4"]
                    },
                    {
                        "id": "step6",
                        "name": "Continue to payment",
                        "type": "click",
                        "action": "click",
                        "selector": "#continue-payment",
                        "depends_on": ["step5"]
                    },
                    {
                        "id": "step7",
                        "name": "Enter card number",
                        "type": "type",
                        "action": "type",
                        "selector": "#card-number",
                        "value": "4111111111111111",
                        "depends_on": ["step6"]
                    },
                    {
                        "id": "step8",
                        "name": "Complete purchase",
                        "type": "click",
                        "action": "click",
                        "selector": "#complete-purchase",
                        "depends_on": ["step7"]
                    },
                    {
                        "id": "step9",
                        "name": "Verify order confirmation",
                        "type": "verify",
                        "action": "verify",
                        "expected": "order confirmation",
                        "depends_on": ["step8"]
                    }
                ]
            }
        }
    
    def create_plan_from_template(self, template_name: str, plan_id: str) -> Optional[TestPlan]:
        """Tạo plan từ template"""
        if template_name not in self.templates:
            return None
        
        template = self.templates[template_name]
        plan = TestPlan(
            id=plan_id,
            name=template["name"],
            description=template["description"]
        )
        
        for step_data in template["steps"]:
            step = TestStep(
                id=step_data["id"],
                name=step_data["name"],
                type=StepType(step_data["type"]),
                action=step_data["action"],
                selector=step_data.get("selector"),
                value=step_data.get("value"),
                expected=step_data.get("expected"),
                depends_on=step_data.get("depends_on", [])
            )
            plan.add_step(step)
        
        self.plans.append(plan)
        return plan
    
    def create_custom_plan(self, plan_id: str, name: str, description: str, 
                          steps_data: List[Dict]) -> TestPlan:
        """Tạo custom plan"""
        plan = TestPlan(
            id=plan_id,
            name=name,
            description=description
        )
        
        for step_data in steps_data:
            step = TestStep(
                id=step_data["id"],
                name=step_data["name"],
                type=StepType(step_data["type"]),
                action=step_data["action"],
                selector=step_data.get("selector"),
                value=step_data.get("value"),
                expected=step_data.get("expected"),
                depends_on=step_data.get("depends_on", [])
            )
            plan.add_step(step)
        
        self.plans.append(plan)
        return plan
    
    def get_plan(self, plan_id: str) -> Optional[TestPlan]:
        """Lấy plan theo ID"""
        for plan in self.plans:
            if plan.id == plan_id:
                return plan
        return None
    
    def list_templates(self) -> List[str]:
        """List tất cả templates"""
        return list(self.templates.keys())
    
    def save_plan(self, plan: TestPlan, filepath: str):
        """Lưu plan ra file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)
    
    def load_plan(self, filepath: str) -> TestPlan:
        """Load plan từ file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        plan = TestPlan(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            priority=data.get("priority", "medium"),
            tags=data.get("tags", [])
        )
        
        for step_data in data["steps"]:
            step = TestStep(
                id=step_data["id"],
                name=step_data["name"],
                type=StepType(step_data["type"]),
                action=step_data["action"],
                selector=step_data.get("selector"),
                value=step_data.get("value"),
                expected=step_data.get("expected"),
                depends_on=step_data.get("depends_on", []),
                status=StepStatus(step_data.get("status", "pending"))
            )
            plan.add_step(step)
        
        return plan
    
    def visualize_plan(self, plan: TestPlan) -> str:
        """Tạo visualization của plan (text-based)"""
        lines = []
        lines.append(f"\n{'='*60}")
        lines.append(f"📋 Test Plan: {plan.name}")
        lines.append(f"{'='*60}")
        lines.append(f"Description: {plan.description}")
        lines.append(f"Priority: {plan.priority}")
        lines.append(f"Progress: {plan.get_progress()['progress']} ({plan.get_progress()['percentage']:.1f}%)")
        lines.append(f"\n{'Steps:'}")
        lines.append(f"{'-'*60}")
        
        for i, step in enumerate(plan.steps, 1):
            status_icon = {
                StepStatus.PENDING: "⏳",
                StepStatus.RUNNING: "🔄",
                StepStatus.SUCCESS: "✅",
                StepStatus.FAILED: "❌",
                StepStatus.SKIPPED: "⏭️"
            }.get(step.status, "❓")
            
            lines.append(f"{i}. {status_icon} {step.name} ({step.type.value})")
            
            if step.depends_on:
                deps = ", ".join(step.depends_on)
                lines.append(f"   └─ Depends on: {deps}")
            
            if step.selector:
                lines.append(f"   └─ Selector: {step.selector}")
            
            if step.value:
                lines.append(f"   └─ Value: {step.value}")
        
        lines.append(f"{'-'*60}\n")
        
        return "\n".join(lines)
