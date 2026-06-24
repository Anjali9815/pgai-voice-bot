"""
scenarios.py - Patient Scenarios

OOP Concepts: Dataclasses, Enums, Static Methods
Each scenario is an OBJECT with its own data and behavior.

Think of scenarios like test cases:
- Each one has a different patient persona
- Each one has a specific goal
- Each one tests a different part of the PGAI agent
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


# ─────────────────────────────────────────────
# ENUMS
# ─────────────────────────────────────────────

class ScenarioType(Enum):
    """
    OOP Concept: Enum
    Instead of using plain strings like "scheduling"
    we use ScenarioType.SCHEDULING
    
    Benefits:
    - No typos possible
    - Autocomplete in VS Code
    - Clear and readable
    """
    SCHEDULING        = "scheduling"
    RESCHEDULING      = "rescheduling"
    CANCELLATION      = "cancellation"
    MEDICATION_REFILL = "medication_refill"
    OFFICE_INFO       = "office_info"
    INSURANCE         = "insurance"
    EDGE_CASE         = "edge_case"


class Severity(Enum):
    """How bad is it if the agent fails this scenario."""
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


# ─────────────────────────────────────────────
# DATACLASSES
# ─────────────────────────────────────────────

@dataclass
class PatientPersona:
    """
    OOP Concept: Dataclass
    A class that mainly holds data.
    @dataclass automatically creates __init__ for us.
    
    Without @dataclass you would write:
        def __init__(self, name, age, condition...):
            self.name = name
            self.age = age
            ...
    
    With @dataclass Python does that automatically!
    """
    name: str
    age: int
    condition: str
    personality: str
    insurance: str = "BlueCross"
    doctor: str = "Dr. Smith"


@dataclass
class Scenario:
    """
    OOP Concept: Composition
    Scenario HAS a PatientPersona inside it.
    
    "Has-a" relationship:
    - A Scenario HAS a PatientPersona
    - This is Composition
    
    vs "Is-a" relationship (Inheritance):
    - A Dog IS AN Animal
    """
    id: str
    name: str
    scenario_type: ScenarioType
    persona: PatientPersona
    goal: str
    system_prompt: str
    opening_line: str
    success_criteria: List[str]
    edge_triggers: List[str] = field(default_factory=list)
    severity_if_fails: Severity = Severity.MEDIUM

    def get_full_system_prompt(self) -> str:
        """
        OOP Concept: Instance method
        Uses self to build a complete prompt
        specific to THIS scenario's persona.
        """
        return f"""
You are {self.persona.name}, a {self.persona.age}-year-old patient calling a medical office.

PERSONALITY: {self.persona.personality}
CONDITION: {self.persona.condition}
INSURANCE: {self.persona.insurance}
YOUR DOCTOR: {self.persona.doctor}

YOUR GOAL: {self.goal}

SPECIFIC INSTRUCTIONS:
{self.system_prompt}

CONVERSATION RULES:
- Speak naturally like a real patient on the phone
- Keep responses SHORT -- 1 to 3 sentences max
- This is a phone call, not a chat
- If the agent asks for info, provide it naturally
- If you achieve your goal, wrap up the call politely
- Do NOT break character ever
- Do NOT say you are an AI or a bot

SPECIAL TAGS TO USE:
- Add [GOAL_ACHIEVED] when you got what you needed
- Add [CALL_COMPLETE] when ready to hang up
- Add [BUG_DETECTED: description] if agent says something wrong
"""

    def __repr__(self):
        return f"Scenario(id={self.id}, type={self.scenario_type.value})"


# ─────────────────────────────────────────────
# SCENARIO LIBRARY
# ─────────────────────────────────────────────

class ScenarioLibrary:
    """
    OOP Concept: Static Methods + Repository Pattern
    
    This class is a LIBRARY of all test scenarios.
    Static methods mean you don't need to create an object:
    
    Normal method:   lib = ScenarioLibrary(); lib.get_all()
    Static method:   ScenarioLibrary.get_all()
    
    Use static when the method doesn't need self (no instance data needed).
    """

    @staticmethod
    def get_all() -> List[Scenario]:
        """Returns all available test scenarios."""
        return [
            ScenarioLibrary._simple_scheduling(),
            ScenarioLibrary._reschedule_appointment(),
            ScenarioLibrary._cancel_appointment(),
            ScenarioLibrary._medication_refill(),
            ScenarioLibrary._office_hours_inquiry(),
            ScenarioLibrary._insurance_question(),
            ScenarioLibrary._weekend_edge_case(),
            ScenarioLibrary._confused_patient(),
            ScenarioLibrary._urgent_same_day(),
            ScenarioLibrary._new_patient(),
        ]

    @staticmethod
    def get_by_id(scenario_id: str) -> Scenario:
        """Fetch a specific scenario by its ID."""
        scenarios = {s.id: s for s in ScenarioLibrary.get_all()}
        if scenario_id not in scenarios:
            raise ValueError(f"Scenario '{scenario_id}' not found.")
        return scenarios[scenario_id]

    @staticmethod
    def get_by_type(scenario_type: ScenarioType) -> List[Scenario]:
        """Fetch all scenarios of a specific type."""
        return [
            s for s in ScenarioLibrary.get_all()
            if s.scenario_type == scenario_type
        ]

    # ─────────────────────────────────────────
    # Private scenario definitions
    # ─────────────────────────────────────────

    @staticmethod
    def _simple_scheduling() -> Scenario:
        return Scenario(
            id="SCN001",
            name="Simple Appointment Scheduling",
            scenario_type=ScenarioType.SCHEDULING,
            persona=PatientPersona(
                name="Sarah Johnson",
                age=34,
                condition="Annual checkup",
                personality="Friendly and straightforward",
            ),
            goal="Schedule a general checkup appointment next week",
            system_prompt="""
- You want a morning appointment if possible
- You are available Monday through Wednesday
- This is a routine annual checkup, nothing urgent
""",
            opening_line="Hi, I'd like to schedule an appointment for a general checkup.",
            success_criteria=[
                "Agent asks for your name",
                "Agent asks for preferred date and time",
                "Agent confirms the appointment",
            ],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _reschedule_appointment() -> Scenario:
        return Scenario(
            id="SCN002",
            name="Reschedule Existing Appointment",
            scenario_type=ScenarioType.RESCHEDULING,
            persona=PatientPersona(
                name="Michael Torres",
                age=45,
                condition="Follow-up visit",
                personality="Slightly impatient, busy professional",
            ),
            goal="Reschedule tomorrow's 2pm appointment to next Friday",
            system_prompt="""
- You have an existing appointment tomorrow at 2pm
- Something came up at work, you need to move it
- You prefer afternoon slots
- You are a bit rushed on the phone
""",
            opening_line="Hi, I need to reschedule my appointment that's tomorrow at 2pm.",
            success_criteria=[
                "Agent looks up existing appointment",
                "Agent offers alternative slots",
                "Agent confirms new date and time",
            ],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _cancel_appointment() -> Scenario:
        return Scenario(
            id="SCN003",
            name="Cancel Appointment",
            scenario_type=ScenarioType.CANCELLATION,
            persona=PatientPersona(
                name="Linda Park",
                age=62,
                condition="Routine visit",
                personality="Polite and apologetic",
            ),
            goal="Cancel upcoming appointment and ask about cancellation policy",
            system_prompt="""
- You need to cancel your appointment for next Monday
- You feel bad about cancelling
- Ask if there is a cancellation fee
- Ask if you need to reschedule right now
""",
            opening_line="Hello, I'm sorry to bother you but I need to cancel my appointment for next Monday.",
            success_criteria=[
                "Agent cancels the appointment",
                "Agent explains cancellation policy",
                "Agent offers to reschedule",
            ],
            severity_if_fails=Severity.MEDIUM,
        )

    @staticmethod
    def _medication_refill() -> Scenario:
        return Scenario(
            id="SCN004",
            name="Medication Refill Request",
            scenario_type=ScenarioType.MEDICATION_REFILL,
            persona=PatientPersona(
                name="Robert Chen",
                age=58,
                condition="Hypertension on lisinopril",
                personality="Matter of fact, knows his medication well",
            ),
            goal="Request a refill for lisinopril 10mg",
            system_prompt="""
- You take lisinopril 10mg daily for blood pressure
- Your prescription runs out in 3 days
- Your pharmacy is Walgreens on Main Street
- Ask how long the refill will take
""",
            opening_line="Hi, I need to request a refill for my blood pressure medication, lisinopril 10mg.",
            success_criteria=[
                "Agent takes medication name and dosage",
                "Agent asks for pharmacy info",
                "Agent gives timeline for refill",
            ],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _office_hours_inquiry() -> Scenario:
        return Scenario(
            id="SCN005",
            name="Office Hours and Location",
            scenario_type=ScenarioType.OFFICE_INFO,
            persona=PatientPersona(
                name="Amy Williams",
                age=29,
                condition="New patient inquiring",
                personality="Curious, asks multiple questions",
            ),
            goal="Find out office hours, location, and parking",
            system_prompt="""
- You are new to the area
- Ask about weekday AND weekend hours specifically
- Ask about the address
- Ask about parking availability
""",
            opening_line="Hi, I'm new to the area and thinking about becoming a patient. Can you tell me about your office hours?",
            success_criteria=[
                "Agent provides weekday hours",
                "Agent clarifies weekend availability",
                "Agent provides address",
            ],
            severity_if_fails=Severity.MEDIUM,
        )

    @staticmethod
    def _insurance_question() -> Scenario:
        return Scenario(
            id="SCN006",
            name="Insurance Acceptance Question",
            scenario_type=ScenarioType.INSURANCE,
            persona=PatientPersona(
                name="James Davis",
                age=41,
                condition="Looking for new primary care",
                personality="Careful and detail oriented",
                insurance="Aetna PPO",
            ),
            goal="Confirm if the practice accepts Aetna PPO insurance",
            system_prompt="""
- You have Aetna PPO insurance through your employer
- Ask specifically about Aetna PPO
- Ask if there is a copay for new patient visits
""",
            opening_line="Hi, I'd like to know if you accept Aetna PPO insurance before I schedule anything.",
            success_criteria=[
                "Agent confirms or denies Aetna PPO",
                "Agent provides copay information",
            ],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _weekend_edge_case() -> Scenario:
        """
        KEY edge case from the challenge brief.
        Agent should NOT book Sunday appointments.
        """
        return Scenario(
            id="SCN007",
            name="Weekend Appointment Edge Case",
            scenario_type=ScenarioType.EDGE_CASE,
            persona=PatientPersona(
                name="Kevin Murphy",
                age=37,
                condition="Minor illness",
                personality="Busy, prefers weekends",
            ),
            goal="Try to book Sunday appointment to test if agent catches the error",
            system_prompt="""
- You specifically ask for Sunday at 10am
- If agent tries to book it, that is a BUG -- add [BUG_DETECTED: Agent booked Sunday appointment when office should be closed]
- If agent says closed on Sunday, ask about Saturday instead
""",
            opening_line="Hi, can I get an appointment for this Sunday at 10am?",
            success_criteria=[
                "Agent says office is closed on Sunday",
                "Agent offers next available weekday",
            ],
            edge_triggers=["What about Saturday?", "Are you sure you're closed Sunday?"],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _confused_patient() -> Scenario:
        return Scenario(
            id="SCN008",
            name="Confused Elderly Patient",
            scenario_type=ScenarioType.EDGE_CASE,
            persona=PatientPersona(
                name="Dorothy Hayes",
                age=78,
                condition="Various age related issues",
                personality="Elderly, sometimes confused, repeats herself",
            ),
            goal="Test how agent handles unclear and repetitive speech",
            system_prompt="""
- You are elderly and a bit confused
- Change topic mid sentence sometimes
- Repeat your name twice when asked
- Ask the same question twice in a row
- Use um and uh naturally
- Trail off mid sentence sometimes
""",
            opening_line="Hello? Yes hi, I'm calling about... um, I need to make an appointment, or maybe it was... who am I speaking with?",
            success_criteria=[
                "Agent remains patient",
                "Agent gently clarifies without being rude",
                "Agent successfully captures needed info",
            ],
            severity_if_fails=Severity.MEDIUM,
        )

    @staticmethod
    def _urgent_same_day() -> Scenario:
        return Scenario(
            id="SCN009",
            name="Urgent Same Day Appointment",
            scenario_type=ScenarioType.SCHEDULING,
            persona=PatientPersona(
                name="Tom Bradley",
                age=52,
                condition="Chest discomfort",
                personality="Anxious and urgent",
            ),
            goal="Request urgent same day appointment for chest discomfort",
            system_prompt="""
- You have mild chest discomfort since this morning
- You want to be seen TODAY if possible
- If they cannot see you today, ask what you should do
- Note if agent appropriately handles urgent medical situation
""",
            opening_line="Hi, I've been having some chest discomfort since this morning and I was hoping to get seen today if possible.",
            success_criteria=[
                "Agent takes urgency seriously",
                "Agent offers same day slot or advises appropriately",
                "Agent asks about symptom severity",
            ],
            severity_if_fails=Severity.HIGH,
        )

    @staticmethod
    def _new_patient() -> Scenario:
        return Scenario(
            id="SCN010",
            name="New Patient Registration",
            scenario_type=ScenarioType.SCHEDULING,
            persona=PatientPersona(
                name="Priya Patel",
                age=31,
                condition="New patient general wellness",
                personality="Organized, has questions ready",
                insurance="United Healthcare",
            ),
            goal="Register as new patient and schedule first appointment",
            system_prompt="""
- You just moved to the area
- You have United Healthcare insurance
- Ask what documents to bring for first visit
- Ask if new patient forms can be filled out online
""",
            opening_line="Hi, I'd like to become a new patient and schedule my first appointment.",
            success_criteria=[
                "Agent walks through new patient process",
                "Agent schedules appointment",
                "Agent provides intake instructions",
            ],
            severity_if_fails=Severity.MEDIUM,
        )