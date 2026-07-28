"""Generate minimal vendir.yml, sync, and read lock pins."""

from __future__ import annotations

import re
import shutil
import tempfile
from pathlib import Path

from ut_cli import proc
from ut_cli.catalog import catalog_root
from ut_cli.config import catalog_repo

STATE_DIR = ".snip"
VENDIR_YML = "vendir.yml"
VENDIR_LOCK = "vendir.lock.yml"


def vendir_bin() -> str:
    return proc.require_tool("vendir")


def state_dir(base: Path | None = None) -> Path:
    root = (base or Path.cwd()) / STATE_DIR
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_vendir_config(
    units: list[dict],
    *,
    dest_dir: Path,
) -> Path:
    """
    units: list of {name, path, dest, ref?}
    Writes vendir.yml under dest_dir (usually .snip/).
    Local catalogs: directory contents (dirs only; files staged into a temp dir first).
    Remote catalogs: git contents with paths.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    local = catalog_root()
    lines = ["apiVersion: vendir.k14s.io/v1alpha1", "kind: Config", "directories:"]
    for unit in units:
        name = unit["name"]
        catalog_path = unit["path"].strip().strip("/")
        dest = unit["dest"]
        ref = unit.get("ref")
        lines.append(f"- path: {dest}")
        lines.append("  contents:")
        lines.append(f"  - path: {name}")
        if local is not None:
            abs_src = (local / catalog_path).resolve()
            if abs_src.is_file():
                # vendir directory source requires a directory — stage the single file.
                # Path must be relative to dest_dir (vendir sync cwd), not the project root.
                stage = dest_dir / ".stage" / name
                stage.mkdir(parents=True, exist_ok=True)
                staged = stage / abs_src.name
                shutil.copy2(abs_src, staged)
                lines.append("    directory:")
                lines.append(f"      path: {stage.relative_to(dest_dir)}")
            else:
                lines.append("    directory:")
                lines.append(f"      path: {abs_src}")
        else:
            lines.append("    git:")
            lines.append(f"      url: {catalog_repo()}")
            if ref:
                lines.append(f"      ref: {ref}")
            lines.append("      paths:")
            lines.append(f"      - {catalog_path}")
    yml = dest_dir / VENDIR_YML
    yml.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yml


def sync(cwd: Path | None = None) -> None:
    work = cwd or state_dir()
    proc.run([vendir_bin(), "sync", "-f", VENDIR_YML], cwd=str(work), capture=True)


def read_lock_refs(cwd: Path | None = None) -> dict[str, str]:
    """Best-effort parse of vendir.lock.yml for git refs by path name."""
    work = cwd or state_dir()
    lock = work / VENDIR_LOCK
    if not lock.is_file():
        return {}
    text = lock.read_text(encoding="utf-8")
    refs: dict[str, str] = {}
    current_path: str | None = None
    for line in text.splitlines():
        m_path = re.match(r"^\s+-\s+path:\s+(\S+)", line)
        if m_path:
            current_path = m_path.group(1)
            continue
        m_sha = re.match(r"^\s+sha:\s+(\S+)", line)
        if m_sha and current_path:
            refs[current_path] = m_sha.group(1)
            continue
        m_ref = re.match(r"^\s+ref:\s+(\S+)", line)
        if m_ref and current_path:
            refs.setdefault(current_path, m_ref.group(1))
    return refs


def load_units(base: Path | None = None) -> list[dict]:
    """Load tracked units from .snip/units.txt (name|path|dest|ref)."""
    path = state_dir(base) / "units.txt"
    if not path.is_file():
        return []
    units: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 3:
            continue
        units.append(
            {
                "name": parts[0],
                "path": parts[1],
                "dest": parts[2],
                "ref": parts[3] if len(parts) > 3 and parts[3] else None,
            }
        )
    return units


def save_units(units: list[dict], base: Path | None = None) -> None:
    path = state_dir(base) / "units.txt"
    lines = ["# name|catalog_path|dest|ref"]
    for u in units:
        ref = u.get("ref") or ""
        lines.append(f"{u['name']}|{u['path']}|{u['dest']}|{ref}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_unit(
    catalog_path: str,
    *,
    dest: str | Path = ".",
    ref: str | None = None,
    base: Path | None = None,
) -> Path:
    """Track a catalog path and sync it into dest. Returns materialized path."""
    catalog_path = catalog_path.strip().strip("/")
    name = catalog_path.replace("/", "__")
    dest_path = Path(dest)
    if not dest_path.is_absolute():
        dest_path = (base or Path.cwd()) / dest_path
    dest_path.mkdir(parents=True, exist_ok=True)

    rel_vendor = f"vendor/{name}"
    units = load_units(base)
    entry = {
        "name": name,
        "path": catalog_path,
        "dest": rel_vendor,
        "ref": ref,
    }
    if any(u["path"] == catalog_path for u in units):
        units = [entry if u["path"] == catalog_path else u for u in units]
    else:
        units.append(entry)
    save_units(units, base)

    work = state_dir(base)
    local = catalog_root()
    if local is not None:
        # Fast local path: copy without requiring vendir for the happy path,
        # but still write vendir.yml for remote-parity / future sync.
        src = (local / catalog_path).resolve()
        if not src.exists():
            raise FileNotFoundError(f"not found in catalog: {catalog_path}")
        write_vendir_config(units, dest_dir=work)
        try:
            sync(work)
            vendor_root = work / rel_vendor / name
            if not vendor_root.exists():
                vendor_root = work / rel_vendor
            return _materialize_to_dest(vendor_root, dest_path, catalog_path)
        except proc.ToolMissingError:
            return _copy_local(src, dest_path, catalog_path)

    write_vendir_config(units, dest_dir=work)
    sync(work)
    vendor_root = work / rel_vendor / name
    if not vendor_root.exists():
        vendor_root = work / rel_vendor
    return _materialize_to_dest(vendor_root, dest_path, catalog_path)


def _copy_local(src: Path, dest_path: Path, catalog_path: str) -> Path:
    leaf = Path(catalog_path).name
    if src.is_file():
        target = dest_path / src.name
        shutil.copy2(src, target)
        return target
    for path in src.rglob("*"):
        if path.is_file():
            rel = path.relative_to(src)
            target = dest_path / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return dest_path / leaf if (dest_path / leaf).exists() else dest_path


def _materialize_to_dest(vendor_root: Path, dest_path: Path, catalog_path: str) -> Path:
    """Copy synced files into destination; return primary path."""
    if vendor_root.is_file():
        target = dest_path / vendor_root.name
        shutil.copy2(vendor_root, target)
        return target

    leaf = Path(catalog_path).name
    candidate = vendor_root / leaf if (vendor_root / leaf).exists() else vendor_root
    if candidate.is_file():
        target = dest_path / candidate.name
        shutil.copy2(candidate, target)
        return target

    if candidate.is_dir():
        for src in candidate.rglob("*"):
            if src.is_file():
                rel = src.relative_to(candidate)
                target = dest_path / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
        return dest_path / leaf if (dest_path / leaf).exists() else dest_path

    raise FileNotFoundError(f"vendir sync produced no files for {catalog_path}")


def fetch_bytes(catalog_path: str, *, ref: str | None = None) -> bytes:
    """Fetch catalog file bytes (local copy or vendir temp sync)."""
    catalog_path = catalog_path.strip().strip("/")
    local = catalog_root()
    if local is not None:
        src = local / catalog_path
        if src.is_file():
            return src.read_bytes()
        if src.is_dir():
            files = [p for p in sorted(src.rglob("*")) if p.is_file()]
            if len(files) == 1:
                return files[0].read_bytes()
            raise IsADirectoryError(
                f"catalog path is a directory with multiple files: {catalog_path}"
            )
        raise FileNotFoundError(catalog_path)

    tmp = Path(tempfile.mkdtemp(prefix="ut-vendir-fetch-"))
    try:
        name = "content"
        write_vendir_config(
            [{"name": name, "path": catalog_path, "dest": "out", "ref": ref}],
            dest_dir=tmp,
        )
        sync(tmp)
        root = tmp / "out" / name
        if root.is_file():
            return root.read_bytes()
        if not root.exists():
            root = tmp / "out"
        files = [p for p in sorted(root.rglob("*")) if p.is_file()] if root.is_dir() else []
        if len(files) == 1:
            return files[0].read_bytes()
        leaf = Path(catalog_path).name
        for f in files:
            if f.name == leaf:
                return f.read_bytes()
        raise FileNotFoundError(f"no file fetched for {catalog_path}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
