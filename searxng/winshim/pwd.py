"""Windows-only import shim for SearXNG research instance (local use only).

Upstream `searx/valkeydb.py` does `import pwd` (Unix-only) at module top level.
In our config no `valkey.url` is set, so `initialize()` returns False before any
`pwd.*` call — this stub exists solely to satisfy the import and is never called.
If it IS ever called, it fails loudly instead of returning wrong data.
Not part of upstream; do not commit upstream; delete if running on Linux.
"""


def getpwuid(_uid):
    raise NotImplementedError("pwd shim: no Unix user database on Windows")


def getpwnam(_name):
    raise NotImplementedError("pwd shim: no Unix user database on Windows")
