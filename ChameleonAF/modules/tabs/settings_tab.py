# modules/tabs/settings_tab.py

import ttkbootstrap as tb
from tkinter import ttk, filedialog
from ttkbootstrap.tooltip import ToolTip
from modules import settings_manager, system_utils


def create_settings_tab(notebook):
    tab_settings = ttk.Frame(notebook)
    settings = settings_manager.load_settings()

    def browse_file(entry, filetypes=[("All files", "*.*")]):
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            entry.delete(0, 'end')
            entry.insert(0, path)

    def browse_dir(entry):
        path = filedialog.askdirectory()
        if path:
            entry.delete(0, 'end')
            entry.insert(0, path)

    def save_and_reload():
        new_settings = settings_manager.load_settings()
        for field, entry in entries.items():
            if isinstance(entry, tb.StringVar):
                new_settings[field] = entry.get()
            else:
                new_settings[field] = entry.get()
        settings_manager.save_settings(new_settings)
        tb.dialogs.Messagebox.show_info("Settings saved successfully.")

    def create_path_row(parent, label_text, tip_text, key_name, is_dir=False):
        label_frame = ttk.Frame(parent)
        label_frame.pack(anchor="w", padx=10, pady=(10, 0), fill="x")
        ttk.Label(label_frame, text=label_text, bootstyle="default").pack(side="left")
        tip_label = ttk.Label(label_frame, text="❓", foreground="red", cursor="question_arrow")
        tip_label.pack(side="left", padx=(5, 0))
        ToolTip(tip_label, text=tip_text)
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=10, pady=2)
        entry = ttk.Entry(frame)
        entry.insert(0, settings.get(key_name, ""))
        entry.pack(side="left", fill="x", expand=True)
        browse_cmd = browse_dir if is_dir else browse_file
        ttk.Button(frame, text="Browse", command=lambda: browse_cmd(entry)).pack(side="left", padx=5)
        entries[key_name] = entry

    entries = {}

    # IP Address only
    status_frame = ttk.Frame(tab_settings)
    status_frame.pack(pady=(10, 0), fill="x")
    ip_text = f"💻 Your IP Address: {system_utils.get_ip()}"
    ttk.Label(status_frame, text=ip_text, bootstyle="info").pack(side="top", padx=15)

    ttk.Separator(tab_settings, bootstyle="secondary").pack(fill="x", padx=10, pady=(10, 20))

    # Path fields
    create_path_row(tab_settings, "apktool.jar Path:", "Required for APK decoding.", "apktool_path")
    create_path_row(tab_settings, "Android.jar Path:", "From Android SDK platforms/<version>/android.jar",
                    "android_jar")
    create_path_row(tab_settings, "D8 Path:", "From Android SDK build-tools/<version>/d8.bat", "d8_path")
    create_path_row(tab_settings, "Baksmali.jar Path:", "Path to baksmali JAR file", "baksmali_jar")
    create_path_row(tab_settings, "Javac Path:", "Java compiler executable (leave empty to use PATH)", "javac_path")
    create_path_row(tab_settings, "Java Path:", "Java runtime executable (leave empty to use PATH)", "java_path")
    create_path_row(tab_settings, "Keystore Path:", "Android debug keystore or custom keystore", "keystore_path")
    create_path_row(tab_settings, "ADB Path:", "ADB executable (leave empty to use PATH)", "adb_path")

    # Save button
    ttk.Button(tab_settings, text="💾 Save Settings", command=save_and_reload, bootstyle="success").pack(pady=20, anchor="center")

    return tab_settings
