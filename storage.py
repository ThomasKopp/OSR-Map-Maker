"""Independent project-file storage and resource limits."""
from __future__ import annotations

import copy
import hashlib
import io
import json
import os
import re
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid4, uuid5

from validation import validate_project_document

COMPRESSED_PROJECT_SUFFIX = ".osrmapz"
PROJECT_ZIP_MEMBER = "project.json"


class ProjectFileConflictError(OSError):
    """The destination changed after it was reviewed and before replacement."""


@dataclass(frozen=True)
class ProjectResourceLimits:
    """Configurable defensive limits for project input and raster output."""

    max_file_bytes: int = 128 * 1024 * 1024
    max_uncompressed_bytes: int = 256 * 1024 * 1024
    max_export_pixels: int = 80_000_000
    bytes_per_export_pixel: int = 4


def resource_limits_from_environment() -> ProjectResourceLimits:
    """Read optional MiB/megapixel limits without adding UI-global state."""
    defaults = ProjectResourceLimits()

    def positive(name: str, fallback: int) -> int:
        try:
            return max(1, int(os.environ.get(name, fallback)))
        except ValueError:
            return fallback

    return ProjectResourceLimits(
        max_file_bytes=positive("OSR_MAP_MAX_FILE_MIB", defaults.max_file_bytes // 1024 // 1024) * 1024 * 1024,
        max_uncompressed_bytes=positive("OSR_MAP_MAX_EXPANDED_MIB", defaults.max_uncompressed_bytes // 1024 // 1024) * 1024 * 1024,
        max_export_pixels=positive("OSR_MAP_MAX_EXPORT_MP", defaults.max_export_pixels // 1_000_000) * 1_000_000,
        bytes_per_export_pixel=defaults.bytes_per_export_pixel,
    )


DEFAULT_RESOURCE_LIMITS = resource_limits_from_environment()


def file_fingerprint(path: Path) -> str | None:
    try:
        with path.open("rb") as handle:
            digest = hashlib.sha256()
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
            return digest.hexdigest()
    except FileNotFoundError:
        return None


def normalized_file_path(path: Path) -> str:
    return os.path.normcase(str(path.resolve()))


def ensure_project_id(project: dict[str, Any], source: Path | None = None) -> str:
    meta = project.setdefault("meta", {})
    if not isinstance(meta, dict):
        meta = {}
        project["meta"] = meta
    identity = meta.get("projectId")
    if not isinstance(identity, str) or not re.fullmatch(r"[0-9a-f]{32}", identity):
        identity = (
            uuid5(NAMESPACE_URL, os.path.normcase(str(source.resolve()))).hex
            if source is not None
            else uuid4().hex
        )
        meta["projectId"] = identity
    return identity


def _checked_file_bytes(path: Path, limits: ProjectResourceLimits) -> bytes:
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Could not inspect project file: {exc}") from exc
    if size > limits.max_file_bytes:
        raise ValueError(
            f"Project is {size / 1024 / 1024:.1f} MiB; the configured input limit is "
            f"{limits.max_file_bytes / 1024 / 1024:.1f} MiB."
        )
    return path.read_bytes()


def _checked_zip_member(content: bytes, limits: ProjectResourceLimits) -> bytes:
    with zipfile.ZipFile(io.BytesIO(content), "r") as archive:
        try:
            info = archive.getinfo(PROJECT_ZIP_MEMBER)
        except KeyError as exc:
            raise ValueError("Compressed project has no project.json member.") from exc
        if info.file_size > limits.max_uncompressed_bytes:
            raise ValueError(
                f"Compressed project expands to {info.file_size / 1024 / 1024:.1f} MiB; "
                f"the configured limit is {limits.max_uncompressed_bytes / 1024 / 1024:.1f} MiB."
            )
        with archive.open(info, "r") as handle:
            chunks: list[bytes] = []
            total = 0
            while chunk := handle.read(1024 * 1024):
                total += len(chunk)
                if total > limits.max_uncompressed_bytes:
                    raise ValueError("Compressed project exceeds the configured expanded-size limit.")
                chunks.append(chunk)
    return b"".join(chunks)


def read_project_with_fingerprint(
    path: Path, limits: ProjectResourceLimits = DEFAULT_RESOURCE_LIMITS
) -> tuple[dict[str, Any], str]:
    content = _checked_file_bytes(path, limits)
    data = _checked_zip_member(content, limits) if path.suffix.lower() == COMPRESSED_PROJECT_SUFFIX else content
    if len(data) > limits.max_uncompressed_bytes:
        raise ValueError("Project exceeds the configured expanded-size limit.")
    try:
        loaded = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Project JSON is invalid: {exc}") from exc
    loaded = validate_project_document(loaded)
    ensure_project_id(loaded, path)
    return loaded, hashlib.sha256(content).hexdigest()


def read_project_file(
    path: Path, limits: ProjectResourceLimits = DEFAULT_RESOURCE_LIMITS
) -> dict[str, Any]:
    return read_project_with_fingerprint(path, limits)[0]


def write_project_data(
    path: Path, project: dict[str, Any], *, compact: bool = False,
    expected_fingerprint: str | None = None, check_conflict: bool = False,
) -> str:
    """Atomically publish a complete, flushed project file."""
    content = json.dumps(project, separators=(",", ":")) if compact else json.dumps(project, indent=2)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w+b", prefix=f".{path.name}.", suffix=".tmp", dir=path.parent, delete=False
        ) as handle:
            temporary = Path(handle.name)
            if path.suffix.lower() == COMPRESSED_PROJECT_SUFFIX:
                with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                    archive.writestr(PROJECT_ZIP_MEMBER, content)
            else:
                handle.write(content.encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
        fingerprint = file_fingerprint(temporary)
        if check_conflict and file_fingerprint(path) != expected_fingerprint:
            raise ProjectFileConflictError("The destination changed while saving. Please review it and try again.")
        os.replace(temporary, path)
        return str(fingerprint)
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


def load_project(path: str | Path) -> dict[str, Any]:
    return read_project_file(Path(path))


def save_project(path: str | Path, project: dict[str, Any]) -> None:
    snapshot = copy.deepcopy(project)
    write_project_data(Path(path), snapshot)


def autosave_project(path: str | Path, project: dict[str, Any]) -> None:
    save_project(path, project)
