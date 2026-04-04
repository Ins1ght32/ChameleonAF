# compile_tab.py
import tkinter as tk
from tkinter import ttk, filedialog
from ttkbootstrap.constants import *
import tkinter.font as tkfont
import threading
import shutil, os
from pathlib import Path
import json

# ===== Engine import =====
try:
    from modules.compile_engine import (
        init_engine,
        get_feature_sources,
        get_indexed_features,
        delete_indexed_feature,
        compile_selected_feature,
        get_feature_ui_metadata,
        detect_feature_requires_root,
        CompileMeta,
    )
except Exception:
    import importlib.util, sys

    ce_spec = importlib.util.spec_from_file_location("compile_engine", str(Path("modules") / "compile_engine.py"))
    ce = importlib.util.module_from_spec(ce_spec)
    assert ce_spec and ce_spec.loader
    ce_spec.loader.exec_module(ce)  # type: ignore
    init_engine = ce.init_engine
    get_feature_sources = ce.get_feature_sources
    get_indexed_features = ce.get_indexed_features
    compile_selected_feature = ce.compile_selected_feature
    get_feature_ui_metadata = ce.get_feature_ui_metadata
    detect_feature_requires_root = ce.detect_feature_requires_root
    CompileMeta = ce.CompileMeta

tab_builder_compile_log_frame = None
tab_builder_compile_refresh_callback = None

def build_compile_tab(parent):
    try:
        init_engine()
    except Exception as e:
        print(f"[Compile Tab] Init warning: {e}")

    outer = ttk.Frame(parent)
    outer.pack(fill="both", expand=True, padx=10, pady=10)
    outer.grid_rowconfigure(0, weight=5)
    outer.grid_rowconfigure(1, weight=4)
    outer.grid_columnconfigure(0, weight=1)

    upper = ttk.Frame(outer)
    upper.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
    upper.grid_columnconfigure(0, weight=1, uniform="half")
    upper.grid_columnconfigure(1, weight=1, uniform="half")
    upper.grid_rowconfigure(0, weight=1)

    # ========== LEFT SIDE ==========
    left = ttk.Frame(upper)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
    left.grid_rowconfigure(0, weight=1)
    left.grid_columnconfigure(0, weight=1)

    view_existing = ttk.LabelFrame(left, text="View Existing", bootstyle="primary")
    view_existing.grid(row=0, column=0, sticky="nsew")

    # ========== RIGHT SIDE ==========
    right_stack = ttk.Frame(upper)
    right_stack.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
    right_stack.grid_rowconfigure(0, weight=3)
    right_stack.grid_columnconfigure(0, weight=1)

    # Compile New
    right = ttk.LabelFrame(right_stack, text="Compile New", bootstyle="success")
    right.grid(row=0, column=0, sticky="nsew")

    def push_log(msg: str):
        print(msg)

    # View Existing content
    existing = ttk.Frame(view_existing)
    existing.grid(row=0, column=0, sticky="nsew", padx=10, pady=0)
    view_existing.grid_rowconfigure(0, weight=1)
    view_existing.grid_columnconfigure(0, weight=1)

    ttk.Label(existing, text="Indexed Feature:").grid(row=0, column=0, sticky="w")
    existing_var = tk.StringVar()
    existing_dd = ttk.Combobox(existing, textvariable=existing_var, state="readonly", values=[])
    existing_dd.grid(row=0, column=1, sticky="we", padx=(8, 4))
    remove_btn = ttk.Button(existing, text="Remove", bootstyle="danger-outline", width=10)
    remove_btn.grid(row=0, column=2, padx=(4, 0))
    existing.grid_columnconfigure(1, weight=1)

    detail = ttk.Frame(existing)
    detail.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))
    existing.grid_rowconfigure(1, weight=1)

    labels = {
        "name": ttk.Label(detail, text="Feature:", anchor="w"),
        "compiled": ttk.Label(detail, text="Compiled Date:", anchor="w"),
        "desc": ttk.Label(detail, text="Description:", anchor="w"),
        "artifact": ttk.Label(detail, text="Smali Artifact(s):", anchor="w"),
        "perms": ttk.Label(detail, text="Permissions:", anchor="w"),
        "status": ttk.Label(detail, text="Status:", anchor="w"),
        "requires_root": ttk.Label(detail, text="Requires Root:", anchor="w"),
        "java_path": ttk.Label(detail, text="Source (.java):", anchor="w"),
    }
    vals = {
        "name": ttk.Label(detail, text="", anchor="w"),
        "compiled": ttk.Label(detail, text="", anchor="w"),
        "desc": ttk.Label(detail, text="", anchor="w", justify="left"),
        "artifact": ttk.Label(detail, text="", anchor="w", justify="left"),
        "perms": ttk.Label(detail, text="", anchor="w", justify="left"),
        "status": ttk.Label(detail, text="", anchor="w"),
        "requires_root": ttk.Label(detail, text="", anchor="w"),
        "java_path": ttk.Label(detail, text="", anchor="w", justify="left"),
    }

    for i, k in enumerate(labels):
        labels[k].grid(row=i, column=0, sticky="nw", pady=3)
        vals[k].grid(row=i, column=1, sticky="nsew", padx=(10, 0), pady=3)

    detail.grid_columnconfigure(1, weight=1)

    def bind_dynamic_wrap(label):
        def _resize(event, lbl=label):
            lbl.configure(wraplength=lbl.winfo_width())

        label.bind("<Configure>", _resize)

    for key in ("desc", "artifact", "java_path", "perms"):
        bind_dynamic_wrap(vals[key])

    _existing_records = []

    def remove_selected_feature():
        label = existing_var.get()
        rec = next(
            (r for r in _existing_records if (r.get("name") or Path(r.get("java_path", "x.java")).stem) == label), None)
        if not rec:
            push_log("[Remove] No matching feature found.")
            return
        confirm = tk.messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove: {label}?")
        if not confirm:
            return
        success = delete_indexed_feature(rec.get("java_path"))
        if success:
            push_log(f"[Remove] Deleted: {label}")
        else:
            push_log(f"[Remove] Failed to delete: {label}")
        refresh_existing()
        refresh_swap_dropdown()

    remove_btn.config(command=remove_selected_feature)

    def refresh_existing():
        nonlocal _existing_records
        _existing_records = get_indexed_features()
        items = [(r.get("name") or Path(r.get("java_path", "unknown.java")).stem) for r in _existing_records]
        existing_dd.config(values=items)
        if items:
            existing_var.set(items[0])
            apply_existing_selection()
        else:
            existing_var.set("")
            for v in vals.values():
                v.configure(text="-")

    def _json_list(val):
        try:
            data = json.loads(val or "[]")
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def apply_existing_selection(*_):
        label = existing_var.get()
        rec = next(
            (r for r in _existing_records if (r.get("name") or Path(r.get("java_path", "x.java")).stem) == label), None)
        if not rec:
            for v in vals.values():
                v.configure(text="-")
            return
        vals["name"].configure(text=rec.get("name", "-"))
        vals["compiled"].configure(text=rec.get("compiled_date", "-"))
        vals["desc"].configure(text=rec.get("description", "-"))
        vals["artifact"].configure(text="\n".join(_json_list(rec.get("smali_paths")) or []))
        runtime = _json_list(rec.get("runtime_permissions"))
        special = _json_list(rec.get("special_permissions"))
        all_perms = runtime + [p for p in special if p not in runtime]
        vals["perms"].configure(
            text=", ".join(all_perms) if all_perms else "-"
        )
        vals["status"].configure(text=rec.get("status", "-"))
        vals["requires_root"].configure(text="Yes" if rec.get("requires_root") else "No")
        vals["java_path"].configure(text=rec.get("java_path", "-"))

    existing_dd.bind("<<ComboboxSelected>>", apply_existing_selection)
    refresh_existing()

    # ----- Compile New Content -----
    right_top = ttk.Frame(right)
    right_top.pack(fill="x", padx=10, pady=(10, 8))

    progress_var = tk.DoubleVar(value=0)
    progress = ttk.Progressbar(right_top, variable=progress_var, mode="determinate", bootstyle="info", maximum=100)
    progress.grid(row=0, column=0, columnspan=4, sticky="we")
    right_top.grid_columnconfigure(0, weight=0)
    right_top.grid_columnconfigure(1, weight=1)
    right_top.grid_columnconfigure(2, weight=0)
    right_top.grid_columnconfigure(3, weight=0)

    ttk.Label(right_top, text="Available Feature:").grid(row=1, column=0, sticky="w", pady=(8, 0))
    source_var = tk.StringVar(value="")
    source_dd = ttk.Combobox(right_top, textvariable=source_var, state="readonly", values=[])
    source_dd.grid(row=1, column=1, sticky="we", padx=(8, 8), pady=(8, 0))

    compile_btn = ttk.Button(right_top, text="Compile", bootstyle=SUCCESS)
    compile_btn.grid(row=1, column=2, sticky="e", padx=(0, 6), pady=(8, 0))

    def import_java_file():
        path = filedialog.askopenfilename(
            title="Select a Java file",
            filetypes=[("Java files", "*.java"), ("All files", "*.*")]
        )
        if not path:
            return
        dest_dir = os.path.join("modules", "features")
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, os.path.basename(path))

        try:
            if Path(path).resolve() == Path(dest_path).resolve():
                push_log(f"[Import Features] Skipped – '{path}' is already in the features folder.")
            else:
                shutil.copy(path, dest_path)
                push_log(f"[Import Features] Copied {path} -> {dest_path}")
                refresh_sources()
        except shutil.SameFileError:
            push_log(f"[Import Features] Skipped – source and destination are the same.")
        except Exception as e:
            push_log(f"[Import Features] Error: {e}")

    import_btn = ttk.Button(right_top, text="Import .java File", bootstyle=SECONDARY, command=import_java_file)
    import_btn.grid(row=1, column=3, sticky="e", pady=(8, 0))

    ttk.Separator(right, bootstyle="secondary").pack(fill="x", padx=10, pady=(6, 8))

    form = ttk.Frame(right)
    form.pack(fill="both", expand=True, padx=10, pady=(10, 10))
    form.grid_columnconfigure(0, weight=0, minsize=180)
    form.grid_columnconfigure(1, weight=1, minsize=380)

    ttk.Label(form, text="Requires Device Rooted:").grid(row=0, column=0, sticky="w", pady=4, padx=(0, 8))
    req_root_var = tk.IntVar(value=0)
    ttk.Checkbutton(form, text="", variable=req_root_var).grid(row=0, column=1, sticky="w", pady=4, padx=(8, 0))

    ttk.Label(form, text="Feature Name:").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 8))
    feat_name = tk.StringVar()
    ttk.Entry(form, textvariable=feat_name).grid(row=1, column=1, sticky="we", pady=4, padx=(8, 0))

    ttk.Label(form, text="Description:").grid(row=2, column=0, sticky="w", pady=4, padx=(0, 8))
    feat_desc = tk.StringVar()
    ttk.Entry(form, textvariable=feat_desc).grid(row=2, column=1, sticky="we", pady=4, padx=(8, 0))

    anti_block = ttk.Frame(form)
    anti_block.grid(row=3, column=0, columnspan=2, sticky="we", pady=0)
    anti_block.grid_columnconfigure(0, weight=0, minsize=180)
    anti_block.grid_columnconfigure(1, weight=1, minsize=380)
    target_pkg_lbl = ttk.Label(anti_block, text="Target Package (from AntiAgent):")
    target_pkg_var = tk.StringVar()
    target_pkg_ent = ttk.Entry(anti_block, textvariable=target_pkg_var)

    # ----- Permissions (Compile-time metadata) -----
    # Single unified table:
    #   col1: Permission
    #   col2: Type (Runtime/Special)
    #   col3: Selected? (tick toggles on click)
    perm_frame = ttk.LabelFrame(form, text="Permissions (Compile Metadata)", bootstyle="secondary")
    perm_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
    perm_frame.grid_rowconfigure(0, weight=1)
    perm_frame.grid_columnconfigure(0, weight=1)

    NORMAL_PERMS = [
        # Common “install-time” permissions (no runtime prompt)
        "android.permission.INTERNET",
        "android.permission.ACCESS_NETWORK_STATE",
        "android.permission.ACCESS_WIFI_STATE",
        "android.permission.WAKE_LOCK",
        "android.permission.RECEIVE_BOOT_COMPLETED",
        "android.permission.FOREGROUND_SERVICE",
        "android.permission.VIBRATE",
    ]

    RUNTIME_PERMS = [
        "android.permission.READ_SMS",
        "android.permission.SEND_SMS",
        "android.permission.READ_CONTACTS",
        "android.permission.WRITE_CONTACTS",
        "android.permission.READ_CALL_LOG",
        "android.permission.WRITE_CALL_LOG",
        "android.permission.CAMERA",
        "android.permission.RECORD_AUDIO",
        "android.permission.ACCESS_FINE_LOCATION",
        "android.permission.ACCESS_COARSE_LOCATION",

        # Android 13+ runtime media perms
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.READ_MEDIA_VIDEO",
        "android.permission.READ_MEDIA_AUDIO",

        # Legacy storage (runtime on older Androids; behavior changes by API level)
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.WRITE_EXTERNAL_STORAGE",

        # Android 13+ runtime
        "android.permission.POST_NOTIFICATIONS",
    ]

    SPECIAL_PERMS = [
        "android.permission.MANAGE_EXTERNAL_STORAGE",  # “All files access” toggle
        "android.permission.SYSTEM_ALERT_WINDOW",  # “Display over other apps” toggle
        "android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS",  # user confirmation / whitelist behavior
        "android.permission.PACKAGE_USAGE_STATS",  # “Usage access” (AppOps)
    ]

    # --- Unified permission table (treeview) + scrollbars ---
    perm_table_box = ttk.Frame(perm_frame)
    perm_table_box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    perm_table_box.grid_rowconfigure(0, weight=1)
    perm_table_box.grid_columnconfigure(0, weight=1)

    perm_tv = ttk.Treeview(
        perm_table_box,
        columns=("perm", "ptype", "selected"),
        show="headings",
        height=8,
    )
    perm_tv.grid(row=0, column=0, sticky="nsew")

    perm_vsb = ttk.Scrollbar(perm_table_box, orient="vertical", command=perm_tv.yview)
    perm_vsb.grid(row=0, column=1, sticky="ns", padx=(6, 0))
    perm_tv.configure(yscrollcommand=perm_vsb.set)

    perm_hsb = ttk.Scrollbar(perm_table_box, orient="horizontal", command=perm_tv.xview)
    perm_hsb.grid(row=1, column=0, sticky="ew", pady=(6, 0))
    perm_tv.configure(xscrollcommand=perm_hsb.set)

    perm_tv.heading("perm", text="Permission")
    perm_tv.heading("ptype", text="Type")
    perm_tv.heading("selected", text="Selected?")

    # Column sizing (keep permission wide, make Selected narrow)
    perm_tv.column("perm", width=420, anchor="w", stretch=True)
    perm_tv.column("ptype", width=110, anchor="center", stretch=False)
    perm_tv.column("selected", width=190, anchor="center", stretch=False)

    # Populate unified table (iid = permission string)
    for p in NORMAL_PERMS:
        perm_tv.insert("", "end", iid=p, values=(p, "Normal", ""))
    for p in RUNTIME_PERMS:
        perm_tv.insert("", "end", iid=p, values=(p, "Runtime", ""))
    for p in SPECIAL_PERMS:
        if p in perm_tv.get_children(""):
            continue
        perm_tv.insert("", "end", iid=p, values=(p, "Special", ""))

    def _toggle_perm_selected(iid: str):
        try:
            cur = list(perm_tv.item(iid, "values"))
        except Exception:
            return
        if len(cur) != 3:
            return
        cur[2] = "" if cur[2] else "✓"
        perm_tv.item(iid, values=tuple(cur))

    def _on_perm_click_release(event):
        """Toggle when clicking Permission or Selected? columns.

        Use ButtonRelease so Treeview selection behaviour still works.
        """
        iid = perm_tv.identify_row(event.y)
        if not iid:
            return
        col = perm_tv.identify_column(event.x)  # e.g., "#1" "#2" "#3"
        if col in ("#1", "#3"):
            _toggle_perm_selected(iid)

    def _on_perm_space(event):
        sel = perm_tv.selection()
        if not sel:
            return
        _toggle_perm_selected(sel[0])
        return "break"

    perm_tv.bind("<ButtonRelease-1>", _on_perm_click_release)
    perm_tv.bind("<space>", _on_perm_space)

    def _dedup_preserve_order(seq):
        seen = set()
        out = []
        for x in seq:
            x = (x or "").strip()
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def _get_permissions_from_ui():
        runtime_like: list[str] = []  # Runtime + Normal (same downstream handling)
        special: list[str] = []

        for iid in perm_tv.get_children(""):
            vals = perm_tv.item(iid, "values")
            if not vals or len(vals) < 3:
                continue

            perm, ptype, selected = vals[0], vals[1], vals[2]
            if not selected:
                continue

            t = str(ptype).strip().lower()
            if t in ("runtime", "normal"):
                runtime_like.append(perm)
            else:
                special.append(perm)

        return _dedup_preserve_order(runtime_like), _dedup_preserve_order(special)

    def _show_target_pkg(initial_pkg: str):
        target_pkg_lbl.grid(row=0, column=0, sticky="w", pady=4, padx=(0, 8))
        target_pkg_ent.grid(row=0, column=1, sticky="we", pady=4, padx=(8, 0))
        target_pkg_var.set(initial_pkg or "")

    def _hide_target_pkg():
        for w in (target_pkg_lbl, target_pkg_ent):
            w.grid_remove()
        target_pkg_var.set("")

    _source_items = []

    def get_selected_source():
        label = source_var.get()
        return next((s for s in _source_items if s["label"] == label), None)

    def _apply_source_change(*_):
        _refresh_compile_ui_state()

    source_dd.bind("<<ComboboxSelected>>", _apply_source_change)

    def refresh_sources():
        nonlocal _source_items
        _source_items = get_feature_sources()
        labels = [s["label"] for s in _source_items]
        source_dd.config(values=labels)
        if labels:
            if source_var.get() not in labels:
                source_var.set(labels[0])
        else:
            source_var.set("")
        _refresh_compile_ui_state()

    def run_compile():
        try:
            progress_var.set(0)
            sel = get_selected_source()
            if not sel:
                push_log("[!] No Available Feature selected.")
                return

            ui_meta = get_feature_ui_metadata(sel["path"])
            pass_pkg = target_pkg_var.get().strip() if ui_meta.get("show_target_package") else ""

            runtime_perms, special_perms = _get_permissions_from_ui()

            meta = CompileMeta(
                name=feat_name.get().strip() or Path(sel["path"]).stem,
                description=feat_desc.get().strip(),
                requires_root=bool(req_root_var.get()),
                target_package_override=pass_pkg,

                runtime_permissions=runtime_perms,
                special_permissions=special_perms,
            )

            push_log(f"[Compile] Starting smali build for: {Path(sel['path']).name}")

            def logger(msg: str):
                push_log(msg)

            def progress_cb(pct: int):
                progress_var.set(pct)

            rec = compile_selected_feature(sel["path"], meta, logger=logger, progress=progress_cb)
            push_log(f"[✓] Completed. Indexed as: {rec.get('name')}")
            progress_var.set(100)
            refresh_existing()
            refresh_swap_dropdown()
        except Exception as e:
            push_log(f"[ERROR] {e}")
        finally:
            compile_btn.config(state=NORMAL)

    def on_compile():
        compile_btn.config(state=DISABLED)
        threading.Thread(target=run_compile, daemon=True).start()

    def _refresh_compile_ui_state():
        sel = get_selected_source()
        if not sel:
            _hide_target_pkg()
            req_root_var.set(0)
            return

        meta = get_feature_ui_metadata(sel["path"])
        if meta.get("show_target_package"):
            _show_target_pkg(meta.get("initial_target_package", ""))
        else:
            _hide_target_pkg()

        try:
            req_root_var.set(1 if detect_feature_requires_root(sel["path"]) else 0)
        except Exception:
            req_root_var.set(0)

    global tab_builder_compile_refresh_callback
    tab_builder_compile_refresh_callback = _refresh_compile_ui_state

    compile_btn.config(command=on_compile)
    refresh_sources()

    # ----- Manage Compiled Versions -----
    version_frame = ttk.LabelFrame(right_stack, text="Manage Compiled Versions", bootstyle="warning")
    version_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
    version_frame.grid_columnconfigure(1, weight=1)

    # Dropdown: Select Indexed Feature
    ttk.Label(version_frame, text="Indexed Feature:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 4))
    swap_feat_var = tk.StringVar()
    swap_feat_dd = ttk.Combobox(version_frame, textvariable=swap_feat_var, state="readonly", values=[])
    swap_feat_dd.grid(row=0, column=1, columnspan=2, sticky="we", padx=(4, 10), pady=(10, 4))

    # Dropdown: Select Compiled Version Folder
    ttk.Label(version_frame, text="Compiled Version:").grid(row=1, column=0, sticky="w", padx=10, pady=4)
    swap_ver_var = tk.StringVar()
    swap_ver_dd = ttk.Combobox(version_frame, textvariable=swap_ver_var, state="readonly", values=[])
    swap_ver_dd.grid(row=1, column=1, columnspan=2, sticky="we", padx=(4, 10), pady=4)

    # Button: Use this version
    use_btn = ttk.Button(version_frame, text="Use This Version", bootstyle="success-outline")
    use_btn.grid(row=2, column=0, padx=(10, 4), pady=(8, 10), sticky="w")

    # Inline info label between buttons
    version_note = ttk.Label(
        version_frame,
        text="Version switching updates compiled smali only. Indexed metadata remains unchanged.",
        bootstyle="secondary"
    )
    version_note.grid(row=2, column=1, padx=6, pady=(8, 10))

    italic_font = tkfont.Font(version_note, version_note.cget("font"))
    italic_font.configure(slant="italic")
    version_note.configure(font=italic_font)

    # Button: Delete this version
    del_btn = ttk.Button(version_frame, text="Delete This Version", bootstyle="danger-outline")
    del_btn.grid(row=2, column=2, padx=(6, 10), pady=(8, 10), sticky="e")

    # Logic to update versions dropdown when feature is selected
    def _update_version_dropdown(*_):
        label = swap_feat_var.get()
        rec = next(
            (r for r in _existing_records if (r.get("name") or Path(r.get("java_path", "x.java")).stem) == label), None)
        if not rec:
            swap_ver_dd.config(values=[])
            swap_ver_var.set("")
            return
        from modules.compile_engine import list_compiled_versions
        versions = list_compiled_versions(rec["java_path"])
        swap_ver_dd.config(values=versions)
        if versions:
            swap_ver_var.set(versions[0])
        else:
            swap_ver_var.set("")

    swap_feat_dd.bind("<<ComboboxSelected>>", _update_version_dropdown)

    def refresh_swap_dropdown():
        items = [(r.get("name") or Path(r.get("java_path", "unknown.java")).stem) for r in _existing_records]
        swap_feat_dd.config(values=items)
        if items:
            swap_feat_var.set(items[0])
            _update_version_dropdown()
        else:
            swap_feat_var.set("")
            swap_ver_var.set("")
            swap_ver_dd.config(values=[])

    def _do_use_version():
        feat_label = swap_feat_var.get()
        version_folder = swap_ver_var.get()
        if not feat_label or not version_folder:
            push_log("[Use Version] Missing selection.")
            return
        rec = next(
            (r for r in _existing_records if (r.get("name") or Path(r.get("java_path", "x.java")).stem) == feat_label),
            None)
        if not rec:
            push_log("[Use Version] Invalid feature.")
            return
        from modules.compile_engine import switch_active_version
        try:
            switch_active_version(rec["java_path"], version_folder)
            push_log(f"[✓] Updated '{feat_label}' to use version '{version_folder}'")
            refresh_existing()
        except Exception as e:
            push_log(f"[ERROR] Failed to switch version: {e}")

    def _do_delete_version():
        version_folder = swap_ver_var.get()
        if not version_folder:
            push_log("[Delete Version] No version selected.")
            return
        confirm = tk.messagebox.askyesno("Confirm Delete", f"Delete compiled version folder:\n{version_folder} ?")
        if not confirm:
            return
        from modules.compile_engine import delete_compiled_version_folder
        try:
            delete_compiled_version_folder(version_folder)
            push_log(f"[✓] Deleted version folder: {version_folder}")
            refresh_existing()
            _update_version_dropdown()
        except Exception as e:
            push_log(f"[ERROR] Failed to delete folder: {e}")

    use_btn.config(command=_do_use_version)
    del_btn.config(command=_do_delete_version)

    # Initial population
    refresh_swap_dropdown()

    # ----- Log -----
    log_holder = ttk.LabelFrame(outer, text="Command Output Log", bootstyle="info")
    log_holder.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    inner = ttk.Frame(log_holder)
    inner.pack(fill="both", expand=True, padx=8, pady=8)
    global tab_builder_compile_log_frame
    tab_builder_compile_log_frame = inner
