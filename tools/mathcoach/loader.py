"""Importing one chapter's templates from another.

The diagnostic and the consolidation tiers both draw on the real chapter
templates rather than on parallel copies, so what they test and what the
chapters teach cannot drift apart. Both need to import a sibling package, which
is fiddly enough to be worth doing in one place.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from .generator import Template

CONTENT = Path(__file__).resolve().parent.parent.parent / "content" / "chapters"

_CACHE: dict[str, tuple[Template, ...]] = {}


def templates_of(dirname: str) -> tuple[Template, ...]:
    """The TEMPLATES registry from content/chapters/<dirname>/templates.py."""
    if dirname in _CACHE:
        return _CACHE[dirname]

    package_dir = CONTENT / dirname
    if not package_dir.is_dir():
        raise FileNotFoundError(f"no chapter directory {package_dir}")

    package_name = f"mathcoach_content_{dirname.replace('-', '_')}"
    if package_name not in sys.modules:
        package_spec = importlib.util.spec_from_file_location(
            package_name,
            package_dir / "__init__.py",
            submodule_search_locations=[str(package_dir)],
        )
        if package_spec is None or package_spec.loader is None:
            raise ImportError(f"cannot load package for {dirname}")
        package = importlib.util.module_from_spec(package_spec)
        sys.modules[package_name] = package
        package_spec.loader.exec_module(package)

    full_name = f"{package_name}.templates"
    spec = importlib.util.spec_from_file_location(
        full_name, package_dir / "templates.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {full_name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)

    registry = getattr(module, "TEMPLATES", None)
    if registry is None:
        registry = getattr(module, "ALL_TEMPLATES", None)
    if registry is None:
        raise AttributeError(f"{dirname}/templates.py exposes no TEMPLATES")

    _CACHE[dirname] = tuple(registry)
    return _CACHE[dirname]


def template(dirname: str, template_id: str) -> Template:
    for candidate in templates_of(dirname):
        if candidate.id == template_id:
            return candidate
    raise KeyError(
        f"no template {template_id!r} in {dirname} "
        f"(have {[t.id for t in templates_of(dirname)]})"
    )
