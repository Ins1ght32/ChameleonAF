# modules/tabs/build_tab.py
import os
import tkinter as tk
from tkinter import ttk, filedialog
from ttkbootstrap.constants import *
from pathlib import Path
import json
import threading

# ===== Engine import (read-only for UI population) =====
try:
    from modules.feature_api import (
        init_engine,
        get_indexed_features,
    )
except Exception:
    import importlib.util, sys

    fa_spec = importlib.util.spec_from_file_location("feature_api", str(Path("modules") / "feature_api.py"))
    fa = importlib.util.module_from_spec(fa_spec)
    assert fa_spec and fa_spec.loader
    fa_spec.loader.exec_module(fa)  # type: ignore
    init_engine = fa.init_engine
    get_indexed_features = fa.get_indexed_features

# Holder so main.py can mount the shared log inside the labeled frame
tab_builder_build_log_frame = None


def _safe_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return x != 0
    if isinstance(x, str):
        return x.strip().lower() in ("1", "true", "yes", "y")
    return False


def _stub_log(msg: str):
    print(msg)


def build_build_tab(parent, shared_output_text: tk.Text):
    """
    Build tab UI:
      - Left area (columns 0..1 merged): two stacked frames:
          (Top) Indexed Features  -> Combobox + dynamic details + [Add Feature]
          (Bottom) Selected for Build -> list + [Remove] / [Clear]
      - Right (column 2): Build controls (unchanged)
      - Bottom: Command Output Log (same structure as Compile)
    """
    try:
        init_engine()  # harmless if already initialized
    except Exception as e:
        print(f"[Build Tab] Init warning: {e}")

    outer = ttk.Frame(parent)
    outer.pack(fill="both", expand=True, padx=10, pady=10)

    # Keep the same overall proportions as before
    outer.grid_rowconfigure(0, weight=5)
    outer.grid_rowconfigure(1, weight=4)
    outer.grid_columnconfigure(0, weight=1)

    top = ttk.Frame(outer)
    top.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
    for c in range(3):
        top.grid_columnconfigure(c, weight=1, uniform="thirds")
    top.grid_rowconfigure(0, weight=1)

    # -------------------------------------------------------------------------
    # Left area: merge columns 0..1, then stack two frames 50/50 vertically
    # -------------------------------------------------------------------------
    left_col = ttk.Frame(top)
    left_col.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(0, 6))
    left_col.grid_rowconfigure(0, weight=1)  # Indexed Features
    left_col.grid_rowconfigure(1, weight=1)  # Selected for Build
    left_col.grid_columnconfigure(0, weight=1)

    # =========================
    # (Top) Indexed Features — combobox + dynamic detail panel + Add
    # Style mirrors compile_tab.py's "View Existing" section
    # =========================
    idx_frame = ttk.LabelFrame(left_col, text="Indexed Features", bootstyle="primary")
    idx_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 4))
    idx_frame_inner = ttk.Frame(idx_frame)
    idx_frame_inner.pack(fill="both", expand=True, padx=10, pady=10)

    idx_frame_inner.grid_columnconfigure(0, minsize=120)  # "Indexed Feature:" label
    idx_frame_inner.grid_columnconfigure(1, weight=1, minsize=420)  # Combobox column
    idx_frame_inner.grid_columnconfigure(2, minsize=130)  # "＋ Add Feature" button

    ttk.Label(idx_frame_inner, text="Indexed Feature:").grid(row=0, column=0, sticky="w")
    feature_var = tk.StringVar()
    feature_dd = ttk.Combobox(idx_frame_inner, textvariable=feature_var, state="readonly", values=[])
    feature_dd.grid(row=0, column=1, sticky="we", padx=(8, 8))
    feature_dd.config(width=48)

    add_btn = ttk.Button(idx_frame_inner, text="＋ Add Feature", bootstyle=SUCCESS)
    add_btn.grid(row=0, column=2, sticky="e")
    idx_frame_inner.grid_columnconfigure(1, weight=1)

    # Dynamic details (wrap like compile tab)
    detail = ttk.Frame(idx_frame_inner)
    detail.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))

    detail.grid_columnconfigure(0, minsize=140)  # left labels ("Feature:", "Compiled Date:", etc.)
    detail.grid_columnconfigure(1, weight=1, minsize=420)  # right values (wrapped text)

    idx_frame_inner.grid_rowconfigure(1, weight=1)
    detail.grid_columnconfigure(1, weight=1)

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
    r = 0
    for k in ["name", "compiled", "desc", "artifact", "perms", "status", "requires_root", "java_path"]:
        labels[k].grid(row=r, column=0, sticky="nw", pady=3)
        vals[k].grid(row=r, column=1, sticky="nsew", padx=(10, 0), pady=3)
        r += 1

    def _wrap(lbl: ttk.Label):
        def _resize(_e, _lbl=lbl):
            _lbl.configure(wraplength=_lbl.winfo_width())

        lbl.bind("<Configure>", _resize)

    for key in ("desc", "artifact", "java_path", "perms"):
        vals[key].configure(width=1)  # prevents width-request jumps on some themes
        _wrap(vals[key])

    _indexed_records = []

    def _json_list(val):
        try:
            data = json.loads(val or "[]")
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def refresh_indexed_dropdown():
        nonlocal _indexed_records
        try:
            _indexed_records = get_indexed_features()
        except Exception as e:
            _indexed_records = []
            print(f"[Build Tab] get_indexed_features() failed: {e}")

        items = []
        for rec in _indexed_records:
            label = rec.get("name") or Path(rec.get("java_path", "unknown.java")).stem
            items.append(label)
        feature_dd.config(values=items)
        if items:
            feature_var.set(items[0])
            apply_selected_indexed()
        else:
            feature_var.set("")
            for v in vals.values():
                v.configure(text="-")

    def _find_record_by_label(label: str) -> dict | None:
        for rec in _indexed_records:
            if (rec.get("name") or Path(rec.get("java_path", "x.java")).stem) == label:
                return rec
        return None

    def apply_selected_indexed(*_):
        rec = _find_record_by_label(feature_var.get())
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
        vals["requires_root"].configure(text="Yes" if _safe_bool(rec.get("requires_root")) else "No")
        vals["java_path"].configure(text=rec.get("java_path", "-"))

    feature_dd.bind("<<ComboboxSelected>>", apply_selected_indexed)
    refresh_indexed_dropdown()

    def _on_tab_focus(event):
        try:
            if event.widget == parent:
                refresh_indexed_dropdown()
        except Exception as e:
            print(f"[Build Tab] Tab focus error: {e}")

    parent.bind("<Visibility>", _on_tab_focus)

    # =========================
    # (Bottom) Selected for Build — list + Remove / Clear
    # =========================
    sel_frame = ttk.LabelFrame(left_col, text="Selected for Build", bootstyle="secondary")
    sel_frame.grid(row=1, column=0, sticky="nsew", pady=(4, 0))

    counters = ttk.Frame(sel_frame)
    counters.pack(fill="x", padx=10, pady=(10, 6))
    lbl_selected = ttk.Label(counters, text="Total: 0")
    lbl_selected.pack(side="left")
    lbl_root = ttk.Label(counters, text="Requires Root: 0", bootstyle="danger")
    lbl_root.pack(side="left", padx=(10, 0))

    sel_wrap = ttk.Frame(sel_frame)
    sel_wrap.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    sel_cols = ("name", "root", "source")
    sel_tv = ttk.Treeview(sel_wrap, columns=sel_cols, show="headings", height=6)
    sel_vscroll = ttk.Scrollbar(sel_wrap, orient="vertical", command=sel_tv.yview)
    sel_tv.configure(yscrollcommand=sel_vscroll.set)

    sel_tv.heading("name", text="Name")
    sel_tv.heading("root", text="Root?")
    sel_tv.heading("source", text="Source (.java)")

    sel_tv.column("name", width=240, anchor="w")
    sel_tv.column("root", width=80, anchor="center")
    sel_tv.column("source", width=400, anchor="w")  # widened slightly

    sel_tv.grid(row=0, column=0, sticky="nsew")
    sel_vscroll.grid(row=0, column=1, sticky="ns")

    sel_wrap.grid_rowconfigure(0, weight=1)
    sel_wrap.grid_columnconfigure(0, weight=1)

    # Controls: Remove / Clear
    sel_btns = ttk.Frame(sel_frame)
    sel_btns.pack(fill="x", padx=10, pady=(0, 10))
    btn_remove = ttk.Button(sel_btns, text="🗑 Remove", bootstyle=DANGER)
    btn_clear = ttk.Button(sel_btns, text="Clear All")
    btn_remove.pack(side="left")
    btn_clear.pack(side="right")

    def _update_counts():
        total = len(sel_tv.get_children())
        root_ct = 0
        for iid in sel_tv.get_children():
            vals_row = sel_tv.item(iid, "values")
            if len(vals_row) >= 2 and str(vals_row[1]).lower().startswith("y"):
                root_ct += 1
        lbl_selected.configure(text=f"Total: {total}")
        lbl_root.configure(text=f"Requires Root: {root_ct}")

    def _add_current_feature():
        rec = _find_record_by_label(feature_var.get())
        if not rec:
            _stub_log("[Build] No indexed feature selected to add.")
            return
        name = rec.get("name") or Path(rec.get("java_path", "unknown.java")).stem
        root = "Yes" if _safe_bool(rec.get("requires_root")) else "No"
        source = rec.get("java_path", "-")
        # dedupe by source
        for iid in sel_tv.get_children():
            if sel_tv.item(iid, "values")[2] == source:
                _stub_log("[Build] Feature already in the Selected list.")
                return
        sel_tv.insert("", "end", values=(name, root, source))
        _update_counts()
        _stub_log(f"[Build] Added: {name}")

    add_btn.config(command=_add_current_feature)

    def _remove_selected():
        for iid in sel_tv.selection():
            sel_tv.delete(iid)
        _update_counts()

    def _clear_all():
        for iid in sel_tv.get_children():
            sel_tv.delete(iid)
        _update_counts()

    btn_remove.config(command=_remove_selected)
    btn_clear.config(command=_clear_all)

    # -------------------------------------------------------------------------
    # Right: Build controls
    # -------------------------------------------------------------------------
    right = ttk.LabelFrame(top, text="Build Controls", bootstyle="success")
    right.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

    form = ttk.Frame(right)
    form.pack(fill="both", expand=True, padx=10, pady=10)
    form.grid_columnconfigure(0, weight=0, minsize=170)
    form.grid_columnconfigure(1, weight=1, minsize=300)

    row = 0
    ttk.Label(form, text="Base APK Path:").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
    base_apk_var = tk.StringVar()
    ttk.Entry(form, textvariable=base_apk_var).grid(row=row, column=1, sticky="we", pady=4)

    def _browse_apk():
        p = filedialog.askopenfilename(title="Select Base APK", filetypes=[("APK files", "*.apk"), ("All", "*.*")])
        if p:
            base_apk_var.set(p)

    ttk.Button(form, text="Browse", command=_browse_apk).grid(row=row, column=2, sticky="w", padx=(6, 0))

    row += 1
    ttk.Label(form, text="Output App ID (package):").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
    pkg_var = tk.StringVar()
    ttk.Entry(form, textvariable=pkg_var).grid(row=row, column=1, sticky="we", pady=4)

    row += 1
    ttk.Label(form, text="App Version Name:").grid(row=row, column=0, sticky="w", pady=4, padx=(0, 8))
    ver_var = tk.StringVar()
    ttk.Entry(form, textvariable=ver_var).grid(row=row, column=1, sticky="we", pady=4)

    # Shift separator up
    ttk.Separator(form).grid(row=row + 1, column=0, columnspan=3, sticky="we", pady=(10, 10))

    # Row + 2 -> Combined status + buttons
    status_color = tk.StringVar(value="black")
    status_text = tk.StringVar(value="Idle – No action taken yet")

    status_actions = ttk.Frame(form)
    status_actions.grid(row=row + 2, column=0, columnspan=3, sticky="we")

    # Traffic Light Row
    status_bar = ttk.Label(
        status_actions,
        textvariable=status_text,
        anchor="center",
        background="black",
        foreground="white",
        font=("Segoe UI", 10, "bold"),
        padding=6
    )
    status_bar.grid(row=0, column=0, columnspan=2, sticky="we", pady=(0, 8))
    status_bar.configure(background=status_color.get())

    # Buttons Row
    btn_run = ttk.Button(status_actions, text="Build & Run", bootstyle=SUCCESS)
    btn_stop = ttk.Button(status_actions, text="Stop Session", bootstyle=DANGER)
    btn_run.grid(row=1, column=0, sticky="we", padx=(0, 6))
    btn_stop.grid(row=1, column=1, sticky="we", padx=(6, 0))
    status_actions.grid_columnconfigure(0, weight=1)
    status_actions.grid_columnconfigure(1, weight=1)

    # ASCII art block 
    full_ascii_art = """
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣾⣿⡦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⠀⠀⣰⣿⣿⣿⣿⣷⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠈⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠆⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⡀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀
        ⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿BANG!⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⡀⠀
        ⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠉⠻⣿⣿⣿⣿⡆
        ⠀⢀⣾⣿⣿⣿⠟⠁⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠸⣿⣿⣿⣷
        ⠀⢸⣿⣿⣿⡏⠀⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⣿⣿⣿⣿
        ⠀⣿⣿⣿⣿⠀⢀⣄⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡏⢠⡄⠀⠀⢹⣿⣿⡟
        ⠀⣿⣿⣿⠏⠀⢸⣇⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⢸⣷⡠⠶⣿⣿⣿⠋
        ⠰⣿⣿⣿⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⢸⣿⡿⠀
        ⢠⣿⣿⠿⣧⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢠⣿⠟⠁⠀
        ⣿⣿⠃⠀⠈⠀⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠂⠀⠁⠀⠀⠀
        ⠘⠟⠃⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣿⡟⠉⢿⣿⣿⣿⣿⣿⣿⠉⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⣿⡟⠀⠀⠈⢿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡿⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⢀⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⢠⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⢸⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀
        ⠀⠀⠀⣠⣾⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠿⠿⠿⣿⣿⣶⣦⠄  
        """

    # Row + 3 → ASCII art
    ascii_label = tk.Label(
        form,
        text=full_ascii_art,
        font=("Courier New", 8),
        justify="center",
        anchor="center"
    )
    ascii_label.grid(row=row + 3, column=0, columnspan=3, pady=(10, 0))

    # ========== Prefill UI ==============
    base_apk_var.set("assets/chameleon.apk")
    # pkg_var.set("com.example.smaliinject")
    pkg_var.set("com.chameleonforensics.chameleon")
    ver_var.set("1.0")

    from modules.build_engine import run_build_from_ui, stop_session  # ← include stop_session
    # ========== Build Button Wiring ==============
    def _dedup_preserve_order(seq):
        seen = set()
        out = []
        for x in seq or []:
            x = (x or "").strip()
            if x and x not in seen:
                seen.add(x)
                out.append(x)
        return out

    def _extract_selected_special_perms_by_smali() -> dict[str, list[str]]:
        """
        Returns mapping:
          { "<ABS_PATH_TO_TOPLEVEL_SMALI>": ["android.permission.X", ...], ... }

        Build engine will convert this into:
          { "com.pkg.FeatureClass": ["..."], ... }
        """
        out: dict[str, list[str]] = {}

        for iid in sel_tv.get_children():
            row = sel_tv.item(iid, "values")
            if not row:
                continue

            rec = _find_record_by_label(row[0])
            if not rec:
                continue

            # read special perms from DB record
            try:
                special = json.loads(rec.get("special_permissions", "[]") or "[]")
            except Exception:
                special = []

            if not isinstance(special, list):
                special = []
            special = [(p or "").strip() for p in special if isinstance(p, str) and (p or "").strip()]
            if not special:
                continue

            # map perms to each TOP-LEVEL smali in smali_paths
            try:
                smalis = json.loads(rec.get("smali_paths", "[]") or "[]")
            except Exception:
                smalis = []

            if not isinstance(smalis, list):
                continue

            for rel in smalis:
                try:
                    p = Path("modules/injects").joinpath(rel).resolve()
                except Exception:
                    continue

                # build_engine already skips "$" main inputs, so we only map top-level here too
                if p.suffix.lower() != ".smali":
                    continue
                if "$" in p.stem:
                    continue

                key = os.path.normcase(os.path.abspath(str(p)))
                out[key] = special

        return out

    def _extract_selected_permissions() -> tuple[list[str], list[str]]:
        runtime_all = []
        special_all = []

        for iid in sel_tv.get_children():
            row = sel_tv.item(iid, "values")
            if not row:
                continue

            rec = _find_record_by_label(row[0])
            if not rec:
                continue

            # These will exist after your DB migration + compile_engine saving them
            try:
                r = json.loads(rec.get("runtime_permissions", "[]") or "[]")
                s = json.loads(rec.get("special_permissions", "[]") or "[]")
            except Exception:
                r, s = [], []

            if isinstance(r, list):
                runtime_all.extend(r)
            if isinstance(s, list):
                special_all.extend(s)

        return _dedup_preserve_order(runtime_all), _dedup_preserve_order(special_all)

    def _extract_selected_smali_paths() -> list[Path]:
        selected = []
        for iid in sel_tv.get_children():
            row = sel_tv.item(iid, "values")
            src = row[2] if len(row) >= 3 else None
            if not src:
                continue
            try:
                rec = _find_record_by_label(row[0])
                smalis = json.loads(rec.get("smali_paths", "[]"))
                selected.extend([Path("modules/injects").joinpath(s).resolve() for s in smalis])
            except Exception:
                continue
        return selected

    def _log(msg: str):
        try:
            shared_output_text.configure(state="normal")
            shared_output_text.insert("end", msg + "\n")
            shared_output_text.see("end")
            shared_output_text.configure(state="disabled")
        except Exception:
            print(msg)

    import threading

    def _build_clicked(do_run=False):
        def thread_target():
            try:
                status_color.set("yellow")
                status_text.set("Build in progress…")
                status_bar.configure(background="yellow", foreground="black")

                paths = _extract_selected_smali_paths()
                if not paths:
                    _log("[!] No features selected.")
                    status_color.set("red")
                    status_text.set("Build failed – check logs")
                    status_bar.configure(background="red", foreground="white")
                    return
                runtime_perms, special_perms = _extract_selected_permissions()
                special_perms_by_smali = _extract_selected_special_perms_by_smali()

                apk_path = Path(base_apk_var.get()).expanduser()

                if not apk_path.exists():
                    _log(f"[!] Base APK not found: {apk_path}")
                    status_color.set("red")
                    status_text.set("Build failed – base APK not found")
                    status_bar.configure(background="red", foreground="white")
                    btn_run.config(state=tk.NORMAL)
                    return

                run_build_from_ui(
                    smali_paths=paths,
                    base_apk=apk_path,
                    app_id=pkg_var.get(),
                    version=ver_var.get(),
                    log_fn=_log,
                    do_run=do_run,
                    runtime_permissions=runtime_perms,
                    special_permissions=special_perms,
                    special_perms_by_smali=special_perms_by_smali,
                )

                status_color.set("green")
                status_text.set("Build completed successfully")
                status_bar.configure(background="green", foreground="white")
            except Exception as e:
                _log(f"[✗] Build failed: {e}")
                status_color.set("red")
                status_text.set("Build failed – check logs")
                status_bar.configure(background="red", foreground="white")
            finally:
                btn_run.config(state=tk.NORMAL)

        # Disable buttons while building
        btn_run.config(state=tk.DISABLED)

        # Start thread
        threading.Thread(target=thread_target, daemon=True).start()

    btn_run.config(command=lambda: _build_clicked(True))

    # ========== Build Button Wiring ==============
    def _stop_clicked():
        def thread_target():
            try:
                stop_session(app_id=pkg_var.get(), log_fn=_log)
            except Exception as e:
                _log(f"[✗] Stop session error: {e}")
            finally:
                btn_run.config(state=tk.NORMAL)
                btn_stop.config(state=tk.NORMAL)
                status_color.set("black")
                status_text.set("Session stopped and cleaned up")
                status_bar.configure(background="black")

        btn_run.config(state=tk.DISABLED)
        btn_stop.config(state=tk.DISABLED)
        threading.Thread(target=thread_target, daemon=True).start()

    btn_stop.config(command=_stop_clicked)

    # -------------------------------------------------------------------------
    # Bottom: Command Output Log (same structure as Compile)
    # -------------------------------------------------------------------------
    log_holder = ttk.LabelFrame(outer, text="Command Output Log", bootstyle="info")
    log_holder.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

    inner = ttk.Frame(log_holder)
    inner.pack(fill="both", expand=True, padx=8, pady=8)

    global tab_builder_build_log_frame
    tab_builder_build_log_frame = inner

    # Let main.py mount the shared log into this holder without importing the module
    try:
        parent._log_holder = inner
    except Exception:
        pass
