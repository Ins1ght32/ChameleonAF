# tabs/help_tab.py
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Scrollbar, Canvas, Frame, Label
from ttkbootstrap.constants import *

def build_help_tab(parent):
    """
    Builds the Help tab UI.
    """
    # Canvas + scrollbar for scrolling content
    canvas = Canvas(parent)
    scrollbar = Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Mousewheel support
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
    canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))

    # Layout
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ---- Under Construction Notice ----
    notice = Label(
        scrollable_frame,
        text="⚠️ This Help page is under development and will be updated in a future release.",
        font=("Helvetica", 11, "italic"),
        foreground="#aa0000",
        justify="center",
        anchor="center"
    )
    notice.pack(fill="x", pady=(20, 10), padx=10)

    # Example help sections (update to suit new project)
    sections = {
        "Overview": (
            "This tool is a modular Android forensic feature builder and test harness.\n\n"
            "It allows you to:\n"
            "• Compile Java-based feature modules into Smali artifacts\n"
            "• Attach metadata such as permissions and root requirements\n"
            "• Inject selected features into a base APK\n"
            "• Build and deploy the modified APK\n"
            "• Validate feature execution through structured runtime reports\n\n"
            "The workflow is intentionally separated into Compile → Build → Report stages "
            "to ensure traceability and repeatability during forensic testing."
        ),

        "Compile Tab": (
            "The Compile tab converts a single Java feature into one or more Smali artifacts "
            "and records its metadata in the feature index.\n\n"
            "Key concepts:\n"
            "• A feature represents a single forensic or anti-forensic capability\n"
            "• Compilation does NOT modify any APK\n"
            "• Compiled features are versioned and reusable across builds\n\n"
            "Main actions:\n"
            "• Import .java File – Copies a feature source into the features directory\n"
            "• Compile – Generates Smali, extracts metadata, and indexes the feature\n"
            "• Manage Compiled Versions – Switch or delete historical compiled outputs\n\n"
            "Permissions handling:\n"
            "• Normal permissions are install-time only\n"
            "• Runtime permissions require user or ADB grant\n"
            "• Special permissions require explicit system settings interaction\n\n"
            "Metadata recorded at compile time is later consumed automatically by the Build tab."
        ),

        "Build Tab": (
            "The Build tab assembles a final APK using selected compiled features.\n\n"
            "Left panel:\n"
            "• Indexed Features – Displays all compiled features and their metadata\n"
            "• Selected for Build – Controls which features are injected into the APK\n\n"
            "Right panel:\n"
            "• Base APK Path – Original APK to inject into\n"
            "• Output App ID – Package name for the rebuilt APK\n"
            "• App Version Name – Version string for the rebuilt APK\n\n"
            "Build process:\n"
            "• Injects Smali code into the decoded APK\n"
            "• Merges runtime permissions into the manifest\n"
            "• Tracks special permissions per feature for post-install handling\n"
            "• Rebuilds, signs, and optionally runs the APK\n\n"
            "Build status is shown using traffic-light indicators and detailed command logs."
        ),

        "Permissions Model": (
            "Permissions are handled in three categories:\n\n"
            "Normal permissions:\n"
            "• Declared in the manifest\n"
            "• Granted automatically at install time\n\n"
            "Runtime permissions:\n"
            "• Granted via user prompt or adb shell pm grant\n"
            "• Required for accessing protected user data\n\n"
            "Special permissions:\n"
            "• Require manual enablement in system settings\n"
            "• Cannot be granted silently or via adb\n\n"
            "The tool tracks permission intent for each feature but does not bypass "
            "Android security enforcement mechanisms."
        ),

        "Report Tab": (
            "The Report tab visualises runtime behaviour of injected features.\n\n"
            "Reports:\n"
            "• Stored as NDJSON files\n"
            "• Each line represents a lifecycle or trigger event\n\n"
            "Left panel:\n"
            "• Date filtering\n"
            "• Report file selection\n"
            "• Raw report viewer\n\n"
            "Right panel:\n"
            "• Per-feature execution status\n"
            "• Initialisation and trigger state\n"
            "• Trigger timestamps and notes\n\n"
            "Status meanings:\n"
            "• Triggered – Feature executed successfully\n"
            "• Not Triggered – Initialised but no trigger occurred\n"
            "• Initialisation Pending – Partial lifecycle observed\n"
            "• Not Initialised – Feature never loaded\n\n"
            "This view is intended for forensic validation and tool efficacy testing."
        ),

        "Settings Tab": (
            "The Settings tab defines external tool dependencies and runtime paths.\n\n"
            "Configured tools include:\n"
            "• apktool\n"
            "• baksmali\n"
            "• d8\n"
            "• Java runtime and compiler\n"
            "• ADB\n"
            "• Keystore\n\n"
            "Notes:\n"
            "• Leave fields empty to fall back to PATH or environment variables\n"
            "• Changes apply immediately after saving\n"
            "• Incorrect paths will cause compile or build failures\n"
        ),

        "Operational Notes": (
            "This tool is designed for controlled forensic testing environments.\n\n"
            "Recommendations:\n"
            "• Use emulator or test devices only\n"
            "• Maintain original APK hashes for integrity comparison\n"
            "• Treat compiled features as immutable once validated\n"
            "• Use reports as evidence artifacts, not raw logs\n\n"
            "Misuse of injected capabilities outside authorised testing contexts "
            "may violate platform or legal restrictions."
        ),
    }

    for title, content in sections.items():
        Label(scrollable_frame, text=title, font=("Helvetica", 16, "bold")).pack(anchor="w", pady=(15, 5), padx=10)
        Label(scrollable_frame, text=content, wraplength=1200, justify="left").pack(anchor="w", padx=20)
