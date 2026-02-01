import sys

if sys.platform != "darwin":
    raise RuntimeError(f"This package requires macOS (darwin). Current platform: {sys.platform}")
