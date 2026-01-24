from pathlib import Path


def find_repo_root(start_path: Path) -> Path:
    """Find repository root by walking up to a directory containing .git."""
    for candidate in [start_path, *start_path.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise FileNotFoundError("Unable to locate repository root containing .git")
