import ttkbootstrap as tb
from tkinter import ttk
from modules.tabs import compile_tab
from modules.tabs.help_tab import build_help_tab
from modules.tabs.build_tab import build_build_tab
from modules.tabs.report_tab import build_report_tab
from modules.tabs.settings_tab import create_settings_tab
import sys
import io
import os
import tkinter as tk  # for TextRedirector hints

# UTF-8 safe stdout/stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
os.environ["PYTHONIOENCODING"] = "utf-8"

# Redirector so print()/tracebacks go to the log Text widget
class TextRedirector(io.TextIOBase):
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget

    def write(self, s):
        if not s:
            return 0
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", s)
        self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
        return len(s)

    def flush(self):
        pass

# Main window setup
app = tb.Window(themename="vapor")
app.title("ChameleonAF - Anti-Forensic APK Instrumentation Framework")
app.geometry("3000x1500")
# app.iconbitmap("icon.ico")  # Uncomment if you have an icon

# Notebook (tabs container)
notebook = ttk.Notebook(app, bootstyle="dark")
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Shared log container (mounted into specific tabs dynamically)
log_frame_container = ttk.Frame()
shared_output_text = tb.Text(
    log_frame_container,
    height=10,
    state="disabled",
    wrap="word",
    bg="black",
    fg="lightgreen"
)
output_scroll = ttk.Scrollbar(log_frame_container, orient="vertical", command=shared_output_text.yview)
shared_output_text.configure(yscrollcommand=output_scroll.set)
shared_output_text.pack(side="left", fill="both", expand=True, padx=(5, 0), pady=5)
output_scroll.pack(side="right", fill="y", padx=(0, 5), pady=5)

# Pipe stdout/stderr to the shared output log
sys.stdout = TextRedirector(shared_output_text)
sys.stderr = TextRedirector(shared_output_text)

# Tabs
tab_help = ttk.Frame(notebook)
notebook.add(tab_help, text="🆘 Help")

tab_build = ttk.Frame(notebook)
notebook.add(tab_build, text="🧱 Build")

tab_compile = ttk.Frame(notebook)
notebook.add(tab_compile, text="🛠 Compile")

tab_report = ttk.Frame(notebook)
notebook.add(tab_report, text="📊 Report")

# Settings tab stays at the end
tab_settings = create_settings_tab(notebook)
notebook.add(tab_settings, text="⚙ Settings")

# Build each tab's UI
build_help_tab(tab_help)
build_build_tab(tab_build, shared_output_text)

# IMPORTANT: build the Compile tab via the module (so the module-level holder gets set)
compile_tab.build_compile_tab(tab_compile)  # correct arity (no shared_output_text arg)

build_report_tab(tab_report)

# Move shared log when switching tabs (show under Build/Compile)
def on_tab_change(event):
    selected = event.widget.tab(event.widget.select(), "text")

    # Always detach from any previous parent before re-mounting
    log_frame_container.pack_forget()

    if selected == "🛠 Compile":
        # Use the up-to-date holder from the module (NOT a copied value)
        target = compile_tab.tab_builder_compile_log_frame or tab_compile
        log_frame_container.pack(in_=target, fill="both", expand=True)

        refresh_cb = getattr(compile_tab, "tab_builder_compile_refresh_callback", None)
        if callable(refresh_cb):
            try:
                refresh_cb()
            except Exception as e:
                print(f"[Compile Tab] Refresh on enter failed: {e}")
    elif selected == "🧱 Build":
        current_tab = event.widget.nametowidget(event.widget.select())
        target = getattr(current_tab, "_log_holder", None)
        log_frame_container.pack(in_=(target or current_tab), fill="both", expand=True)
    else:
        # Hide log on tabs that don't have a holder
        log_frame_container.pack_forget()

notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# Default log placement: start under Compile (force reparenting)
default_target = compile_tab.tab_builder_compile_log_frame or tab_compile
log_frame_container.pack_forget()
log_frame_container.pack(in_=default_target, fill="both", expand=True)

# Start app
app.mainloop()
