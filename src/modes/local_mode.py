"""
local_mode.py - Mode 1: Local Conversation

OOP Concept: Orchestrator Class
This class COORDINATES all other classes together.
It doesn't do the work itself -- it delegates to:
- GroqBrain    (thinking)
- LocalTTS     (speaking)
- SpeechToText (listening)
- TranscriptManager (saving)

Real world analogy:
A conductor doesn't play instruments.
They coordinate musicians who do the actual playing.
"""

from src.core.groq_brain import GroqBrain
from src.scenarios.scenarios import ScenarioLibrary, Scenario
from src.utils.audio_utils import LocalTTS, SpeechToText, get_tts_engine
from src.utils.transcript_manager import TranscriptManager


class LocalMode:
    """
    OOP Concept: Orchestrator / Coordinator class

    Has-a relationships (Composition):
    - LocalMode HAS A GroqBrain
    - LocalMode HAS A LocalTTS
    - LocalMode HAS A SpeechToText
    - LocalMode HAS A TranscriptManager

    None of these do anything until LocalMode coordinates them.
    """

    def __init__(self, scenario: Scenario, use_mic: bool = False):
        """
        Args:
            scenario:  which patient scenario to run
            use_mic:   True = speak into mic
                       False = type your responses (easier for testing)
        """
        self.scenario    = scenario
        self.use_mic     = use_mic
        self.call_id     = f"local_{scenario.id}"

        # Initialize all components
        self._brain      = GroqBrain(scenario)
        self._tts        = get_tts_engine()
        self._stt        = SpeechToText() if use_mic else None
        self._transcript = TranscriptManager()

        print(f"\n[LocalMode] Ready")
        print(f"[LocalMode] Scenario : {scenario.name}")
        print(f"[LocalMode] Input    : {'Microphone' if use_mic else 'Keyboard'}")
        print(f"[LocalMode] Patient  : {scenario.persona.name}")

    def run(self):
        """
        Main method -- runs the full conversation loop.

        OOP Concept: Public method as entry point
        One method starts everything. Clean and simple.
        """
        self._print_header()

        # Step 1: Patient says opening line
        opening = self._brain.get_opening_line()
        self._tts.speak(opening)

        # Step 2: Conversation loop
        while not self._should_end():
            # Get input (mic or keyboard)
            agent_response = self._get_input()

            if not agent_response:
                continue

            if agent_response.lower() in ["quit", "exit", "q"]:
                print("\n[LocalMode] Ending conversation...")
                break

            # Brain generates patient response
            patient_response = self._brain.respond(agent_response)

            # Speak it out
            self._tts.speak(patient_response)

            # Show turn count
            print(f"[Turn {self._brain.turn_count}]")

        # Step 3: Save everything
        self._save_results()
        self._print_summary()

    # ─────────────────────────────────────────
    # Private Methods
    # ─────────────────────────────────────────

    def _get_input(self) -> str:
        """
        Gets agent response either from mic or keyboard.

        OOP Concept: Private method that handles input source switching.
        The run() loop doesn't care HOW we get input -- just that we do.
        """
        if self.use_mic and self._stt:
            print("\n[Waiting for agent response -- speak or type]")
            return self._stt.listen()
        else:
            return input("\n[AGENT RESPONSE -- type what agent said]: ").strip()

    def _should_end(self) -> bool:
        """Check if conversation should end."""
        return self._brain.call_complete or self._brain.turn_count >= 15

    def _save_results(self):
        """Saves transcript and bug report."""
        summary = self._brain.get_summary()
        self._transcript.save_transcript(summary, self.call_id)
        self._transcript.save_json(summary, self.call_id)
        self._transcript.save_bug_report(
            summary["bugs_found"],
            self.scenario.name,
            self.call_id
        )

    def _print_header(self):
        print("\n" + "=" * 60)
        print("PGAI VOICE BOT -- LOCAL MODE")
        print("=" * 60)
        print(f"Scenario : {self.scenario.name}")
        print(f"Patient  : {self.scenario.persona.name}, {self.scenario.persona.age}")
        print(f"Goal     : {self.scenario.goal}")
        print("=" * 60)
        print("Type what the PGAI agent says after the bot speaks.")
        print("Type 'quit' to end the conversation.")
        print("=" * 60 + "\n")

    def _print_summary(self):
        summary = self._brain.get_summary()
        print("\n" + "=" * 60)
        print("CONVERSATION COMPLETE")
        print("=" * 60)
        print(f"Total Turns   : {summary['total_turns']}")
        print(f"Goal Achieved : {summary['goal_achieved']}")
        print(f"Bugs Found    : {len(summary['bugs_found'])}")
        if summary['bugs_found']:
            print("\nBugs:")
            for bug in summary['bugs_found']:
                print(f"  - {bug}")
        print("=" * 60)

    def __repr__(self):
        return f"LocalMode(scenario={self.scenario.id}, mic={self.use_mic})"