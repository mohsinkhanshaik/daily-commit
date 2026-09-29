"""Multi-step digest processing orchestrator for complex analysis workflows.

Enables composable pipelines that chain models, tags, scores, and filters.
Supports result aggregation, error handling, and cross-step dependencies.
"""

from dataclasses import dataclass, field
from typing import Callable, Any, Dict, List
from datetime import date

@dataclass
class Task:
    name: str
    func: Callable
    inputs: Dict[str, Any]

@dataclass
class WorkflowResult:
    step_name: str
    status: str
    data: Any
    error: str = ""

@dataclass
class Orchestrator:
    tasks: List[Task] = field(default_factory=list)
    results: List[WorkflowResult] = field(default_factory=list)

    def add_task(self, name: str, func: Callable, inputs: Dict[str, Any]) -> None:
        self.tasks.append(Task(name, func, inputs))

    def run_workflow(self) -> bool:
        for task in self.tasks:
            try:
                result = task.func(**task.inputs)
                self.results.append(WorkflowResult(
                    step_name=task.name,
                    status="success",
                    data=result
                ))
            except Exception as e:
                self.results.append(WorkflowResult(
                    step_name=task.name,
                    status="error",
                    data=None,
                    error=str(e)
                ))
                return False
        return True

    def aggregate_results(self) -> Dict[str, Any]:
        success_count = sum(1 for r in self.results if r.status == "success")
        return {
            "total_steps": len(self.results),
            "succeeded": success_count,
            "failed": len(self.results) - success_count,
            "steps": [
                {"name": r.step_name, "status": r.status}
                for r in self.results
            ]
        }

def compose_pipeline(*funcs: Callable) -> Callable:
    def pipeline(data: Any) -> Any:
        result = data
        for func in funcs:
            result = func(result)
        return result
    return pipeline

if __name__ == "__main__":
    def tag_items(items: List[str]) -> List[str]:
        return [f"[TAGGED] {item}" for item in items]

    def score_items(items: List[str]) -> List[tuple]:
        return [(item, len(item)) for item in items]

    def filter_items(items: List[tuple]) -> List[tuple]:
        return [i for i in items if i[1] > 5]

    orch = Orchestrator()
    orch.add_task("tag", tag_items, {"items": ["news1", "story2"]})
    orch.add_task("score", score_items, {"items": ["[TAGGED] news1", "[TAGGED] story2"]})
    orch.add_task("filter", filter_items, {"items": [("[TAGGED] news1", 16), ("[TAGGED] story2", 17)]})

    if orch.run_workflow():
        agg = orch.aggregate_results()
        print(f"Workflow complete: {agg['succeeded']}/{agg['total_steps']} steps succeeded")
    else:
        print("Workflow failed")
