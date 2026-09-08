"""Plugin system for AI Pulse: extensible analyzers and exporters.

This module enables third-party extensions without modifying core code.
Plugins register as Analyzer or Exporter subclasses via PluginRegistry.

Design: PluginRegistry maintains a dict of registered plugins by name.
Hooks run at digest ingestion, analysis, and export stages. Plugins
can read digest state, emit events, and produce outputs. Discovery via
directory scan of plugins/ or explicit registration.
"""

import importlib.util
import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type


@dataclass
class Hook:
    """Event emitted when a hook stage runs."""
    stage: str
    data: Any


class Plugin(ABC):
    """Base class for all plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin identifier."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Semantic version."""
        pass


class Analyzer(Plugin):
    """Base class for custom analyzers."""

    @abstractmethod
    def analyze(self, data: Any) -> Dict[str, Any]:
        """Analyze data and return results."""
        pass


class Exporter(Plugin):
    """Base class for custom exporters."""

    @abstractmethod
    def export(self, data: Any, path: str) -> bool:
        """Export data to file. Return True on success."""
        pass



class PluginRegistry:
    """Manages plugin registration, discovery, and lifecycle."""

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[Callable]] = {
            'ingest': [],
            'analyze': [],
            'export': []
        }

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance."""
        if plugin.name in self.plugins:
            raise ValueError(f"Plugin {plugin.name} already registered")
        self.plugins[plugin.name] = plugin

    def unregister(self, name: str) -> None:
        """Unregister a plugin by name."""
        if name in self.plugins:
            del self.plugins[name]

    def get(self, name: str) -> Optional[Plugin]:
        """Retrieve a plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        """Return all registered plugin names."""
        return list(self.plugins.keys())

    def list_analyzers(self) -> List[Analyzer]:
        """Return all registered analyzers."""
        return [p for p in self.plugins.values() if isinstance(p, Analyzer)]

    def list_exporters(self) -> List[Exporter]:
        """Return all registered exporters."""
        return [p for p in self.plugins.values() if isinstance(p, Exporter)]

    def on(self, stage: str, callback: Callable) -> None:
        """Register a hook callback for a stage."""
        if stage not in self.hooks:
            self.hooks[stage] = []
        self.hooks[stage].append(callback)

    def emit(self, stage: str, data: Any) -> None:
        """Emit a hook event for all registered callbacks."""
        for callback in self.hooks.get(stage, []):
            callback(Hook(stage, data))

    def load_directory(self, path: str) -> int:
        """Scan and load plugins from a directory. Return count loaded."""
        p = Path(path)
        if not p.is_dir():
            return 0
        count = 0
        for py_file in p.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            try:
                spec = importlib.util.spec_from_file_location(
                    py_file.stem, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and
                        issubclass(obj, Plugin) and
                        obj is not Plugin):
                        self.register(obj())
                        count += 1
            except Exception:
                pass
        return count



if __name__ == '__main__':
    class DemoAnalyzer(Analyzer):
        @property
        def name(self) -> str:
            return 'demo_analyzer'

        @property
        def version(self) -> str:
            return '1.0.0'

        def analyze(self, data: Any) -> Dict[str, Any]:
            return {'demo': 'result', 'input': data}

    class DemoExporter(Exporter):
        @property
        def name(self) -> str:
            return 'demo_exporter'

        @property
        def version(self) -> str:
            return '1.0.0'

        def export(self, data: Any, path: str) -> bool:
            Path(path).write_text(str(data))
            return True

    registry = PluginRegistry()
    analyzer = DemoAnalyzer()
    exporter = DemoExporter()

    registry.register(analyzer)
    registry.register(exporter)

    print(f"Plugins: {registry.list_plugins()}")
    print(f"Analyzers: {[a.name for a in registry.list_analyzers()]}")

    def log_hook(hook: Hook):
        print(f"Hook {hook.stage}: {hook.data}")

    registry.on('analyze', log_hook)
    registry.emit('analyze', {'test': 'data'})

    result = analyzer.analyze({'key': 'value'})
    print(f"Analysis result: {result}")

    success = exporter.export({'out': 'data'}, '/tmp/test.txt')
    print(f"Export success: {success}")
