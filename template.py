# template.py
from pathlib import Path

folders = [
    "src/core",
    "src/scenarios",
    "src/modes",
    "src/utils",
    "transcripts",
    "recordings",
    "logs",
]

files = {
    "run_local.py": "",
    "run_call.py": "",
    "src/core/__init__.py": "",
    "src/core/config.py": "",
    "src/core/gemini_brain.py": "",
    "src/scenarios/__init__.py": "",
    "src/scenarios/scenarios.py": "",
    "src/modes/__init__.py": "",
    "src/modes/local_mode.py": "",
    "src/modes/twilio_mode.py": "",
    "src/utils/__init__.py": "",
    "src/utils/transcript_manager.py": "",
    "src/utils/audio_utils.py": "",
}

# Create folders
for folder in folders:
    Path(folder).mkdir(parents=True, exist_ok=True)

# Create files
for file in files:
    Path(file).parent.mkdir(parents=True, exist_ok=True)
    Path(file).touch(exist_ok=True)

print("✅ Project structure created successfully!")