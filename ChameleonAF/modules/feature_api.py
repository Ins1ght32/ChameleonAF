# modules/feature_api.py
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
import re

# ----------------------------- Layout/Paths -----------------------------
ROOT_DIR = Path(".").resolve()
MODULES_DIR = ROOT_DIR / "modules"

FEATURES_DIR = MODULES_DIR / "features"   # raw Java
INJECTS_DIR = MODULES_DIR / "injects"     # compiled smali outputs
WORK_DIR = MODULES_DIR / "work"           # temp workspace (not used here, but reserved)
TOOLS_DIR = MODULES_DIR / "tools"         # 3rd party jars/bins (not used here)
INDEX_DB = MODULES_DIR / "features_index.db"

TARGET_DECL_RE = re.compile(
    r'(private\s+static\s+final\s+String\s+TARGET_PACKAGE\s*=\s*")([^"]*)(";\s*)'
)

# ----------------------------- Utilities -----------------------------
def _ensure_dirs():
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    INJECTS_DIR.mkdir(parents=True, exist_ok=True)
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)

def _read_file_text(p: str) -> str:
    return Path(p).read_text(encoding="utf-8", errors="ignore")

def _read_target_package_from_text(java_src_text: str) -> str:
    m = TARGET_DECL_RE.search(java_src_text)
    return m.group(2).strip() if m else ""

def _is_antiagent_filename(java_path_or_label: str) -> bool:
    return os.path.basename(java_path_or_label).strip().lower() == "antiagent.java"

# ----------------------------- DB (read-only init/list) -----------------------------
def _init_db():
    _ensure_dirs()
    conn = sqlite3.connect(INDEX_DB)
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
        #Patch to ensure permissions are being handled
        cur = conn.execute("PRAGMA table_info(features)")
        existing_cols = {row[1] for row in cur.fetchall()}

        if "runtime_permissions" not in existing_cols:
            conn.execute("ALTER TABLE features ADD COLUMN runtime_permissions TEXT")

        if "special_permissions" not in existing_cols:
            conn.execute("ALTER TABLE features ADD COLUMN special_permissions TEXT")
    conn.close()

def _list_indexed_features() -> list[dict]:
    _ensure_dirs()
    rows: list[dict] = []
    conn = sqlite3.connect(INDEX_DB)
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

# ----------------------------- Source Scanner -----------------------------
def _scan_feature_sources() -> list[dict]:
    _ensure_dirs()
    items = []
    for p in FEATURES_DIR.rglob("*.java"):
        items.append({
            "label": p.name,
            "path": str(p.resolve()),
            "name_hint": p.stem
        })
    items.sort(key=lambda x: x["label"].lower())
    return items

# ----------------------------- Public UI-Facing API -----------------------------
def init_engine():
    """
    Initialize DB and required folders (idempotent).
    This is safe to call from any tab.
    """
    _init_db()

def get_feature_sources() -> list[dict]:
    """
    List available *.java feature sources (read-only).
    """
    return _scan_feature_sources()

def get_indexed_features() -> list[dict]:
    """
    Read indexed/compiled features from SQLite (read-only).
    """
    return _list_indexed_features()

def get_feature_ui_metadata(java_path: str) -> dict:
    """
    Returns UI-driving metadata for a given feature source, so tabs never read files themselves.
    {
      "show_target_package": bool,
      "initial_target_package": str
    }
    """
    show_target = _is_antiagent_filename(java_path)
    initial_pkg = ""
    try:
        txt = _read_file_text(java_path)
        if show_target:
            initial_pkg = _read_target_package_from_text(txt)
    except Exception:
        initial_pkg = ""
    return {
        "show_target_package": show_target,
        "initial_target_package": initial_pkg
    }
