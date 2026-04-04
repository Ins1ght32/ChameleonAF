# ChameleonAF – Anti-Forensic APK Instrumentation Framework

ChameleonAF is an anti-forensic instrumentation framework designed to support the development, compilation, deployment, and evaluation of Android anti-forensic features. The tool enables controlled feature injection, permission handling, root management, and execution telemetry for repeatable forensic tool testing and research.

---

## Repository Structure

```text
.
├── Chameleon/
│   └── Base Anti-Forensic APK (Android Studio project)
│
├── ChameleonAF/
│   └── Python-based Controller (main.py)
│
├── Anti-Forensic Feature Development Template.java
├── requirements.txt
└── README.md
```

### Chameleon (Base Anti-Forensic APK)
- Android Studio project copied out as a standalone folder.
- Acts as the base APK into which compiled anti-forensic features are injected.
- Users do **not** need to modify this folder unless they wish to:
  - Inspect inner workings
  - Upgrade core APK logic
  - Extend base APK capabilities

### ChameleonAF (Controller)
- Python-based controller application.
- Responsible for:
  - Compiling anti-forensic features
  - Building and signing the APK
  - Deploying and running the APK
  - Managing feature metadata, permissions, and execution telemetry
- This is the primary entry point for users.

### Anti-Forensic Feature Development Template
- Java template used for creating new anti-forensic feature modules.
- Provides the required structure for features that will be compiled and injected into the Chameleon base APK.
- Defines a consistent execution entry point and reporting mechanism so features remain compatible with the controller workflow.
- Users should modify this file when developing new anti-forensic logic, including:
  - Implementing feature behaviour inside the RUN BODY section
  - Adding any required helper methods
  - Triggering telemetry reporting when detection conditions are met

---

## Environment Requirements

### Operating System
- Windows 11

### Python
- Python 3.10 or newer

Install dependencies:
```
pip install -r requirements.txt
```

---

## Mandatory Setup (Important)

Before using the tool, the following paths must be configured in the Controller.

### Launch the Controller
```
cd ChameleonAF
python main.py
```

### Configure Tool Paths (Settings Tab)
Open the Settings tab in the Controller UI and configure the following fields:

| Setting           | Required | Description                                        |
| ----------------- | -------- | -------------------------------------------------- |
| apktool.jar Path  | Yes      | Required for APK decompilation and rebuild         |
| Android.jar Path  | Yes      | From Android SDK `platforms/<version>/android.jar` |
| Baksmali.jar Path | Yes      | Used to disassemble DEX into smali                 |

Failure to configure this minimum set of paths will cause compilation and build workflows to fail.

To note: There is a Baksmali.jar file located at ChameleonAF\modules\tools, for use.

### Assumed Installed via Windows PATH
The following tools are assumed to already be installed and accessible via Windows environment variables, so they do not need to be edited in the Controller UI:
- Java
- Javac
- D8
- Android SDK
- ADB
- Android Keystore tools

These paths may be optionally overridden in the Settings tab, but PATH-based resolution is assumed by default.

---

## License

This project is licensed under the **GNU General Public License v3.0**.

See the [LICENSE](LICENSE.md) file for details.
