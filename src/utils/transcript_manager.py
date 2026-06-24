"""
transcript_manager.py - Saves transcripts and bug reports

OOP Concept: Single Responsibility Principle (SRP)
This class does ONE thing only: save and manage conversation data.

SRP means each class should have only ONE reason to change.
If saving logic changes, only THIS file changes.
Nothing else is affected.
"""

import os
import json
from datetime import datetime
from typing import Dict, List
from src.core.config import config


class TranscriptManager:
    """
    OOP Concept: Constructor sets up the environment.
    All directory creation happens here once,
    not scattered across multiple files.
    """

    def __init__(self):
        self.transcripts_dir = config.transcripts_dir
        self.recordings_dir  = config.recordings_dir
        self.logs_dir        = config.logs_dir
        self._ensure_directories()

    def _ensure_directories(self):
        """
        Private method -- creates folders if they don't exist.
        Called automatically in __init__ so caller never has to worry.
        """
        for directory in [self.transcripts_dir, self.recordings_dir, self.logs_dir]:
            os.makedirs(directory, exist_ok=True)
        print("[TranscriptManager] Directories ready")

    def save_transcript(self, summary: Dict, call_id: str) -> str:
        """
        Saves human readable transcript as a .txt file.
        Returns the file path where it was saved.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{call_id}_{timestamp}.txt"
        filepath  = os.path.join(self.transcripts_dir, filename)

        with open(filepath, "w") as f:
            f.write(self._format_transcript(summary))

        print(f"[TranscriptManager] Transcript saved: {filepath}")
        return filepath

    def save_json(self, summary: Dict, call_id: str) -> str:
        """
        Saves raw data as .json file.
        Useful for programmatic analysis later.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"{call_id}_{timestamp}.json"
        filepath  = os.path.join(self.transcripts_dir, filename)

        with open(filepath, "w") as f:
            json.dump(summary, f, indent=2)

        print(f"[TranscriptManager] JSON saved: {filepath}")
        return filepath

    def save_bug_report(self, bugs: List[str], scenario_name: str, call_id: str):
        """
        Appends bugs to a master bug_report.md file.
        All bugs from all calls go into ONE file.
        """
        if not bugs:
            print("[TranscriptManager] No bugs found for this call")
            return

        filepath  = os.path.join(self.logs_dir, "bug_report.md")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(filepath, "a") as f:
            f.write(f"\n\n## [{timestamp}] {scenario_name}\n")
            f.write(f"**Call ID:** {call_id}\n")
            for i, bug in enumerate(bugs, 1):
                f.write(f"\n### Bug {i}\n")
                f.write(f"**Description:** {bug}\n")
                f.write(f"**Transcript:** transcripts/{call_id}.txt\n")

        print(f"[TranscriptManager] Bug report updated: {filepath}")

    # ─────────────────────────────────────────
    # Private formatting method
    # ─────────────────────────────────────────

    def _format_transcript(self, summary: Dict) -> str:
        """
        OOP Concept: Private helper method
        Converts raw dictionary data into
        a clean readable text format.
        Only TranscriptManager needs this.
        """
        lines = []

        lines.append("=" * 60)
        lines.append("PGAI VOICE BOT -- CALL TRANSCRIPT")
        lines.append("=" * 60)
        lines.append(f"Scenario ID   : {summary.get('scenario_id', 'Unknown')}")
        lines.append(f"Scenario Name : {summary.get('scenario_name', 'Unknown')}")
        lines.append(f"Total Turns   : {summary.get('total_turns', 0)}")
        lines.append(f"Goal Achieved : {summary.get('goal_achieved', False)}")
        lines.append("=" * 60)
        lines.append("")

        for msg in summary.get("transcript", []):
            role    = msg.get("role", "unknown")
            content = msg.get("content", "")

            if role == "assistant":
                speaker = "PATIENT (Bot)"
            elif role == "user":
                speaker = "AGENT (PGAI)"
            else:
                speaker = role.upper()

            lines.append(f"[{speaker}]")
            lines.append(content)
            lines.append("")

        bugs = summary.get("bugs_found", [])
        if bugs:
            lines.append("=" * 60)
            lines.append("BUGS DETECTED DURING THIS CALL:")
            lines.append("=" * 60)
            for i, bug in enumerate(bugs, 1):
                lines.append(f"{i}. {bug}")

        return "\n".join(lines)

    def __repr__(self):
        return f"TranscriptManager(transcripts={self.transcripts_dir})"