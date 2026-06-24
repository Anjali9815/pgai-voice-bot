"""
groq_brain.py - The AI Brain using Groq

OOP Concepts: Class, instance variables, methods, encapsulation
This class handles all Groq API calls and conversation history.
"""

from groq import Groq
from typing import List, Dict
from src.core.config import config
from src.scenarios.scenarios import Scenario


class ConversationMessage:
    """
    Represents a single message in a conversation.
    
    OOP Concept: Simple class with constructor
    """

    def __init__(self, role: str, content: str):
        self.role = role        # "user" or "assistant"
        self.content = content

    def to_dict(self) -> Dict:
        """Convert to dictionary format Groq expects."""
        return {"role": self.role, "content": self.content}

    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"Message(role={self.role}, content='{preview}')"


class GroqBrain:
    """
    OOP Concept: Encapsulation + Abstraction
    
    All Groq logic is hidden inside this class.
    Outside code just calls: brain.respond("agent said hello")
    """

    def __init__(self, scenario: Scenario):
        """
        OOP Concept: Constructor
        Sets up everything this brain needs to work.
        """
        self.scenario = scenario
        self.conversation_history: List[ConversationMessage] = []
        self.bug_reports: List[str] = []
        self.goal_achieved: bool = False
        self.call_complete: bool = False
        self.turn_count: int = 0

        # Initialize Groq client
        self._client = Groq(api_key=config.groq_api_key)
        self._system_prompt = scenario.get_full_system_prompt()

        print(f"[GroqBrain] Initialized for scenario: {scenario.name}")

    def respond(self, agent_said: str) -> str:
        """
        Main method: given what the agent said, return what patient says next.
        
        OOP Concept: Public method -- main interface of this class
        """
        self.turn_count += 1

        # Store what agent said
        self._add_to_history("user", agent_said)

        # Ask Groq what patient should say
        raw_response = self._call_groq()

        # Parse special tags like [BUG_DETECTED]
        clean_response = self._parse_response(raw_response)

        # Store patient response
        self._add_to_history("assistant", clean_response)

        return clean_response

    def get_opening_line(self) -> str:
        """First thing patient says when call connects."""
        opening = self.scenario.opening_line
        self._add_to_history("assistant", opening)
        return opening

    def get_summary(self) -> Dict:
        """Returns full conversation summary for saving."""
        return {
            "scenario_id": self.scenario.id,
            "scenario_name": self.scenario.name,
            "total_turns": self.turn_count,
            "goal_achieved": self.goal_achieved,
            "bugs_found": self.bug_reports,
            "transcript": [m.to_dict() for m in self.conversation_history],
        }

    # -------------------------
    # Private Methods
    # -------------------------

    def _call_groq(self) -> str:
        """
        OOP Concept: Private method
        Handles the actual Groq API call.
        Only GroqBrain uses this internally.
        """
        try:
            messages = [
                {"role": "system", "content": self._system_prompt}
            ] + [m.to_dict() for m in self.conversation_history]

            response = self._client.chat.completions.create(
                model=config.groq_model,
                messages=messages,
                max_tokens=150,      # Keep responses short -- it's a phone call
                temperature=0.7,     # Some creativity but not too random
            )
            return response.choices[0].message.content

        except Exception as e:
            print(f"[GroqBrain] API error: {e}")
            return "I'm sorry, could you repeat that?"

    def _parse_response(self, raw: str) -> str:
        """
        Parses special tags from response.
        
        OOP Concept: Private helper method -- does one specific job
        """
        clean = raw

        if "[GOAL_ACHIEVED]" in clean:
            self.goal_achieved = True
            clean = clean.replace("[GOAL_ACHIEVED]", "").strip()

        if "[CALL_COMPLETE]" in clean:
            self.call_complete = True
            clean = clean.replace("[CALL_COMPLETE]", "").strip()

        if "[BUG_DETECTED:" in clean:
            start = clean.index("[BUG_DETECTED:")
            end = clean.index("]", start)
            bug = clean[start + len("[BUG_DETECTED:"):end].strip()
            self.bug_reports.append(bug)
            print(f"[GroqBrain] BUG DETECTED: {bug}")
            clean = clean[:start] + clean[end + 1:]
            clean = clean.strip()

        return clean

    def _add_to_history(self, role: str, content: str):
        """Adds a message to conversation history."""
        self.conversation_history.append(
            ConversationMessage(role=role, content=content)
        )

    def __repr__(self):
        return (
            f"GroqBrain("
            f"scenario={self.scenario.id}, "
            f"turns={self.turn_count}, "
            f"bugs={len(self.bug_reports)}"
            f")"
        )