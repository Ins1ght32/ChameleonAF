# modules/settings_manager.py
import os
import json

CONFIG_PATH = os.path.join("config", "user_settings.json")

def default_settings():
    return {
        # Existing
        "apktool_path": "",

        # Compiler/Controller shared
        "android_jar": "",
        "d8_path": "",
        "baksmali_jar": "",
        "javac_path": "",
        "java_path": "",
        "keystore_path": "",
        "adb_path": ""
    }

def load_settings():
    if not os.path.exists(CONFIG_PATH):
        save_settings(default_settings())
        return default_settings()
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            # Ensure missing keys get filled in
            defaults = default_settings()
            for k, v in defaults.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception:
        return default_settings()

def save_settings(settings):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(settings, f, indent=4)

def update_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
    return settings
