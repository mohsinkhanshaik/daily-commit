"""Index caching layer for AI Pulse.

The original file never imported: the whole Cache class body had been
saved with literal backslash-n escapes inside one string, so Python saw an
unterminated docstring. This rewrite restores the class and fixes the
behavioral bugs hiding behind the syntax error:

- ttl=0 was silently replaced by the default (`ttl or default_ttl`);
  None now means "use the default" and 0 means "expire immediately".
- get() returned None both for a miss and for a cached None; it now takes
  a `default` and get_or_compute() avoids the ambiguity entirely.
- It cached nothing the roadmap asked for. cached_archive() is the actual
  index cache: it keys the parsed DigestArchive on a fingerprint of every
  digest file's name, size and mtime, so editing or adding a digest
  invalidates the entry while repeated CLI/search calls reuse the parse.
"""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

_MISSING = object()


@dataclass
class CacheEntry:
    value: Any
    ttl: float
    stored_at: float = field(default_factory=time.monotonic)

    def is_expired(self, now=None) -> bool:
        return (now if now is not None else time.monotonic()) - self.stored_at >= self.ttl


class Cache:
    """In-memory TTL cache with hit/miss accounting (not thread-safe)."""

    def __init__(self, default_ttl: float = 3600):
        self.store = {}
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        self.store[key] = CacheEntry(value, self.default_ttl if ttl is None else ttl)

    def get(self, key: str, default: Any = None) -> Any:
        entry = self.store.get(key)
        if entry is None or entry.is_expired():
            self.store.pop(key, None)
            self.misses += 1
            return default
        self.hits += 1
        return entry.value

    def get_or_compute(self, key: str, compute: Callable[[], Any], ttl=None) -> Any:
        value = self.get(key, _MISSING)
        if value is _MISSING:
            value = compute()
            self.set(key, value, ttl)
        return value

    def invalidate(self, key: str) -> None:
        self.store.pop(key, None)

    def clear(self) -> None:
        self.store.clear()

    def prune_expired(self) -> int:
        now = time.monotonic()
        expired = [k for k, v in self.store.items() if v.is_expired(now)]
        for key in expired:
            del self.store[key]
        return len(expired)

    def stats(self) -> dict:
        lookups = self.hits + self.misses
        return {"size": len(self.store), "hits": self.hits, "misses": self.misses,
                "hit_rate": round(self.hits / lookups, 3) if lookups else 0.0}


def digests_fingerprint(digests_dir) -> tuple:
    """(name, size, mtime_ns) for every digest file; changes on any edit."""
    path = Path(digests_dir)
    if not path.is_dir():
        return ()
    return tuple((p.name, p.stat().st_size, p.stat().st_mtime_ns)
                 for p in sorted(path.glob("*.md")) if p.is_file())


INDEX_CACHE = Cache(default_ttl=24 * 3600)


def cached_archive(digests_dir=None):
    """Parsed DigestArchive, re-parsed only when digest files change."""
    from archive import DEFAULT_DIR, DigestArchive
    folder = Path(digests_dir) if digests_dir else DEFAULT_DIR
    key = "archive:%s:%d" % (folder, hash(digests_fingerprint(folder)))
    return INDEX_CACHE.get_or_compute(key, lambda: DigestArchive.load(folder))


if __name__ == "__main__":
    c = Cache(default_ttl=10)
    c.set("none_value", None)
    c.set("gone", 1, ttl=0)
    print("cached None found:", c.get("none_value", "MISS") is None,
          "| ttl=0 expired:", c.get("gone", "MISS") == "MISS")
    t0 = time.perf_counter(); first = cached_archive(); t1 = time.perf_counter()
    second = cached_archive(); t2 = time.perf_counter()
    print("archive days:", len(first.digests), "| same object:", first is second,
          "| cold %.1f ms, warm %.3f ms" % ((t1 - t0) * 1000, (t2 - t1) * 1000))
    print(INDEX_CACHE.stats())
