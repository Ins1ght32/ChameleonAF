#!/usr/bin/env python3
"""
compile_engine.py

- Scans feature sources (*.java) in modules/features
- Compiles a selected Java feature -> smali (flat copy to modules/injects)
- Records metadata in SQLite (modules/features_index.db)
- All tool paths are sourced from modules/settings_manager.py.
  If a setting is blank, we fall back to environment variables or PATH/JAVA_HOME.

UI should call ONLY the public API at the bottom.
"""

import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

# ---- Settings loader (must exist in modules/) ----
try:
    # if used as package (recommended)
    from . import settings_manager  # loads/saves config/user_settings.json
except Exception:
    # fallback if imported as a plain script
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "settings_manager", str(Path(__file__).resolve().parent / "settings_manager.py")
    )
    settings_manager = importlib.util.module_from_spec(spec)  # type: ignore
    assert spec and spec.loader
    spec.loader.exec_module(settings_manager)  # type: ignore

# ----------------------------- Layout/Paths -----------------------------
ROOT_DIR = Path(".").resolve()
MODULES_DIR = ROOT_DIR / "modules"

FEATURES_DIR = MODULES_DIR / "features"  # raw Java
WORK_DIR = MODULES_DIR / "work"  # temp workspace
INJECTS_DIR = MODULES_DIR / "injects"  # final smali outputs
TOOLS_DIR = MODULES_DIR / "tools"  # 3rd party jars/bins
INDEX_DB = MODULES_DIR / "features_index.db"

TARGET_DECL_RE = re.compile(
    r'(private\s+static\s+final\s+String\s+TARGET_PACKAGE\s*=\s*")([^"]*)(";\s*)'
)


# ----------------------------- Dataclasses -----------------------------
@dataclass
class EngineConfig:
    features_dir: Path = FEATURES_DIR
    injects_dir: Path = INJECTS_DIR
    index_db: Path = INDEX_DB

    # Tools resolved at compile time from settings/env/PATH
    android_jar: Path | None = None
    d8_path: Path | None = None
    baksmali_jar: Path | None = None
    javac: str | None = None
    java: str | None = None


@dataclass
class CompileMeta:
    name: str
    description: str
    requires_root: bool
    target_package_override: str = ""  # empty => do not modify source

    # NEW: compile-time permission metadata
    runtime_permissions: list[str] = field(default_factory=list)
    special_permissions: list[str] = field(default_factory=list)


# ----------------------------- Utilities -----------------------------
def _ts_now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _ensure_dirs(cfg: EngineConfig):
    cfg.features_dir.mkdir(parents=True, exist_ok=True)
    cfg.injects_dir.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)


def _log(logger, msg: str):
    if logger:
        logger(msg)


def _resolve_tool_path(name: str, explicit: str | None) -> str:
    """
    Resolve a tool path using (1) settings.json, (2) env, (3) PATH / JAVA_HOME.
    name: logical name, also the executable to search on PATH.
    """
    if explicit and str(explicit).strip():
        return str(explicit)

    # environment variable direct
    env_val = os.getenv(name.upper())
    if env_val and os.path.exists(env_val):
        return env_val

    # PATH / JAVA_HOME (javac/java)
    if name.lower() in ("javac", "java"):
        # Try direct on PATH first
        which = shutil.which(name)
        if which:
            return which
        # Try JAVA_HOME/bin
        jh = os.getenv("JAVA_HOME")
        if jh:
            cand = os.path.join(jh, "bin", f"{name}.exe" if os.name == "nt" else name)
            if os.path.exists(cand):
                return cand
    else:
        # generic PATH for others
        which = shutil.which(name)
        if which:
            return which

    # Windows common locations for javac/java fallbacks
    if name.lower() in ("javac", "java"):
        common_bases = (
            r"C:\Program Files\Java",
            r"C:\Program Files\Eclipse Adoptium",
            r"C:\Program Files\Microsoft",
        )
        for base in common_bases:
            try:
                for entry in os.listdir(base):
                    if entry.lower().startswith("jdk"):
                        cand = os.path.join(base, entry, "bin", f"{name}.exe")
                        if os.path.exists(cand):
                            return cand
            except FileNotFoundError:
                continue

    raise FileNotFoundError(f"Could not find {name}. Set it in settings or ensure it's on PATH/JAVA_HOME.")


def _detect_javac_major(javac_path: str) -> int:
    out = subprocess.check_output([javac_path, "-version"], stderr=subprocess.STDOUT, text=True).strip()
    m = re.search(r"javac\s+(\d+)", out)
    return int(m.group(1)) if m else 17


def _infer_package_name(java_src_text: str) -> str:
    m = re.search(r'^\s*package\s+([a-zA-Z0-9_.]+)\s*;\s*$', java_src_text, re.M)
    return m.group(1) if m else ""


def _read_target_package_from_text(java_src_text: str) -> str:
    m = TARGET_DECL_RE.search(java_src_text)
    return m.group(2).strip() if m else ""


def _replace_target_package(java_path: Path, new_pkg: str, logger=None) -> str:
    if not new_pkg.strip():
        return java_path.read_text(encoding="utf-8", errors="ignore")
    s = java_path.read_text(encoding="utf-8", errors="ignore")
    new_s, n = TARGET_DECL_RE.subn(r'\1' + new_pkg + r'\3', s, count=1)
    if n == 0:
        _log(logger, "[warn] TARGET_PACKAGE constant not found; no replacement made.")
        return s
    java_path.write_text(new_s, encoding="utf-8")
    _log(logger, f"[info] Replaced TARGET_PACKAGE -> {new_pkg}")
    return new_s


def _rel_path_from_root(p: Path) -> str:
    """
    Converts an absolute path to a relative path from project root.
    If not under root, returns the absolute path as fallback.
    """
    try:
        return str(p.resolve().relative_to(ROOT_DIR.resolve()))
    except ValueError:
        return str(p.resolve())

def detect_feature_requires_root(java_path: str) -> bool:
    """
    Heuristic scan of a feature source for likely root / su usage.
    Returns True if root-like indicators are found, else False.
    """
    try:
        p = Path(java_path)
        if not p.is_absolute():
            p = (ROOT_DIR / java_path).resolve()

        text = p.read_text(encoding="utf-8", errors="ignore")
        text_l = text.lower()

        indicators = [
            'runtime.getruntime().exec("su")',
            "runtime.getruntime().exec('su')",
            'processbuilder("su")',
            "processbuilder('su')",
            " shell.su",
            "shell.su.",
            "/system/xbin/su",
            "/system/bin/su",
            '"/su"',
            "'/su'",
            '"su"',
            "'su'",
            ".exec(\"su\")",
            ".exec('su')",
            "requiresroot()",
            "android.uid.system",
            "libsuperuser",
            "magisk",
            "busybox su",
            "which su",
            "command su",
        ]

        for needle in indicators:
            if needle in text_l:
                return True

        # Slightly safer regex checks for common su command patterns
        regexes = [
            r'\bexec\s*\(\s*"su"\s*\)',
            r"\bexec\s*\(\s*'su'\s*\)",
            r'\bnew\s+processbuilder\s*\(\s*"su"\s*\)',
            r"\bnew\s+processbuilder\s*\(\s*'su'\s*\)",
            r'\bString\s*\[\s*\]\s*\w*\s*=\s*\{[^}]*"su"[^}]*\}',
            r"\bString\s*\[\s*\]\s*\w*\s*=\s*\{[^}]*'su'[^}]*\}",
        ]

        for pat in regexes:
            if re.search(pat, text, re.I | re.S):
                return True

        return False
    except Exception:
        return False


# ----------------------------- DB ------------------------------------
def _init_db(cfg: EngineConfig):
    _ensure_dirs(cfg)
    conn = sqlite3.connect(cfg.index_db)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                requires_root INTEGER DEFAULT 0,
                compiled_date TEXT,
                java_path TEXT NOT NULL UNIQUE,
                smali_paths TEXT,  -- JSON array
                status TEXT,

                -- NEW (permissions)
                runtime_permissions TEXT,  -- JSON array
                special_permissions TEXT   -- JSON array
            )
            """
        )

        # ---- lightweight migration for existing DBs ----
        cur = conn.execute("PRAGMA table_info(features)")
        existing_cols = {row[1] for row in cur.fetchall()}  # row[1] = column name

        if "runtime_permissions" not in existing_cols:
            conn.execute("ALTER TABLE features ADD COLUMN runtime_permissions TEXT")
        if "special_permissions" not in existing_cols:
            conn.execute("ALTER TABLE features ADD COLUMN special_permissions TEXT")

    conn.close()



def _upsert_feature_record(cfg: EngineConfig, rec: Dict):
    conn = sqlite3.connect(cfg.index_db)
    with conn:
        conn.execute(
            """
            INSERT INTO features (
                name, description, requires_root, compiled_date, java_path, smali_paths, status,
                runtime_permissions, special_permissions
            )
            VALUES (
                :name, :description, :requires_root, :compiled_date, :java_path, :smali_paths, :status,
                :runtime_permissions, :special_permissions
            )
            ON CONFLICT(java_path) DO UPDATE SET
                name=excluded.name,
                description=excluded.description,
                requires_root=excluded.requires_root,
                compiled_date=excluded.compiled_date,
                smali_paths=excluded.smali_paths,
                status=excluded.status,
                runtime_permissions=excluded.runtime_permissions,
                special_permissions=excluded.special_permissions
            """,
            rec,
        )
    conn.close()


def _list_indexed_features(cfg: EngineConfig) -> List[Dict]:
    _ensure_dirs(cfg)
    conn = sqlite3.connect(cfg.index_db)
    rows = []
    with conn:
        cur = conn.execute("""
            SELECT name, description, requires_root, compiled_date, java_path, smali_paths, status, runtime_permissions, special_permissions
            FROM features
            ORDER BY (compiled_date IS NULL), compiled_date DESC
        """)
        for (name, description, requires_root, compiled_date, java_path, smali_paths, status,
             runtime_permissions, special_permissions) in cur.fetchall():
            rows.append({
                "name": name,
                "description": description,
                "requires_root": bool(requires_root),
                "compiled_date": compiled_date,
                "java_path": java_path,
                "smali_paths": smali_paths,
                "status": status,
                "runtime_permissions": runtime_permissions,
                "special_permissions": special_permissions,
            })
    conn.close()
    return rows


def delete_indexed_feature(java_path: str) -> bool:
    """Delete a feature record and its associated smali output (if exists)."""
    cfg = EngineConfig()
    _ensure_dirs(cfg)

    conn = sqlite3.connect(cfg.index_db)
    try:
        cur = conn.execute("SELECT smali_paths FROM features WHERE java_path = ?", (java_path,))
        row = cur.fetchone()
        if not row:
            return False

        smali_paths = json.loads(row[0] or "[]")
        for sp in smali_paths:
            smali_dir = cfg.injects_dir / Path(sp).parts[0]
            if smali_dir.exists():
                shutil.rmtree(smali_dir, ignore_errors=True)

        conn.execute("DELETE FROM features WHERE java_path = ?", (java_path,))
        conn.commit()
        return True
    finally:
        conn.close()


# ----------------------------- Source Scanner -----------------------------
def _scan_feature_sources(cfg: EngineConfig) -> List[Dict]:
    _ensure_dirs(cfg)
    items = []
    for p in cfg.features_dir.rglob("*.java"):
        items.append({
            "label": p.name,
            "path": str(p.resolve()),
            "name_hint": p.stem
        })
    items.sort(key=lambda x: x["label"].lower())
    return items


# ----------------------------- UI metadata helpers ------------------------
def _is_antiagent_filename(java_path_or_label: str) -> bool:
    return os.path.basename(java_path_or_label).strip().lower() == "antiagent.java"


def _read_file_text(p: str | Path) -> str:
    return Path(p).resolve().read_text(encoding="utf-8", errors="ignore")


def get_feature_ui_metadata(java_path: str) -> Dict:
    """
    Returns UI-driving metadata for a given feature source, so the TAB never reads files itself.
    {
      "requires_agent_name": bool,
      "initial_target_package": str
    }
    """
    requires_agent_name = _is_antiagent_filename(java_path)
    initial_pkg = ""
    try:
        txt = _read_file_text(ROOT_DIR / java_path)
        initial_pkg = _read_target_package_from_text(txt) if requires_agent_name else ""
    except Exception:
        initial_pkg = ""
    return {
        "requires_agent_name": requires_agent_name,
        "initial_target_package": initial_pkg
    }


# ----------------------------- Compiler Core -----------------------------
def _compile_feature_to_smali(
        cfg: EngineConfig,
        java_file_path: str,
        meta: CompileMeta,
        logger: Optional[Callable[[str], None]] = None,
        progress: Optional[Callable[[int], None]] = None
) -> Dict:
    """
    Compile a selected Java feature -> smali; copy smali into modules/injects/<feature>_YYYYmmddHHMMSS/
    """
    _ensure_dirs(cfg)

    # Load tools lazily
    settings = settings_manager.load_settings()
    android_jar = settings.get("android_jar") or ""
    d8 = settings.get("d8") or ""
    baksmali = settings.get("baksmali_jar") or ""
    javac = settings.get("javac") or ""
    java_bin = settings.get("java") or ""

    cfg.android_jar = Path(android_jar) if android_jar else None
    cfg.d8_path = Path(d8) if d8 else None
    cfg.baksmali_jar = Path(baksmali) if baksmali else None
    cfg.javac = javac or None
    cfg.java = java_bin or None

    # Resolve tool paths (fallbacks to PATH/JAVA_HOME)
    javac_path = _resolve_tool_path("javac", cfg.javac)
    java_bin = _resolve_tool_path("java", cfg.java)
    android_jar_path = str(cfg.android_jar) if cfg.android_jar else _resolve_tool_path("android.jar",
                                                                                       None)  # allow explicit jar or env mapping
    d8_path = str(cfg.d8_path) if cfg.d8_path else _resolve_tool_path("d8", None)
    baksmali_jar_path = str(cfg.baksmali_jar) if cfg.baksmali_jar else _resolve_tool_path("baksmali.jar", None)

    if progress: progress(5)

    # Workspace
    tdir = Path(tempfile.mkdtemp(prefix="featbuild_", dir=WORK_DIR))
    build_src = tdir / "src"
    build_bin = tdir / "bin"
    build_src.mkdir(parents=True, exist_ok=True)
    build_bin.mkdir(parents=True, exist_ok=True)

    # Copy feature source tree (if inside features dir, preserve structure; else flatten)
    java_path = Path(java_file_path)
    if not java_path.exists():
        raise FileNotFoundError(f"Source not found: {java_file_path}")

    # Copy features tree to build/src
    shutil.copytree(FEATURES_DIR, build_src, dirs_exist_ok=True)

    # If selected file is outside features dir, just drop it at root
    if not str(java_path.resolve()).startswith(str(FEATURES_DIR.resolve())):
        shutil.copy2(java_path, build_src / java_path.name)

    # Identify the copied file representative
    try:
        chosen_copy = build_src / java_path.resolve().relative_to(FEATURES_DIR.resolve())
    except ValueError:
        # outside tree; fallback by filename
        matches = list(build_src.rglob(java_path.name))
        if not matches:
            raise FileNotFoundError("Could not map selected file into build tree.")
        chosen_copy = matches[0]

    # Ensure requiresRoot() exists and matches the checkbox (workspace copy only)
    patch_or_inject_requires_root(chosen_copy, meta.requires_root, logger=logger)

    # Target package override (optional, only applied if provided)
    updated_src = _replace_target_package(chosen_copy, meta.target_package_override, logger=logger)

    java_pkg = _infer_package_name(updated_src)
    if not java_pkg:
        raise RuntimeError("Could not infer Java package from source.")

    # Only compile the chosen file
    java_sources = [str(chosen_copy)]
    if not java_sources:
        raise RuntimeError("No Java sources found under build tree.")

    # javac
    if progress: progress(25)
    maj = _detect_javac_major(javac_path)
    javac_cmd = [javac_path]
    if maj >= 9:
        javac_cmd += [
                         "--release", "8",
                         "-classpath", android_jar_path,
                         "-d", str(build_bin),
                     ] + java_sources
    else:
        javac_cmd += ["-source", "1.8", "-target", "1.8", "-classpath", android_jar_path, "-d",
                      str(build_bin)] + java_sources

    _log(logger, "[cmd] " + " ".join(javac_cmd))
    proc = subprocess.run(javac_cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        _log(logger, "[javac stdout] " + proc.stdout)
        _log(logger, "[javac stderr] " + proc.stderr)
        raise RuntimeError(f"javac failed with exit code {proc.returncode}")

    # d8
    if progress: progress(45)
    class_files = [str(p) for p in build_bin.rglob("*.class")]
    if not class_files:
        raise RuntimeError("javac produced no .class files.")
    dexout = tdir / "dexout"
    dexout.mkdir(parents=True, exist_ok=True)
    d8_cmd = [str(d8_path), "--output", str(dexout)] + class_files
    _log(logger, "[cmd] " + " ".join(d8_cmd))
    subprocess.check_call(d8_cmd)

    # baksmali
    if progress: progress(65)
    classes_dex = dexout / "classes.dex"
    if not classes_dex.exists():
        raise RuntimeError("d8 did not output classes.dex")
    smali_out = tdir / "smali"
    smali_out.mkdir(exist_ok=True)
    bak_cmd = [str(java_bin), "-jar", str(baksmali_jar_path), "d", str(classes_dex), "-o", str(smali_out)]
    _log(logger, "[cmd] " + " ".join(bak_cmd))
    subprocess.check_call(bak_cmd)

    # Copy smali into injects dir under timestamped folder
    if progress: progress(80)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    out_dir = INJECTS_DIR / f"{Path(java_file_path).stem}_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    copied = []
    for item in smali_out.rglob("*.smali"):
        rel = item.relative_to(smali_out)
        dest = out_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
        copied.append(str(dest.relative_to(INJECTS_DIR)))

    # Index record
    if progress: progress(95)
    status = f"compiled -> {out_dir.name}"
    record = {
        "name": meta.name or Path(java_file_path).stem,
        "description": meta.description or "",
        "requires_root": 1 if meta.requires_root else 0,
        "compiled_date": _ts_now(),
        "java_path": _rel_path_from_root(Path(java_file_path)),
        "smali_paths": json.dumps(copied),
        "status": status,

        # NEW: permissions (store as JSON arrays)
        "runtime_permissions": json.dumps(meta.runtime_permissions or []),
        "special_permissions": json.dumps(meta.special_permissions or []),
    }
    _upsert_feature_record(cfg, record)
    _log(logger, f"[✓] {status}")
    return record

def list_compiled_versions(java_path: str) -> list[str]:
    """
    Given a java_path (relative or absolute), return all compiled smali folders
    in modules/injects/ that match the filename prefix (e.g., AntiAgent_*)
    """
    base_name = Path(java_path).stem
    injects_dir = EngineConfig().injects_dir
    if not injects_dir.exists():
        return []

    versions = [
        f.name for f in injects_dir.iterdir()
        if f.is_dir() and f.name.startswith(base_name + "_")
    ]
    versions.sort(reverse=True)
    return versions


def switch_active_version(java_path: str, version_folder: str):
    cfg = EngineConfig()
    injects_dir = cfg.injects_dir
    target_dir = injects_dir / version_folder
    if not target_dir.exists():
        raise FileNotFoundError(f"Compiled folder not found: {version_folder}")

    smali_files = list(target_dir.rglob("*.smali"))
    if not smali_files:
        raise RuntimeError("Selected folder contains no .smali files.")

    rel_paths = [str(f.relative_to(injects_dir)) for f in smali_files]
    status = f"Manual Switch -> {version_folder}"

    # Preserve existing fields
    java_rel = _rel_path_from_root(Path(java_path))
    conn = sqlite3.connect(cfg.index_db)
    try:
        cur = conn.execute(
            """
            SELECT name, description, requires_root,
                   runtime_permissions, special_permissions
            FROM features
            WHERE java_path = ?
            """,
            (java_rel,),
        )

        row = cur.fetchone()
        if not row:
            raise RuntimeError("Feature not indexed yet; compile first.")

        name, description, requires_root, runtime_permissions, special_permissions = row
    finally:
        conn.close()

    record = {
        "name": name,
        "description": description,
        "requires_root": int(bool(requires_root)),
        "compiled_date": _ts_now(),
        "java_path": java_rel,
        "smali_paths": json.dumps(rel_paths),
        "status": status,
        "runtime_permissions": runtime_permissions or json.dumps([]),
        "special_permissions": special_permissions or json.dumps([]),
    }
    _upsert_feature_record(cfg, record)


def _preserving_switch(java_path: str, version_folder: str, status_prefix: str):
    """Internal: switch while preserving description/requires_root/name."""
    cfg = EngineConfig()
    injects_dir = cfg.injects_dir
    target_dir = injects_dir / version_folder
    if not target_dir.exists():
        raise FileNotFoundError(f"Compiled folder not found: {version_folder}")

    smali_files = list(target_dir.rglob("*.smali"))
    if not smali_files:
        raise RuntimeError("Selected folder contains no .smali files.")

    rel_paths = [str(f.relative_to(injects_dir)) for f in smali_files]
    status = f"{status_prefix} -> {version_folder}"

    java_rel = _rel_path_from_root(Path(java_path))
    conn = sqlite3.connect(cfg.index_db)
    try:
        cur = conn.execute(
            """
            SELECT name, description, requires_root,
                   runtime_permissions, special_permissions
            FROM features
            WHERE java_path = ?
            """,
            (java_rel,),
        )
        row = cur.fetchone()
        if not row:
            return  # Nothing to preserve/switch

        name, description, requires_root, runtime_permissions, special_permissions = row
    finally:
        conn.close()

    record = {
        "name": name,
        "description": description,
        "requires_root": int(bool(requires_root)),
        "compiled_date": _ts_now(),
        "java_path": java_rel,
        "smali_paths": json.dumps(rel_paths),
        "status": status,
        "runtime_permissions": runtime_permissions or json.dumps([]),
        "special_permissions": special_permissions or json.dumps([]),
    }
    _upsert_feature_record(cfg, record)


def delete_compiled_version_folder(version_folder: str):
    """
    Deletes the folder inside modules/injects/ corresponding to a compiled version.
    If any feature currently points at this version, automatically fall back to the
    next latest compiled version and set status to 'Fallback Switch -> <version>'.
    If no other versions exist, the record is left with empty smali_paths and an
    'inactive' status (description is preserved).
    """
    cfg = EngineConfig()
    injects_dir = cfg.injects_dir
    target = injects_dir / version_folder
    if not target.exists():
        raise FileNotFoundError(f"No such compiled folder: {version_folder}")

    # Identify impacted feature records BEFORE deletion.
    impacted = []
    all_recs = _list_indexed_features(cfg)
    for rec in all_recs:
        try:
            paths = json.loads(rec.get("smali_paths") or "[]")
        except Exception:
            paths = []
        if any((Path(p).parts[0] if Path(p).parts else "") == version_folder for p in paths):
            impacted.append(rec)

    # Delete the folder.
    shutil.rmtree(target)

    # For each impacted feature, attempt fallback.
    for rec in impacted:
        java_path = rec["java_path"]
        java_rel = _rel_path_from_root(Path(java_path))
        # Find the next latest compiled folder for this feature (excluding the one we just deleted).
        versions = list_compiled_versions(java_path)
        versions = [v for v in versions if v != version_folder]
        if versions:
            next_ver = versions[0]  # already sorted newest-first
            _preserving_switch(java_path, next_ver, status_prefix="Fallback Switch")
        else:
            # No fallback available: preserve description/etc, clear smali_paths and mark inactive.
            conn = sqlite3.connect(cfg.index_db)
            try:
                cur = conn.execute(
                    """
                    SELECT name, description, requires_root,
                           runtime_permissions, special_permissions
                    FROM features
                    WHERE java_path = ?
                    """,
                    (java_rel,),
                )
                row = cur.fetchone()
                if row:
                    name, description, requires_root, runtime_permissions, special_permissions = row
                    record = {
                        "name": name,
                        "description": description,
                        "requires_root": int(bool(requires_root)),
                        "compiled_date": _ts_now(),
                        "java_path": java_rel,
                        "smali_paths": json.dumps([]),
                        "status": "inactive (no compiled versions)",
                        "runtime_permissions": runtime_permissions or json.dumps([]),
                        "special_permissions": special_permissions or json.dumps([]),
                    }
                    _upsert_feature_record(cfg, record)
            finally:
                conn.close()

def patch_or_inject_requires_root(java_file: Path, requires_root: bool, logger=None) -> None:
    """
    Patch/inject requiresRoot() in the temp workspace copy of the feature source.
    Does NOT touch original user file.
    If requiresRoot not present, then patch according to checkbox. If it is then just patch the value accordingly.
    """

    REQUIRES_ROOT_METHOD_RE = re.compile(
        r"public\s+static\s+boolean\s+requiresRoot\s*\(\s*\)\s*\{.*?\}",
        re.S,
    )

    # tighter: only replace the return true/false inside requiresRoot() if present
    REQUIRES_ROOT_RETURN_RE = re.compile(
        r"(public\s+static\s+boolean\s+requiresRoot\s*\(\s*\)\s*\{.*?return\s+)(true|false)(\s*;.*?\})",
        re.S,
    )

    CLASS_END_BRACE_RE = re.compile(r"\}\s*$", re.S)

    desired = "true" if requires_root else "false"
    src = java_file.read_text(encoding="utf-8", errors="ignore")

    # Case 1: method exists -> just patch return true/false
    m = REQUIRES_ROOT_RETURN_RE.search(src)
    if m:
        patched = REQUIRES_ROOT_RETURN_RE.sub(rf"\g<1>{desired}\g<3>", src, count=1)
        java_file.write_text(patched, encoding="utf-8")
        if logger:
            logger(f"[*] requiresRoot() found -> set return {desired} in workspace copy: {java_file.name}")
        return

    # Case 1b: method exists but doesn't match our return regex (weird body) -> replace entire method
    if REQUIRES_ROOT_METHOD_RE.search(src):
        new_method = (
            "    /** Patched by controller at compile-time (workspace only) */\n"
            "    public static boolean requiresRoot() {\n"
            f"        return {desired};\n"
            "    }\n"
        )
        patched = REQUIRES_ROOT_METHOD_RE.sub(new_method.rstrip(), src, count=1)
        java_file.write_text(patched, encoding="utf-8")
        if logger:
            logger(f"[*] requiresRoot() found (complex) -> replaced with return {desired}: {java_file.name}")
        return

    # Case 2: method missing -> inject before final class brace
    new_method = (
        "\n"
        "    /** Injected by controller at compile-time (workspace only) */\n"
        "    public static boolean requiresRoot() {\n"
        f"        return {desired};\n"
        "    }\n"
    )

    if not CLASS_END_BRACE_RE.search(src):
        if logger:
            logger(f"[!] Could not inject requiresRoot() (no class closing brace): {java_file.name}")
        return

    injected = CLASS_END_BRACE_RE.sub(new_method + "}\n", src, count=1)
    java_file.write_text(injected, encoding="utf-8")
    if logger:
        logger(f"[*] requiresRoot() missing -> injected return {desired} into workspace copy: {java_file.name}")

# ----------------------------- Public API -----------------------------
# Read-only, UI-facing APIs now live in feature_api to avoid cross-tab coupling.
# Re-exported here for backward compatibility (optional).

from .feature_api import (
    init_engine,
    get_feature_sources,
    get_indexed_features,
    get_feature_ui_metadata,
)

def compile_selected_feature(
        java_path: str,
        meta: CompileMeta,
        logger=None,
        progress=None
) -> dict:
    """Compile the selected feature to smali and index it in SQLite."""
    cfg = EngineConfig()
    if progress: progress(100)
    return _compile_feature_to_smali(cfg, java_path, meta, logger, progress)

