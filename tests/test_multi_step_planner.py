import unittest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.multi_step_planner import (
    MultiStepPlanner,
    TestPlan,
    TestStep,
    StepType,
    StepStatus,
)


class TestStepClass(unittest.TestCase):
    """Test TestStep class"""

    def test_step_creation(self):
        """Test creating a step"""
        step = TestStep(
            id="step1",
            name="Test step",
            type=StepType.CLICK,
            action="click",
            selector="#button",
            depends_on=[],
        )

        self.assertEqual(step.id, "step1")
        self.assertEqual(step.name, "Test step")
        self.assertEqual(step.type, StepType.CLICK)
        self.assertEqual(step.status, StepStatus.PENDING)

    def test_can_execute_no_dependencies(self):
        """Test step can execute when no dependencies"""
        step = TestStep(
            id="step1", name="Test", type=StepType.CLICK, action="click", depends_on=[]
        )

        self.assertTrue(step.can_execute(set()))

    def test_can_execute_with_completed_dependencies(self):
        """Test step can execute when dependencies completed"""
        step = TestStep(
            id="step2",
            name="Test",
            type=StepType.CLICK,
            action="click",
            depends_on=["step1"],
        )

        completed = {"step1"}
        self.assertTrue(step.can_execute(completed))

    def test_cannot_execute_with_incomplete_dependencies(self):
        """Test step cannot execute when dependencies incomplete"""
        step = TestStep(
            id="step2",
            name="Test",
            type=StepType.CLICK,
            action="click",
            depends_on=["step1"],
        )

        completed = set()
        self.assertFalse(step.can_execute(completed))

    def test_cannot_execute_when_not_pending(self):
        """Test step cannot execute when not pending"""
        step = TestStep(
            id="step1", name="Test", type=StepType.CLICK, action="click", depends_on=[]
        )
        step.status = StepStatus.SUCCESS

        self.assertFalse(step.can_execute(set()))

    def test_to_dict(self):
        """Test converting step to dict"""
        step = TestStep(
            id="step1",
            name="Test step",
            type=StepType.CLICK,
            action="click",
            selector="#button",
            value="test",
            expected="result",
            depends_on=["step0"],
        )

        data = step.to_dict()

        self.assertEqual(data["id"], "step1")
        self.assertEqual(data["name"], "Test step")
        self.assertEqual(data["type"], "click")
        self.assertEqual(data["selector"], "#button")
        self.assertEqual(data["value"], "test")
        self.assertEqual(data["expected"], "result")
        self.assertEqual(data["depends_on"], ["step0"])


class TestPlanClass(unittest.TestCase):
    """Test TestPlan class"""

    def setUp(self):
        """Set up test plan"""
        self.plan = TestPlan(
            id="plan1", name="Test Plan", description="Test description"
        )

    def test_plan_creation(self):
        """Test creating a plan"""
        self.assertEqual(self.plan.id, "plan1")
        self.assertEqual(self.plan.name, "Test Plan")
        self.assertEqual(self.plan.description, "Test description")
        self.assertEqual(len(self.plan.steps), 0)

    def test_add_step(self):
        """Test adding step to plan"""
        step = TestStep(id="step1", name="Test", type=StepType.CLICK, action="click")

        self.plan.add_step(step)
        self.assertEqual(len(self.plan.steps), 1)
        self.assertEqual(self.plan.steps[0].id, "step1")

    def test_get_executable_steps(self):
        """Test getting executable steps"""
        step1 = TestStep(
            id="step1", name="S1", type=StepType.CLICK, action="click", depends_on=[]
        )
        step2 = TestStep(
            id="step2",
            name="S2",
            type=StepType.CLICK,
            action="click",
            depends_on=["step1"],
        )

        self.plan.add_step(step1)
        self.plan.add_step(step2)

        # Initially only step1 is executable
        executable = self.plan.get_executable_steps(set())
        executable_ids = [s.id for s in executable]
        self.assertIn("step1", executable_ids)
        # step2 should not be executable yet
        for step in executable:
            if step.id == "step2":
                self.fail("step2 should not be executable without step1 completed")

        # After step1 completes, step2 is executable
        executable = self.plan.get_executable_steps({"step1"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step2", executable_ids)

    def test_get_step_by_id(self):
        """Test getting step by ID"""
        step = TestStep(id="step1", name="Test", type=StepType.CLICK, action="click")
        self.plan.add_step(step)

        found = self.plan.get_step_by_id("step1")
        self.assertIsNotNone(found)
        self.assertEqual(found.id, "step1")

        not_found = self.plan.get_step_by_id("step999")
        self.assertIsNone(not_found)

    def test_is_complete(self):
        """Test checking if plan is complete"""
        step1 = TestStep(id="step1", name="S1", type=StepType.CLICK, action="click")
        step2 = TestStep(id="step2", name="S2", type=StepType.CLICK, action="click")

        self.plan.add_step(step1)
        self.plan.add_step(step2)

        # Not complete initially
        self.assertFalse(self.plan.is_complete())

        # Complete when all steps success
        step1.status = StepStatus.SUCCESS
        step2.status = StepStatus.SUCCESS
        self.assertTrue(self.plan.is_complete())

    def test_has_failed(self):
        """Test checking if plan has failed steps"""
        step1 = TestStep(id="step1", name="S1", type=StepType.CLICK, action="click")
        step2 = TestStep(id="step2", name="S2", type=StepType.CLICK, action="click")

        self.plan.add_step(step1)
        self.plan.add_step(step2)

        # No failures initially
        self.assertFalse(self.plan.has_failed())

        # Has failure when one step fails
        step1.status = StepStatus.FAILED
        self.assertTrue(self.plan.has_failed())

    def test_get_progress(self):
        """Test getting progress"""
        step1 = TestStep(id="step1", name="S1", type=StepType.CLICK, action="click")
        step2 = TestStep(id="step2", name="S2", type=StepType.CLICK, action="click")
        step3 = TestStep(id="step3", name="S3", type=StepType.CLICK, action="click")

        self.plan.add_step(step1)
        self.plan.add_step(step2)
        self.plan.add_step(step3)

        step1.status = StepStatus.SUCCESS
        step2.status = StepStatus.FAILED

        progress = self.plan.get_progress()

        self.assertEqual(progress["total"], 3)
        self.assertEqual(progress["completed"], 1)
        self.assertEqual(progress["failed"], 1)
        self.assertEqual(progress["pending"], 1)
        self.assertEqual(progress["progress"], "1/3")
        self.assertAlmostEqual(progress["percentage"], 33.33, places=1)


class TestMultiStepPlanner(unittest.TestCase):
    """Test MultiStepPlanner class"""

    def setUp(self):
        """Set up planner"""
        self.planner = MultiStepPlanner()

    def test_list_templates(self):
        """Test listing templates"""
        templates = self.planner.list_templates()

        self.assertIsInstance(templates, list)
        self.assertIn("login_flow", templates)
        self.assertIn("form_submission", templates)
        self.assertIn("search_flow", templates)
        self.assertIn("e_commerce_checkout", templates)

    def test_create_plan_from_template(self):
        """Test creating plan from template"""
        plan = self.planner.create_plan_from_template("login_flow", "test_plan")

        self.assertIsNotNone(plan)
        self.assertEqual(plan.id, "test_plan")
        self.assertEqual(plan.name, "Complete Login Flow")
        self.assertGreater(len(plan.steps), 0)

    def test_create_plan_from_invalid_template(self):
        """Test creating plan from invalid template"""
        plan = self.planner.create_plan_from_template("invalid_template", "test")

        self.assertIsNone(plan)

    def test_create_custom_plan(self):
        """Test creating custom plan"""
        steps_data = [
            {
                "id": "step1",
                "name": "Test step",
                "type": "click",
                "action": "click",
                "selector": "#button",
                "depends_on": [],
            }
        ]

        plan = self.planner.create_custom_plan(
            "custom1", "Custom Plan", "Test description", steps_data
        )

        self.assertEqual(plan.id, "custom1")
        self.assertEqual(plan.name, "Custom Plan")
        self.assertEqual(len(plan.steps), 1)
        self.assertEqual(plan.steps[0].id, "step1")

    def test_get_plan(self):
        """Test getting plan by ID"""
        plan = self.planner.create_plan_from_template("login_flow", "test_plan")

        found = self.planner.get_plan("test_plan")
        self.assertIsNotNone(found)
        self.assertEqual(found.id, "test_plan")

        not_found = self.planner.get_plan("nonexistent")
        self.assertIsNone(not_found)

    def test_save_and_load_plan(self):
        """Test saving and loading plan"""
        # Create plan
        steps_data = [
            {
                "id": "step1",
                "name": "Test step",
                "type": "click",
                "action": "click",
                "selector": "#button",
                "depends_on": [],
            }
        ]

        plan = self.planner.create_custom_plan(
            "save_test", "Save Test", "Test save/load", steps_data
        )

        # Save to temp file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_file = f.name

        try:
            self.planner.save_plan(plan, temp_file)

            # Verify file exists
            self.assertTrue(os.path.exists(temp_file))

            # Load plan
            loaded_plan = self.planner.load_plan(temp_file)

            # Verify loaded plan
            self.assertEqual(loaded_plan.id, "save_test")
            self.assertEqual(loaded_plan.name, "Save Test")
            self.assertEqual(len(loaded_plan.steps), 1)
            self.assertEqual(loaded_plan.steps[0].id, "step1")

        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_visualize_plan(self):
        """Test visualizing plan"""
        plan = self.planner.create_plan_from_template("login_flow", "viz_test")

        visualization = self.planner.visualize_plan(plan)

        self.assertIsInstance(visualization, str)
        self.assertIn("Test Plan:", visualization)
        self.assertIn("Complete Login Flow", visualization)
        self.assertIn("Steps:", visualization)


class TestComplexDependencies(unittest.TestCase):
    """Test complex dependency scenarios"""

    def setUp(self):
        """Set up planner"""
        self.planner = MultiStepPlanner()

    def test_linear_dependencies(self):
        """Test linear dependency chain"""
        steps_data = [
            {
                "id": "step1",
                "name": "S1",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step2",
                "name": "S2",
                "type": "click",
                "action": "click",
                "depends_on": ["step1"],
            },
            {
                "id": "step3",
                "name": "S3",
                "type": "click",
                "action": "click",
                "depends_on": ["step2"],
            },
        ]

        plan = self.planner.create_custom_plan("linear", "Linear", "Test", steps_data)

        # Only step1 executable initially
        executable = plan.get_executable_steps(set())
        executable_ids = [s.id for s in executable]
        self.assertIn("step1", executable_ids)
        # Verify step2 and step3 are NOT executable
        for step in executable:
            self.assertNotIn(step.id, ["step2", "step3"])

        # After step1, only step2 executable
        executable = plan.get_executable_steps({"step1"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step2", executable_ids)
        # Verify step3 is NOT executable yet
        for step in executable:
            self.assertNotEqual(step.id, "step3")

        # After step1 and step2, only step3 executable
        executable = plan.get_executable_steps({"step1", "step2"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step3", executable_ids)

    def test_parallel_execution(self):
        """Test parallel execution (no dependencies)"""
        steps_data = [
            {
                "id": "step1",
                "name": "S1",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step2",
                "name": "S2",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step3",
                "name": "S3",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
        ]

        plan = self.planner.create_custom_plan(
            "parallel", "Parallel", "Test", steps_data
        )

        # All steps executable initially
        executable = plan.get_executable_steps(set())
        self.assertEqual(len(executable), 3)

    def test_multiple_dependencies(self):
        """Test step with multiple dependencies"""
        steps_data = [
            {
                "id": "step1",
                "name": "S1",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step2",
                "name": "S2",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step3",
                "name": "S3",
                "type": "click",
                "action": "click",
                "depends_on": ["step1", "step2"],
            },
        ]

        plan = self.planner.create_custom_plan("multi_dep", "Multi", "Test", steps_data)

        # step1 and step2 executable initially
        executable = plan.get_executable_steps(set())
        executable_ids = [s.id for s in executable]
        self.assertIn("step1", executable_ids)
        self.assertIn("step2", executable_ids)
        # step3 should NOT be executable
        for step in executable:
            self.assertNotEqual(step.id, "step3")

        # step3 not executable with only step1 complete
        executable = plan.get_executable_steps({"step1"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step2", executable_ids)
        # step3 should NOT be executable yet
        for step in executable:
            self.assertNotEqual(step.id, "step3")

        # step3 executable when both complete
        executable = plan.get_executable_steps({"step1", "step2"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step3", executable_ids)

    def test_diamond_dependency(self):
        """Test diamond dependency pattern"""
        steps_data = [
            {
                "id": "step1",
                "name": "S1",
                "type": "click",
                "action": "click",
                "depends_on": [],
            },
            {
                "id": "step2a",
                "name": "S2a",
                "type": "click",
                "action": "click",
                "depends_on": ["step1"],
            },
            {
                "id": "step2b",
                "name": "S2b",
                "type": "click",
                "action": "click",
                "depends_on": ["step1"],
            },
            {
                "id": "step3",
                "name": "S3",
                "type": "click",
                "action": "click",
                "depends_on": ["step2a", "step2b"],
            },
        ]

        plan = self.planner.create_custom_plan("diamond", "Diamond", "Test", steps_data)

        # Only step1 initially
        executable = plan.get_executable_steps(set())
        executable_ids = [s.id for s in executable]
        self.assertIn("step1", executable_ids)
        # Verify step2a, step2b, step3 are NOT executable
        for step in executable:
            self.assertNotIn(step.id, ["step2a", "step2b", "step3"])

        # step2a and step2b after step1
        executable = plan.get_executable_steps({"step1"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step2a", executable_ids)
        self.assertIn("step2b", executable_ids)
        # Verify step3 is NOT executable yet
        for step in executable:
            self.assertNotEqual(step.id, "step3")

        # step3 only after both step2a and step2b
        executable = plan.get_executable_steps({"step1", "step2a", "step2b"})
        executable_ids = [s.id for s in executable]
        self.assertIn("step3", executable_ids)


if __name__ == "__main__":
    unittest.main()
