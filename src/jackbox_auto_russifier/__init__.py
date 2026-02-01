import sys

if sys.platform != "darwin":
    raise RuntimeError(
        f"This package requires macOS (darwin). "
        f"Current platform: {sys.platform}"
    )