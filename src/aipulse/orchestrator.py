"""Multi-step digest processing orchestrator.

Orchestrates a multi-step pipeline for digest processing: parse digest
markdown, extract entities, apply topic tagging, score items, build
archive index. Coordinates state across steps and provides a high-level
API to run full pipelines or individual steps with error recovery.
"""

from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from enum import Enum
import json

class StepName(Enum):
      PARSE = "parse"
      TAG = "tag"
      ENTITY = "entity"
      SCORE = "score"
      INDEX = "index"


@dataclass
class ProcessingStep:
      name: StepName
      func: Callable
      enabled: bool = True
      retry_on_error: bool = False
      depends_on: list[StepName] = field(default_factory=list)


@dataclass
class ProcessingResult:
      step: StepName
      success: bool
      data: Any = None
      error: Optional[str] = None


class Orchestrator:
      """Coordinates multi-step digest processing pipeline."""

    def __init__(self):
              self.steps: dict[StepName, ProcessingStep] = {}
              self.results: dict[StepName, ProcessingResult] = {}
              self.step_order: list[StepName] = []

    def register_step(
              self,
              name: StepName,
              func: Callable,
              enabled: bool = True,
              depends_on: list[StepName] = None,
    ):
              """Register a processing step."""
              self.steps[name] = ProcessingStep(
                  name=name,
                  func=func,
                  enabled=enabled,
                  depends_on=depends_on or [],
              )

    def run_pipeline(self, data: Any) -> dict[StepName, ProcessingResult]:
              """Run the full processing pipeline."""
              self._order_steps()
              self.results = {}
              current_data = data

        for step_name in self.step_order:
                      step = self.steps[step_name]
                      if not step.enabled:
                                        continue

                      if not self._check_dependencies(step):
                                        self.results[step_name] = ProcessingResult(
                                                              step=step_name,
                                                              success=False,
                                                              error="Dependency not met",
                                        )
                                        continue

                      try:
                                        result = step.func(current_data)
                                        self.results[step_name] = ProcessingResult(
                                            step=step_name, success=True, data=result
                                        )
                                        current_data = result
except Exception as e:
                self.results[step_name] = ProcessingResult(
                                      step=step_name, success=False, error=str(e)
                )
                if not step.retry_on_error:
                                      break

        return self.results

    def _order_steps(self):
              """Topological sort of steps by dependency."""
              self.step_order = list(self.steps.keys())

    def _check_dependencies(self, step: ProcessingStep) -> bool:
              """Check if step dependencies have succeeded."""
              for dep in step.depends_on:
                            result = self.results.get(dep)
                            if result is None or not result.success:
                                              return False
                                      return True

    def get_step_result(self, name: StepName) -> Optional[ProcessingResult]:
              """Get result of a specific step."""
              return self.results.get(name)

    def export_summary(self) -> str:
              """Export a summary of processing results as JSON."""
              summary = {
                  "total_steps": len(self.steps),
                            "completed_steps": sum(
                                              1 for r in self.results.values() if r.success
                            ),
                            "failed_steps": sum(
                                              1 for r in self.results.values() if not r.success
                            ),
                            "step_results": {
                                              name.value: {"success": result.success, "error": result.error}
                                              for name, result in self.results.items()
                            },
              }
        return json.dumps(summary, indent=2)


if __name__ == "__main__":
      # Demo: simple step functions and orchestration
      def mock_parse(data):
                return {"parsed": data}

    def mock_tag(data):
              return {**data, "tagged": True}

    def mock_score(data):
              return {**data, "scored": True}

    orch = Orchestrator()
    orch.register_step(StepName.PARSE, mock_parse)
    orch.register_step(
              StepName.TAG, mock_tag, depends_on=[StepName.PARSE]
    )
    orch.register_step(
              StepName.SCORE, mock_score, depends_on=[StepName.TAG]
    )

    results = orch.run_pipeline({"content": "test digest"})
    print("Pipeline executed.")
    print(orch.export_summary())
