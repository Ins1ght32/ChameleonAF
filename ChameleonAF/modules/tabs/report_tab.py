# modules/tabs/report_tab.py
import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *
from pathlib import Path
from datetime import datetime, date, timedelta
import json
import re

# --- Import your feature API in modules/ ---
from modules import feature_api  # provides init_engine(), get_indexed_features()

# ---- Config ----
REPORT_DIR = Path("reports")
REPORT_GLOB = "*.ndjson"
DATE_FMT = "%Y-%m-%d %H:%M:%S"

SHORT_TOKEN_RE = re.compile(r"([A-Za-z0-9_]+)(?:[\s\-:|].*)?$")


def build_report_tab(parent):
    """
    Report tab with date-range filtering, NDJSON parsing, and feature name mapping via modules/feature_api.py.
    """

    # ===== Root container =====
    outer = ttk.Frame(parent)
    outer.pack(fill="both", expand=True, padx=12, pady=12)

    # ===== Top bar =====
    top = ttk.Frame(outer)
    top.pack(fill="x", pady=(0, 8))

    ttk.Label(top, text="Build & Test Reports", font=("-size", 12, "-weight", "bold")).pack(side="left")

    legend = ttk.Frame(top)
    legend.pack(side="right")
    ttk.Label(legend, text="Legends: ", foreground="white").pack(side="left", padx=(0, 10))
    ttk.Label(legend, text="Triggered ✓", bootstyle=SUCCESS).pack(side="left", padx=(0, 10))
    ttk.Label(legend, text="Not Triggered ✗", bootstyle=WARNING).pack(side="left", padx=(0, 10))
    ttk.Label(legend, text="Initialisation Pending", bootstyle=DANGER).pack(side="left", padx=(0, 10))
    ttk.Label(legend, text="Not Initialised", bootstyle=SECONDARY).pack(side="left")

    # ===== Panes =====
    panes = ttk.Panedwindow(outer, orient="horizontal")
    panes.pack(fill="both", expand=True)

    # ---------------- Left Pane ----------------
    left = ttk.Frame(panes)
    panes.add(left, weight=0) 

    # --- Date Filter Row ---
    filter_row = ttk.Frame(left)
    filter_row.pack(fill="x", pady=(0, 6))

    ttk.Label(filter_row, text="From (YYYY-MM-DD):").pack(side="left")
    from_var = tk.StringVar()
    from_entry = ttk.Entry(filter_row, textvariable=from_var, width=12)
    from_entry.pack(side="left", padx=(4, 12))

    ttk.Label(filter_row, text="To (YYYY-MM-DD):").pack(side="left")
    to_var = tk.StringVar()
    to_entry = ttk.Entry(filter_row, textvariable=to_var, width=12)
    to_entry.pack(side="left", padx=(4, 12))

    def set_quick(span_days: int):
        today = date.today()
        start = today - timedelta(days=span_days - 1)
        from_var.set(start.isoformat())
        to_var.set(today.isoformat())
        on_apply_filter()

    ttk.Button(filter_row, text="Today", command=lambda: set_quick(1)).pack(side="left", padx=(0, 6))
    ttk.Button(filter_row, text="Last 3d", command=lambda: set_quick(3)).pack(side="left", padx=(0, 6))
    ttk.Button(filter_row, text="Last 7d", command=lambda: set_quick(7)).pack(side="left", padx=(0, 6))

    # --- New row for Clear / Apply / View Raw ---
    action_row = ttk.Frame(left)
    action_row.pack(fill="x", pady=(0, 6))

    def on_view_raw():
        sel = report_tree.focus()
        if not sel:
            return
        _ts, file, _size = report_tree.item(sel, "values")
        path = REPORT_DIR / file
        try:
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            pretty_lines = []
            for line in lines:
                try:
                    obj = json.loads(line)
                    pretty_lines.append(json.dumps(obj, indent=4))
                except Exception:
                    pretty_lines.append(line)
            raw_content = "\n\n".join(pretty_lines)
        except Exception as e:
            raw_content = f"Error reading file: {e}"

        win = tk.Toplevel(outer)
        win.title(f"Raw Report: {file}")
        win.geometry("1400x600")

        # Frame with scrollbars + text
        frame = ttk.Frame(win)
        frame.pack(fill="both", expand=True, padx=6, pady=6)

        txt = tk.Text(frame, wrap="none", font=("Courier New", 10))
        txt.insert("1.0", raw_content)
        txt.config(state="disabled")

        yscroll = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
        xscroll = ttk.Scrollbar(frame, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        txt.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    ttk.Button(action_row, text="Clear", command=lambda: on_clear_filter()).pack(side="left", padx=(0, 6))
    ttk.Button(action_row, text="Apply", command=lambda: on_apply_filter()).pack(side="left", padx=(0, 6))

    sep = ttk.Separator(action_row, orient="vertical")
    sep.pack(side="left", fill="y", padx=8, pady=2)

    ttk.Button(action_row, text="View Raw Report", command=on_view_raw).pack(side="left", padx=(6, 0))

    status_lbl = ttk.Label(left, text="Ready.", bootstyle=INFO)
    status_lbl.pack(fill="x", pady=(0, 6))

    report_cols = ("Timestamp", "File", "Size")
    report_tree = ttk.Treeview(left, columns=report_cols, show="headings", height=14)
    for c in report_cols:
        report_tree.heading(c, text=c)
        anchor = "w" if c != "Size" else "e"
        width = {"Timestamp": 160, "File": 260, "Size": 80}.get(c, 140)
        report_tree.column(c, width=width, anchor=anchor)
    report_tree.pack(fill="both", expand=True)

    left_scroll = ttk.Scrollbar(left, orient="vertical", command=report_tree.yview)
    report_tree.configure(yscrollcommand=left_scroll.set)
    left_scroll.place(in_=report_tree, relx=1.0, rely=0, relheight=1.0, x=-2)

    # ---------------- Right Pane ----------------
    right = ttk.Frame(panes)
    panes.add(right, weight=2)

    summary = ttk.Labelframe(right, text="Selected Report")
    summary.pack(fill="x", pady=(0, 8))
    summary_grid = ttk.Frame(summary);
    summary_grid.pack(fill="x", padx=8, pady=8)

    lbl_ts_val = ttk.Label(summary_grid, text="—")
    lbl_file_val = ttk.Label(summary_grid, text="—")
    lbl_status_val = ttk.Label(summary_grid, text="—", bootstyle=SECONDARY)

    def _grid_kv(parent, key, value_widget, row):
        ttk.Label(parent, text=key).grid(row=row, column=0, sticky="w", padx=(0, 8), pady=2)
        value_widget.grid(row=row, column=1, sticky="w", padx=(0, 8), pady=2)

    _grid_kv(summary_grid, "Timestamp:", lbl_ts_val, row=0)
    _grid_kv(summary_grid, "File:", lbl_file_val, row=1)
    _grid_kv(summary_grid, "Overall Status:", lbl_status_val, row=2)

    kpi = ttk.Frame(right);
    kpi.pack(fill="x", pady=(0, 8))

    def _kpi_badge(parent, label, value, bootstyle=SECONDARY):
        f = ttk.Frame(parent)
        f.pack(side="left", padx=(0, 12))

        ttk.Label(f, text=label).pack(side="top", anchor="w")

        # Only make the Features counter white
        if label.lower() == "features":
            v = ttk.Label(f, text=value, bootstyle=bootstyle, foreground="white")
        else:
            v = ttk.Label(f, text=value, bootstyle=bootstyle)

        v.configure(padding=(12, 4))
        v.pack(side="top", anchor="w", pady=(2, 0))

        return v

    kpi_total_val = _kpi_badge(kpi, "Features", "0")
    kpi_trig_val = _kpi_badge(kpi, "Triggered", "0", bootstyle=SUCCESS)
    kpi_not_val = _kpi_badge(kpi, "Not Triggered", "0", bootstyle=WARNING)
    kpi_pend_val = _kpi_badge(kpi, "Initialisation Pending", "0", bootstyle=DANGER)

    matrix = ttk.Labelframe(right, text="Feature Status")
    matrix.pack(fill="both", expand=True)
    # --- Added Class Path column ---
    feat_cols = ("Feature", "Class Path", "Initialised", "Triggered", "No. of Triggers", "Latest Trigger Time (UTC)", "Notes")
    feat_tree = ttk.Treeview(matrix, columns=feat_cols, show="headings", height=12)
    for c in feat_cols:
        feat_tree.heading(c, text=c)
        width = {
            "Feature": 180,
            "Class Path": 300,
            "Initialised": 100,
            "Triggered": 100,
            "No. of Triggers": 120,
            "Latest Trigger Time (UTC)": 210,
            "Notes": 260,
        }[c]
        anchor = "center" if c in ("Initialised", "Triggered", "No. of Triggers") else "w"
        feat_tree.column(c, width=width, anchor=anchor)
    feat_tree.pack(fill="both", expand=True, padx=6, pady=6)

    feat_tree.tag_configure("ok", foreground="#1f7a1f")  # Triggered ✓ (green)
    feat_tree.tag_configure("warn", foreground="#9a6b00")  # Not Triggered ✗ (amber)
    feat_tree.tag_configure("bad", foreground="#9a1f1f")  # Init Pending (red)
    feat_tree.tag_configure("muted", foreground="#777777")  # Not Initialised (grey)

    feat_scroll = ttk.Scrollbar(matrix, orient="vertical", command=feat_tree.yview)
    feat_tree.configure(yscrollcommand=feat_scroll.set)
    feat_scroll.place(in_=feat_tree, relx=1.0, rely=0, relheight=1.0, x=-2)

    all_rows_cache = []

    feature_api.init_engine()
    feature_name_map = _build_feature_map_from_api()

    def _set_status(msg: str):
        status_lbl.configure(text=msg)

    def _human_size(nbytes: int) -> str:
        units = ["B", "KB", "MB", "GB", "TB"];
        i = 0;
        size = float(nbytes)
        while size >= 1024 and i < len(units) - 1: size /= 1024.0; i += 1
        return f"{size:.0f} {units[i]}"

    def _parse_any_ts(value):
        """
        Parse common timestamp formats from your NDJSON:
          - 2026-02-28T06:59:42.948+0000
          - 2026-02-28T06:59:42.948+00:00
          - 2026-02-28T06:59:42.948Z
          - 2026-02-28T06:59:42+0000
          - epoch seconds (int/float)
        Returns a datetime (timezone-aware if possible) or None.
        """
        if value is None:
            return None

        # epoch seconds
        if isinstance(value, (int, float)):
            try:
                return datetime.fromtimestamp(float(value))
            except Exception:
                return None

        if not isinstance(value, str):
            return None

        s = value.strip()
        if not s:
            return None

        # Normalize Zulu
        if s.endswith("Z"):
            # datetime.strptime with %z doesn't accept bare Z, convert to +0000
            s = s[:-1] + "+0000"

        # Try formats (note: %z supports +0000)
        fmts = (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f%z",
        )

        # Handle offsets like +00:00 by removing colon for strptime %z
        # e.g. 2026-...+00:00 -> 2026-...+0000
        if len(s) >= 6 and (s[-6] in ("+", "-")) and s[-3] == ":":
            s = s[:-3] + s[-2:]

        for fmt in fmts:
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass

        return None

    def _report_timestamp_from_init_complete(path: Path) -> str:
        """
        Return timestamp string based on FIRST 'initialisation_completed' found in file.
        If none exists -> 'FAILED Due to no initialisations'
        """
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue

                    evt = (o.get("event") or o.get("state") or o.get("action") or o.get("status") or "")
                    evt_l = str(evt).lower()

                    if "initialisation_completed" in evt_l:
                        dt = _parse_any_ts(o.get("ts") or o.get("time") or o.get("timestamp"))
                        if dt is None:
                            # Fallback: show raw if parsing fails
                            raw = o.get("ts") or o.get("time") or o.get("timestamp")
                            return str(raw) if raw else "FAILED DUE TO NO INITIALISATIONS"

                        return dt.strftime(DATE_FMT)

        except Exception:
            pass

        return "FAILED Due to no initialisations"

    def _scan_reports():
        rows = []
        try:
            REPORT_DIR.mkdir(parents=True, exist_ok=True)
            files = sorted(REPORT_DIR.glob(REPORT_GLOB),
                           key=lambda p: p.stat().st_mtime,
                           reverse=True)
            for p in files:
                try:
                    ts = _report_timestamp_from_init_complete(p)
                    mtime = datetime.fromtimestamp(p.stat().st_mtime)

                    # --- Apply date filter if set ---
                    f_str, t_str = from_var.get().strip(), to_var.get().strip()
                    if f_str:
                        try:
                            f_dt = datetime.strptime(f_str, "%Y-%m-%d")
                            if mtime.date() < f_dt.date():
                                continue
                        except Exception:
                            pass
                    if t_str:
                        try:
                            t_dt = datetime.strptime(t_str, "%Y-%m-%d")
                            if mtime.date() > t_dt.date():
                                continue
                        except Exception:
                            pass

                    rows.append((ts, p.name, _human_size(p.stat().st_size)))
                except Exception:
                    pass
        except Exception as e:
            _set_status(f"Scan error: {e}")
        return rows

    def _populate_reports(rows):
        report_tree.delete(*report_tree.get_children())
        for row in rows:
            report_tree.insert("", "end", values=row)

    def parse_report_features(path: Path):
        """
            Parse a .ndjson file and aggregate per-feature status:
                returns list of rows: (Feature, Class Path, Initialised, Triggered, Triggered Time, Notes, tag)
            Rules:
                - Feature key is display name via feature_api.
                - Class Path column shows the FQCN directly.
        """
        per = {}

        def parse_ts(o):
            candidates = [o.get("ts"), o.get("time"), o.get("timestamp")]
            for c in candidates:
                if c is None: continue
                if isinstance(c, (int, float)):
                    try:
                        return datetime.fromtimestamp(float(c)).strftime(DATE_FMT)
                    except Exception:
                        pass
                if isinstance(c, str):
                    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"):
                        try:
                            return datetime.strptime(c.replace("Z", ""), fmt).strftime(DATE_FMT)
                        except Exception:
                            pass
                    return c
            return "—"

        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        o = json.loads(line)
                    except Exception:
                        continue

                    # Take the raw FQCN (class path) directly
                    fqcn = o.get("class") or o.get("fqcn") or o.get("feature") or o.get("name") or "Unknown"

                    # Extract last segment after '.' as class name
                    class_name = fqcn.split(".")[-1]

                    # Look up display name via class_name; fallback to class_name itself
                    disp = feature_name_map.get(class_name, class_name)

                    st = per.setdefault(disp, {
                        "fqcn": fqcn,
                        "init": False,
                        "trig": False,
                        "trigger_count": 0,
                        "latest_trigger_dt": None,
                        "latest_trigger_time": "—",
                        "saw_init": False,
                    })

                    evt = (o.get("event") or o.get("state") or o.get("action") or o.get("status") or "")
                    evt_l = str(evt).lower()

                    if "initialisation_completed" in evt_l:
                        st["init"] = True
                    elif "initialis" in evt_l:
                        st["saw_init"] = True

                    if "trigger" in evt_l or "fired" in evt_l or "activated" in evt_l:
                        st["trig"] = True
                        st["trigger_count"] += 1

                        raw_ts = o.get("ts") or o.get("time") or o.get("timestamp")
                        dt = _parse_any_ts(raw_ts)

                        if dt is not None:
                            if st["latest_trigger_dt"] is None or dt > st["latest_trigger_dt"]:
                                st["latest_trigger_dt"] = dt
                                st["latest_trigger_time"] = dt.strftime(DATE_FMT)
                        else:
                            st["latest_trigger_time"] = parse_ts(o)

        except Exception as e:
            _set_status(f"Parse error: {e}")

        rows = []
        for disp, st in sorted(per.items(), key=lambda x: x[0].lower()):
            if st["init"]:
                init_v = "✓"
                if st["trig"]:
                    trig_v, tag, note = "✓", "ok", "Feature triggered successfully"
                else:
                    trig_v, tag, note = "✗", "warn", "Initialised but not triggered"
            else:
                init_v = "✗"
                if st.get("saw_init"):
                    trig_v, tag, note = "✗", "bad", "Initialisation started but not completed"
                else:
                    trig_v, tag, note = "✗", "muted", "Feature never initialised"
            rows.append((disp, st["fqcn"], init_v, trig_v, st["trigger_count"], st["latest_trigger_time"], note, tag,))
        return rows

    def _populate_features(rows):
        feat_tree.delete(*feat_tree.get_children())
        for row in rows:
            feat_tree.insert("", "end", values=row[:-1], tags=(row[-1],))

        total = len(rows)

        triggered = sum(1 for r in rows if r[-1] == "ok")
        not_trig = sum(1 for r in rows if r[-1] == "warn")
        pending = sum(1 for r in rows if r[-1] == "bad")

        kpi_total_val.configure(text=str(total))
        kpi_trig_val.configure(text=str(triggered))
        kpi_not_val.configure(text=str(not_trig))
        kpi_pend_val.configure(text=str(pending))

    def on_select_report(_event=None):
        sel = report_tree.focus()
        if not sel:
            return
        ts, file, _size = report_tree.item(sel, "values")
        lbl_ts_val.configure(text=ts)
        lbl_file_val.configure(text=file)

        path = REPORT_DIR / file
        rows = parse_report_features(path)

        # Count ticks and crosses
        total = len(rows)
        ticks = sum(1 for r in rows if r[2] == "✓" and r[3] == "✓")
        crosses = total - ticks

        # ---- Overall Status ----
        total = len(rows)

        pending = sum(1 for r in rows if r[-1] == "bad")  # init started but not completed
        not_trig = sum(1 for r in rows if r[-1] == "warn")  # initialised but not triggered
        trig = sum(1 for r in rows if r[-1] == "ok")  # triggered
        not_init = sum(1 for r in rows if r[-1] == "muted")  # never initialised

        # Only compare features that have lifecycle signal (exclude never-initialised)
        considered = total - not_init

        if pending >= 1:
            overall, style = "SEVERE WARNING", DANGER

        elif considered <= 0:
            overall, style = "NO INITIALISED FEATURES", SECONDARY

        # ---- "ALL" precedence (covers considered == 1 too) ----
        elif trig == considered:
            overall, style = "ALL TRIGGERED", SUCCESS

        elif not_trig == considered:
            overall, style = "ALL NOT TRIGGERED", WARNING

        else:
            # Majority wording for mixed states
            LARGE_MAJ_RATIO = 0.60
            LARGE_MAJ_MIN_N = 3  # only call it "large majority" if we have enough items

            def is_large_majority(win_count: int) -> bool:
                return (considered >= LARGE_MAJ_MIN_N) and ((win_count / considered) >= LARGE_MAJ_RATIO)

            if trig > not_trig:
                overall, style = ("LARGE MAJORITY TRIGGERED", SUCCESS) if is_large_majority(trig) else (
                "MAJORITY TRIGGERED", SUCCESS)
            elif not_trig > trig:
                overall, style = ("LARGE MAJORITY NOT TRIGGERED", WARNING) if is_large_majority(not_trig) else (
                "MAJORITY NOT TRIGGERED", WARNING)
            else:
                overall, style = "MIXED", INFO

        lbl_status_val.configure(text=overall, bootstyle=style)

        _populate_features(rows)

    report_tree.bind("<<TreeviewSelect>>", on_select_report)
    report_tree.bind("<Double-1>", lambda e: on_view_raw())
    from_entry.bind("<Return>", lambda e: on_apply_filter())
    to_entry.bind("<Return>", lambda e: on_apply_filter())

    # Auto-refresh when user switches into this tab
    def _on_tab_changed(event):
        nb = event.widget
        try:
            sel = nb.nametowidget(nb.select())
        except Exception:
            return
        if str(sel) == str(outer):  # compare widget path
            refresh_list(select_first=True)

    # Bind only if parent is a Notebook
    parent.bind("<<NotebookTabChanged>>", _on_tab_changed)

    def refresh_list(select_first=True):
        nonlocal all_rows_cache
        all_rows_cache = _scan_reports()
        _populate_reports(all_rows_cache)
        status_lbl.configure(text=f"Found {len(all_rows_cache)} report(s).")
        if select_first and report_tree.get_children():
            first = report_tree.get_children()[0]
            report_tree.selection_set(first)
            report_tree.focus(first)
            on_select_report()

    def on_apply_filter():
        refresh_list(select_first=True)

    def on_clear_filter():
        from_var.set("");
        to_var.set("");
        refresh_list(select_first=True)

    outer.bind("<Visibility>", lambda e: refresh_list(select_first=True))

    refresh_list(select_first=True)


# ===== Helpers =====

def _build_feature_map_from_api() -> dict:
    mapping = {}
    try:
        indexed = feature_api.get_indexed_features()
        for row in indexed:
            java_path = row.get("java_path") or ""
            name = row.get("name") or ""

            if java_path and name:
                # Take filename without extension as the key (e.g. AntiAgent.java -> AntiAgent)
                class_name = Path(java_path).stem
                mapping[class_name] = str(name)
    except Exception as e:
        print(f"Feature map build error: {e}")
    return mapping
