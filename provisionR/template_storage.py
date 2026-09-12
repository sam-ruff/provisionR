"""Template locations shared by uploads and rendering."""

import os
from pathlib import Path


BUNDLED_TEMPLATES = Path(__file__).parent / "templates"


def writable_template_directory() -> Path:
    configured = os.environ.get("PROVISIONR_TEMPLATE_DIR")
    if configured is None:
        return BUNDLED_TEMPLATES
    if not configured.strip():
        raise ValueError("PROVISIONR_TEMPLATE_DIR must not be empty")
    return Path(configured)


def template_search_paths() -> list[Path]:
    writable = writable_template_directory()
    if writable == BUNDLED_TEMPLATES:
        return [BUNDLED_TEMPLATES]
    return [writable, BUNDLED_TEMPLATES]
