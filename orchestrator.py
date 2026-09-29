"""Multi-step digest processing orchestrator for AI Pulse.

Orchestrates the processing pipeline: parse digests, tag items, extract
entities, score importance, and update the searchable archive. Handles
batch operations and progress tracking for efficiency.
"""

from dataclasses import dataclass, field
from typing import Callable
from enum import Enum
from datetime import date

class ProcessingStage(str, Enum):
    """Processing pipeline stages."""
    PARSE = "parse"
    TAG = "tag"
    EXTRACT = "extract"
    SCORE = "score"
    INDEX = "index"


@dataclass
class ProcessingTask:
    """A single digest processing job."""
    digest_date: date
    stages: list[ProcessingStage] = field(default_factory=lambda: list(ProcessingStage))
    completed_stages: list[ProcessingStage] = field(default_factory=list)
    status: str = "pending"
    error: str = ""

    def mark_stage_done(self, stage: ProcessingStage) -> None:
        """Record a stage completion."""
        if stage not in self.completed_stages:
            self.completed_stages.append(stage)

    @property
    def progress(self) -> float:
        """Return completion ratio 0.0-1.0."""
        if not self.stages:
            return 1.0
        return len(self.completed_stages) / len(self.stages)

    def is_complete(self) -> bool:
        """Check if all stages are done."""
        return len(self.completed_stages) == len(self.stages)

@dataclass
class BatchProcessor:
    """Orchestrates multi-stage digest processing."""
    stages: list[tuple[ProcessingStage, Callable]] = field(default_factory=list)
    active_tasks: dict[date, ProcessingTask] = field(default_factory=dict)

    def register_stage(self, stage: ProcessingStage, handler: Callable) -> None:
        """Register a processing stage handler."""
        self.stages.append((stage, handler))

    def enqueue_digest(self, digest_date: date, selected_stages: list[ProcessingStage] = None) -> ProcessingTask:
        """Queue a digest for processing."""
        if selected_stages is None:
            selected_stages = [s[0] for s in self.stages]
        task = ProcessingTask(digest_date=digest_date, stages=selected_stages)
        self.active_tasks[digest_date] = task
        return task

    def process(self, task: ProcessingTask) -> bool:
        """Run all stages for a task."""
        try:
            for stage, handler in self.stages:
                if stage in task.stages:
                    handler(task.digest_date)
                    task.mark_stage_done(stage)
            task.status = "complete"
            return True
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            return False

    def get_stats(self) -> dict:
        """Return processing statistics."""
        if not self.active_tasks:
            return {"total": 0, "complete": 0, "failed": 0}
        complete = sum(1 for t in self.active_tasks.values() if t.is_complete())
        failed = sum(1 for t in self.active_tasks.values() if t.status == "failed")
        return {"total": len(self.active_tasks), "complete": complete, "failed": failed}

if __name__ == "__main__":
    from datetime import date

    def mock_parse(d):
        print(f"  Parsed digest {d}")

    def mock_tag(d):
        print(f"  Tagged items in {d}")

    def mock_extract(d):
        print(f"  Extracted entities from {d}")

    proc = BatchProcessor()
    proc.register_stage(ProcessingStage.PARSE, mock_parse)
    proc.register_stage(ProcessingStage.TAG, mock_tag)
    proc.register_stage(ProcessingStage.EXTRACT, mock_extract)

    today = date.today()
    task = proc.enqueue_digest(today)
    print(f"Queued {today} with {len(task.stages)} stages")
    success = proc.process(task)
    print(f"Result: {task.status}, progress {task.progress:.1%}")
    stats = proc.get_stats()
    print(f"Batch stats: {stats}")
