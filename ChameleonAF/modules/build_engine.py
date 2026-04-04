#!/usr/bin/env python3
"""
build_engine.py

- Builds a new APK using selected compiled smali features
- Decompiles base APK, injects selected smali classes, patches manifest, and signs
- All tools and keystore paths are pulled from settings_manager
"""

import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from typing import Callable
import time

# ========== Settings Loader ==========
try:
    from . import settings_manager
except ImportError:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "settings_manager", str(Path(__file__).resolve().parent / "settings_manager.py")
    )
    settings_manager = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(settings_manager)

# ========== Constants ==========
#INJECTOR_PKG = "com.example.smaliinject"
INJECTOR_PKG = "com.chameleonforensics.chameleon"
APKTOOL_JAR = None
KEYSTORE_PATH = None
KEY_ALIAS = "androiddebugkey"
KEYSTORE_PASS = "android"
KEY_PASS = "android"
APKSIGNER = None
ZIPALIGN = None

# ========== Regex Patterns ==========
CLASS_RE = re.compile(r'\.class\b[^\n]*\bL(?P<desc>[^;]+);', re.M)
LABEL_RE = re.compile(r'^\s*\.field\s+public\s+static\s+final\s+LABEL:Ljava/lang/String;\s*=\s*"(?P<label>.*?)"', re.M)
RUN_SIG_RE = re.compile(r'\.method\s+public\s+static\s+run\(Landroid/app/Activity;\)V')
TARGET_RE = re.compile(
    r'\.field\s+private\s+static\s+final\s+TARGET_PACKAGE:Ljava/lang/String;\s*=\s*"(?P<target>[^"]+)"')
CLINIT_RE = re.compile(
    r"\.method\s+static\s+constructor\s+<clinit>\(\)V.*?"
    r"SPECIAL_PERMS_BY_FEATURE:\[\[Ljava/lang/String;.*?"
    r"\.end\s+method",
    re.S
)

# ========== Tooling Setup ==========
def run(cmd, check=True, log_fn=print):
    cmd = list(map(str, cmd))
    log_fn(">> " + " ".join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log_fn(proc.stdout)
    if check and proc.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")


def apktool_cmd(*args):
    return ["java", "-jar", str(APKTOOL_JAR), *map(str, args)]


def resolve_build_tools():
    global APKSIGNER, ZIPALIGN
    APKSIGNER = shutil.which("apksigner") or shutil.which("apksigner.bat")
    ZIPALIGN = shutil.which("zipalign") or shutil.which("zipalign.exe")
    if not (APKSIGNER and ZIPALIGN):
        raise RuntimeError("Missing build-tools (apksigner / zipalign). Check PATH.")


def ensure_tools():
    global APKTOOL_JAR, KEYSTORE_PATH
    settings = settings_manager.load_settings()
    APKTOOL_JAR = Path(settings.get("apktool_path") or "apktool.jar")
    KEYSTORE_PATH = Path(settings.get("debug_keystore") or Path.home() / ".android" / "debug.keystore")
    if not APKTOOL_JAR.exists():
        raise RuntimeError(f"[!] apktool.jar not found: {APKTOOL_JAR}")
    if not KEYSTORE_PATH.exists():
        raise RuntimeError(f"[!] Debug keystore not found: {KEYSTORE_PATH}")
    resolve_build_tools()


# ========== Helpers ==========
def force_delete_dir(path, max_retries=5, delay=0.5):
    import stat

    def remove_readonly(func, path, exc):
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except Exception:
            pass

    path = str(path)
    if os.name == 'nt' and not path.startswith('\\\\?\\'):
        path = '\\?\\' + os.path.abspath(path)

    for attempt in range(max_retries):
        try:
            shutil.rmtree(path, onerror=remove_readonly)
            return
        except Exception as e:
            if attempt == max_retries - 1:
                raise
        time.sleep(delay)


def smali_root(out_dir):
    return out_dir / "smali"


def decompile(apk, out_dir, log_fn):
    if out_dir.exists():
        force_delete_dir(str(out_dir))
    run(apktool_cmd("d", "-f", apk, "-o", out_dir), log_fn=log_fn)


def parse_feature_info(smali_path):
    text = smali_path.read_text(encoding="utf-8", errors="ignore")
    if text and text[0] == "\ufeff":
        text = text[1:]
    m = CLASS_RE.search(text)
    if not m:
        return None
    desc = m.group("desc")
    return {
        "desc": desc,
        "java": desc.replace('/', '.'),
        "label": LABEL_RE.search(text).group("label") if LABEL_RE.search(text) else None,
        "has_run": RUN_SIG_RE.search(text) is not None,
        "target": TARGET_RE.search(text).group("target") if TARGET_RE.search(text) else None
    }


def copy_smali(src, out_root, desc):
    if not src.exists():
        raise FileNotFoundError(f"[!] copy_smali: source does not exist → {src}")
    dst = out_root / Path(desc + ".smali")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


# ========== Manifest and Registry ==========
def patch_manifest(out_dir, targets, permissions, log_fn):
    path = out_dir / "AndroidManifest.xml"
    if not path.exists():
        log_fn("[!] AndroidManifest.xml not found")
        return

    txt = path.read_text(encoding="utf-8")

    # Insert point before <application ...>
    idx = txt.find("<application")
    if idx == -1:
        log_fn("[!] <application> tag not found in AndroidManifest.xml")
        return

    # ---- Inject permissions (ONLY what is requested) ----
    permissions = permissions or []
    injected_any = False
    for perm in permissions:
        perm = (perm or "").strip()
        if not perm:
            continue
        needle = f'android:name="{perm}"'
        if needle not in txt:
            txt = txt[:idx] + f'\n<uses-permission android:name="{perm}" />\n' + txt[idx:]
            idx = txt.find("<application")  # recompute because we changed the text
            injected_any = True

    # ---- Inject <queries> block if targets exist ----
    if targets and "<queries>" not in txt:
        block = ["<queries>\n"] + [f'<package android:name="{pkg}" />\n' for pkg in sorted(targets)] + ["</queries>\n"]
        txt = txt[:idx] + "".join(block) + txt[idx:]

    path.write_text(txt, encoding="utf-8")

    if injected_any or targets:
        log_fn("[*] Manifest patched")
    else:
        log_fn("[*] Manifest unchanged (no permissions/queries requested)")


def generate_feature_registry(out_dir, entries, log_fn):
    dst = smali_root(out_dir) / Path(INJECTOR_PKG.replace('.', '/')) / "FeatureRegistry.smali"
    dst.parent.mkdir(parents=True, exist_ok=True)

    def array_block(field, values):
        lines = [
            f"    const/4 v0, 0x{len(values):x}",
            "    new-array v1, v0, [Ljava/lang/String;"
        ]
        for i, val in enumerate(values):
            lines += [
                f"    const/4 v2, 0x{i:x}",
                f'    const-string v3, "{val}"',
                "    aput-object v3, v1, v2"
            ]
        lines.append(
            f"    sput-object v1, L{INJECTOR_PKG.replace('.', '/')}/FeatureRegistry;->{field}:[Ljava/lang/String;"
        )
        return "\n".join(lines)

    content = f""".class public L{INJECTOR_PKG.replace('.', '/')}/FeatureRegistry;
        .super Ljava/lang/Object;
        
        .field public static featureClasses:[Ljava/lang/String;
        .field public static featureLabels:[Ljava/lang/String;
        
        .method static constructor <clinit>()V
            .locals 4
        
        {array_block("featureClasses", [cls for cls, _ in entries])}
        
        {array_block("featureLabels", [lbl for _, lbl in entries])}
        
            return-void
        .end method
        """
    dst.write_text(content, encoding="utf-8")
    log_fn("[*] FeatureRegistry written")


def patch_special_feature_requirements(out_dir: Path, special_by_feature: dict[str, list[str]], log_fn):
    """
    Patches out/smali/<INJECTOR_PKG>/SpecialFeatureRequirements.smali so that
    SPECIAL_PERMS_BY_FEATURE is populated as:
      [
        ["com.xxx.FeatureA", "perm1", "perm2"],
        ["com.xxx.FeatureB", "permX"],
      ]
    """
    rel = Path(INJECTOR_PKG.replace(".", "/")) / "SpecialFeatureRequirements.smali"

    candidates = sorted(out_dir.glob(str(Path("smali*") / rel)))
    if not candidates:
        log_fn(f"[!] SpecialFeatureRequirements.smali not found in any smali* folder: {rel}")
        return

    smali_path = candidates[0]
    log_fn(f"[*] Patching SpecialFeatureRequirements at: {smali_path}")

    if not smali_path.exists():
        log_fn(f"[!] SpecialFeatureRequirements.smali not found: {smali_path}")
        return

    # Dedup perms per feature, keep deterministic ordering
    rows: list[tuple[str, list[str]]] = []
    for cls, perms in (special_by_feature or {}).items():
        cls = (cls or "").strip()
        if not cls:
            continue
        seen = set()
        clean = []
        for p in perms or []:
            p = (p or "").strip()
            if p and p not in seen:
                seen.add(p)
                clean.append(p)
        if clean:
            rows.append((cls, clean))

    desc_pkg = INJECTOR_PKG.replace(".", "/")

    if not rows:
        clinit = f"""
        .method static constructor <clinit>()V
            .locals 1

            const/4 v0, 0x0
            new-array v0, v0, [[Ljava/lang/String;

            sput-object v0, L{desc_pkg}/SpecialFeatureRequirements;->SPECIAL_PERMS_BY_FEATURE:[[Ljava/lang/String;

            return-void
        .end method
        """.strip()
    else:
        lines = []
        lines.append(".method static constructor <clinit>()V")
        lines.append("    .locals 6")
        lines.append("")
        lines.append(f"    const/4 v0, 0x{len(rows):x}")
        lines.append("    new-array v1, v0, [[Ljava/lang/String;")
        lines.append("")

        for i, (cls, perms) in enumerate(rows):
            m = 1 + len(perms)  # class name + perms
            lines.append(f"    const/4 v2, 0x{i:x}")
            lines.append(f"    const/4 v0, 0x{m:x}")
            lines.append("    new-array v3, v0, [Ljava/lang/String;")
            lines.append("")
            # [0] = class name
            lines.append("    const/4 v4, 0x0")
            lines.append(f'    const-string v5, "{cls}"')
            lines.append("    aput-object v5, v3, v4")
            lines.append("")
            # [1..] perms
            for j, p in enumerate(perms, start=1):
                lines.append(f"    const/4 v4, 0x{j:x}")
                lines.append(f'    const-string v5, "{p}"')
                lines.append("    aput-object v5, v3, v4")
            lines.append("")
            # add row to 2D array
            lines.append("    aput-object v3, v1, v2")
            lines.append("")

        lines.append(f"    sput-object v1, L{desc_pkg}/SpecialFeatureRequirements;->SPECIAL_PERMS_BY_FEATURE:[[Ljava/lang/String;")
        lines.append("")
        lines.append("    return-void")
        lines.append(".end method")

        clinit = "\n".join(lines)

    txt = smali_path.read_text(encoding="utf-8", errors="ignore")
    if not CLINIT_RE.search(txt):
        log_fn("[!] <clinit>() not found in SpecialFeatureRequirements.smali. Not patching.")
        return

    txt2 = CLINIT_RE.sub(clinit, txt, count=1)

    log_fn(f"[*] Patching file: {smali_path}")
    log_fn(f"[*] Rows to write: {rows}")

    txt = smali_path.read_text(encoding="utf-8", errors="ignore")
    m = CLINIT_RE.search(txt)
    log_fn(f"[*] CLINIT_RE match: {'YES' if m else 'NO'}")

    if not m:
        log_fn("[!] <clinit>() not found in SpecialFeatureRequirements.smali. Not patching.")
        return

    txt2 = CLINIT_RE.sub(clinit, txt, count=1)
    smali_path.write_text(txt2, encoding="utf-8")

    # Immediately re-read to confirm it actually changed
    verify = smali_path.read_text(encoding="utf-8", errors="ignore")
    log_fn(f"[*] After patch, contains className const-string? {'const-string' in verify}")
    log_fn(f"[*] Patched SpecialFeatureRequirements for {len(rows)} feature(s)")


# ========== Rebuild & Install ==========
def rebuild_sign_install_run(out_dir, signed_apk, app_id, do_run, log_fn):
    with tempfile.TemporaryDirectory() as td:
        unsigned = Path(td) / "mod-unsigned.apk"
        aligned = Path(td) / "mod-aligned.apk"
        run(apktool_cmd("b", out_dir, "-o", unsigned), log_fn=log_fn)
        run([ZIPALIGN, "-p", "-f", "4", str(unsigned), str(aligned)], log_fn=log_fn)
        run([
            APKSIGNER, "sign",
            "--ks", str(KEYSTORE_PATH),
            "--ks-pass", f"pass:{KEYSTORE_PASS}",
            "--key-pass", f"pass:{KEY_PASS}",
            "--out", str(signed_apk),
            str(aligned)
        ], log_fn=log_fn)
        run([APKSIGNER, "verify", str(signed_apk)], log_fn=log_fn)
    if do_run:
        run(["adb", "install", "-r", str(signed_apk)], log_fn=log_fn)
        #run(["adb", "shell", "am", "start", "-n", f"{app_id}/.MainActivity"], log_fn=log_fn)
        run([
            "adb", "shell", "am", "start",
            "-n", f"{app_id}/.MainActivity",
            "--ez", "autorun", "true"
        ], log_fn=log_fn)


# ========== Public Entry Point ==========
def run_build_from_ui(smali_paths, base_apk, app_id, version, log_fn,
                      do_run=False, runtime_permissions=None, special_permissions=None,
                      special_perms_by_smali=None):
    """
    Build flow:
      1) Decompile base APK
      2) Copy selected smali (and any sibling $Inner*.smali) into out/smali/...
      3) Collect feature entries (class + label) and targets for manifest <queries>
      4) Patch manifest and generate FeatureRegistry
      5) Rebuild, align, sign, and (optionally) install+launch
    """
    try:
        ensure_tools()

        out_dir = Path("out")
        log_fn("[*] Decompiling base APK…")
        decompile(base_apk, out_dir, log_fn)

        out_smali = smali_root(out_dir)
        entries: list[tuple[str, str]] = []
        targets: set[str] = set()
        special_by_feature_java: dict[str, list[str]] = {}

        for smali in smali_paths:
            # Ensure Path
            smali = Path(smali)

            # Skip anything not a top-level class file
            if smali.suffix.lower() != ".smali":
                log_fn(f"[!] Skipping non-smali input: {smali}")
                continue
            if "$" in smali.stem:
                # We copy inner classes ourselves from the main's directory
                log_fn(f"[!] Skipping inner class passed directly: {smali}")
                continue

            info = parse_feature_info(smali)
            if not info:
                log_fn(f"[!] Skipped malformed: {smali.name}")
                continue

            feature_special = []
            if special_perms_by_smali:
                key = os.path.normcase(os.path.abspath(str(smali)))
                feature_special = (special_perms_by_smali or {}).get(key, []) or []

            if feature_special:
                special_by_feature_java[info["java"]] = feature_special

            log_fn(f"[*] Processing feature: {smali}")
            log_fn(f"    └─ desc: {info['desc']}")

            # Copy main class into package path under out/smali/
            copy_smali(smali, out_smali, info["desc"])

            # Collect registry + manifest targets
            simple_name = info["java"].split(".")[-1]
            label = info["label"] or simple_name
            entries.append((info["java"], label))
            if info.get("target"):
                targets.add(info["target"])

            # Copy sibling inner classes from the same (flat) folder, e.g. AntiAgent$PkgReceiver.smali
            inner_pattern = f"{smali.stem}$*.smali"
            for extra in smali.parent.glob(inner_pattern):
                xinfo = parse_feature_info(extra)
                if not xinfo:
                    log_fn(f"    [!] SKIP inner (unparsable): {extra}")
                    continue
                log_fn(f"    └─ Copying inner class: {extra.name}")
                copy_smali(extra, out_smali, xinfo["desc"])

        def _dedup_preserve_order(seq):
            seen = set()
            out = []
            for x in seq or []:
                x = (x or "").strip()
                if x and x not in seen:
                    seen.add(x)
                    out.append(x)
            return out

        all_perms = _dedup_preserve_order((runtime_permissions or []) + (special_permissions or []))

        # Patch manifest with requested permissions + <queries> (if any targets)
        patch_manifest(out_dir, targets, all_perms, log_fn)

        generate_feature_registry(out_dir, entries, log_fn)

        log_fn(f"[*] special_perms_by_smali keys: {len(special_perms_by_smali or {})}")
        log_fn(f"[*] special_by_feature_java rows: {len(special_by_feature_java)}")
        patch_special_feature_requirements(out_dir, special_by_feature_java, log_fn)

        log_fn("[*] Rebuilding and signing APK…")
        assets_dir = Path("assets")
        assets_dir.mkdir(exist_ok=True)
        output_path = assets_dir / "mod-signed.apk"

        rebuild_sign_install_run(out_dir, output_path, app_id, do_run, log_fn)
        log_fn(f"[✓] Done. Output: {output_path}")

    except Exception as e:
        log_fn(f"[✗] Build failed: {e}")


def stop_session(app_id: str, log_fn=print):
    """
    Stops the running app, uninstalls it, and removes any leftover data/folders.
    """
    try:
        log_fn(f"[*] Stopping session for: {app_id}")

        # Finalise report inside the app
        run([
            "adb", "shell", "am", "broadcast",
            "-a", f"{app_id}.ACTION_FINALIZE_REPORT"
        ], log_fn=log_fn)

        # Extract Report (pull to local ./reports folder)
        local_reports = Path("reports")
        local_reports.mkdir(exist_ok=True)
        run([
            "adb", "pull",
            f"/sdcard/Android/data/{app_id}/files/reports/.",
            str(local_reports)
        ], check=False, log_fn=log_fn)

        # Stop the app if running
        run(["adb", "shell", "am", "force-stop", app_id], log_fn=log_fn)

        # Remove app's external storage folders if any
        paths_to_delete = [
            f"/sdcard/Android/data/{app_id}",
            f"/sdcard/{app_id}",
            f"/storage/emulated/0/{app_id}"
        ]
        for path in paths_to_delete:
            run(["adb", "shell", "rm", "-rf", path], check=False, log_fn=log_fn)

        # Uninstall the app
        run(["adb", "uninstall", app_id], log_fn=log_fn)

        log_fn(f"[✓] Session cleanup completed for: {app_id}")
    except Exception as e:
        log_fn(f"[✗] Stop session failed: {e}")
