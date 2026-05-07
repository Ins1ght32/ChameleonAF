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

## Included Anti-Forensic Features

ChameleonAF currently includes several anti-forensic and anti-analysis monitoring modules designed to detect common forensic acquisition or analyst interaction behaviours during Android investigations.

### 1. ADB Screen Capture Detection (`ADBScreenCapture.java`)

Monitors active system processes using elevated (`su`) access to detect execution of the Android `screencap` utility via ADB. The module continuously polls running processes and triggers telemetry events when a `screencap` process executed by the `shell` user is identified.

This feature is intended to detect attempts to capture the device display remotely during forensic examination or analyst interaction.

### 2. Anti-Agent Package Installation Detection (`AntiAgent.java`)

Registers a broadcast receiver that monitors package installation and replacement events (`PACKAGE_ADDED` and `PACKAGE_REPLACED`). The feature detects when a specified forensic, monitoring, or analyst application package is installed or updated on the device.

This allows the framework to identify deployment of targeted forensic tooling or agent-based collection applications during an examination workflow.

**Relevant references**

- K\. J. Karlsson and W. B. Glisson, "Android Anti-forensics: Modifying CyanogenMod," 2014 47th Hawaii International Conference on System Sciences, Waikoloa, HI, USA, 2014, pp. 4828-4837, doi: 10.1109/HICSS.2014.593

### 3. ADB Backup Detection (`AntiBackupDetect.java`)

Performs periodic monitoring of running processes using `su` and `ps` to detect Android backup-related services and commands, including references to `backup`, `BackupManager`, or `backupconfirm`.

The feature is intended to identify logical acquisition attempts using Android backup mechanisms, which have historically been leveraged in mobile forensic workflows for data extraction.

**Relevant references**

- Joseph Lim, Wilson Lim, Isaac Soon, Zhen Yu Kwok, Aloysus Koh, Digital Forensics Project in Singapore Institute of Technology, Dec. 2024
  
### 4. Honeytoken File Deployment and Monitoring (`HoneyTokens.java`)

Deploys decoy (“honeytoken”) files into device storage locations and monitors them for access activity using Linux `inotify` mechanisms executed with elevated privileges.

When the honeytoken files are accessed, modified, or interacted with, the framework records telemetry events. This enables detection of analyst browsing, filesystem inspection, or forensic extraction activity targeting user-accessible storage.

**Relevant references**

- DEFCONConference, “DEF CON 33 - Countering Forensics Software by Baiting Them - Weihan Goh, Joseph Lim & Isaac Soon,” YouTube, Oct. 10, 2025. https://www.youtube.com/watch?v=nUh9GVVhjD8 (accessed Mar. 3, 2026) [Additional Contributors - Wilson Lim, Zhen Yu Kwok, Aloysus Koh]

---

## License

This project is licensed under the **GNU General Public License v3.0**.

See the [LICENSE](LICENSE.md) file for details.
