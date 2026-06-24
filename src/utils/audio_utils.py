"""
audio_utils.py - Text to Speech and Speech to Text

OOP Concepts: Abstract Base Class, Inheritance, Polymorphism

Abstract Base Class = a BLUEPRINT that other classes must follow
Inheritance = child class GETS everything from parent class
Polymorphism = same method name, different behavior per class

Real world analogy:
- ABC says "every vehicle must have a drive() method"
- Car implements drive() one way
- Boat implements drive() differently
- But both are called the same: vehicle.drive()
"""

import os
import tempfile
from abc import ABC, abstractmethod
import pyttsx3
import speech_recognition as sr


# ─────────────────────────────────────────────
# ABSTRACT BASE CLASS
# ─────────────────────────────────────────────

class TextToSpeechBase(ABC):
    """
    OOP Concept: Abstract Base Class

    You CANNOT create this directly:
        tts = TextToSpeechBase()  # ERROR!

    You CAN create its children:
        tts = LocalTTS()          # WORKS!

    Forces ALL child classes to implement speak() and is_available()
    Guarantees consistent interface no matter which TTS we use.
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """Every child class MUST implement this."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Every child class MUST implement this."""
        pass


# ─────────────────────────────────────────────
# CHILD CLASS 1: Local Speaker
# ─────────────────────────────────────────────

class LocalTTS(TextToSpeechBase):
    """
    OOP Concept: Inheritance
    LocalTTS INHERITS from TextToSpeechBase.

    What it inherits:
    - The requirement to implement speak()
    - The requirement to implement is_available()

    What it adds:
    - Its own __init__ with pyttsx3 engine
    - Its own _init_engine() private method
    """

    def __init__(self):
        """
        OOP Concept: super().__init__()
        Calls the parent class constructor first.
        Good practice even if parent has no logic.
        """
        super().__init__()
        self._engine      = None
        self._initialized = False
        self._init_engine()

    def _init_engine(self):
        """Private method -- sets up pyttsx3."""
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 160)   # speaking speed
            self._engine.setProperty("volume", 0.9) # volume 0 to 1
            self._initialized = True
            print("[LocalTTS] Engine ready")
        except Exception as e:
            print(f"[LocalTTS] Warning: {e}")
            print("[LocalTTS] Will print text instead of speaking")
            self._initialized = False

    def speak(self, text: str) -> None:
        """
        OOP Concept: Implementing abstract method
        This is the CONCRETE version of the abstract speak().
        """
        print(f"\n[BOT SPEAKS]: {text}\n")

        if self._initialized and self._engine:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                print(f"[LocalTTS] Speech error: {e}")

    def is_available(self) -> bool:
        return self._initialized

    def __repr__(self):
        return f"LocalTTS(initialized={self._initialized})"


# ─────────────────────────────────────────────
# SPEECH TO TEXT
# ─────────────────────────────────────────────

class SpeechToText:
    """
    OOP Concept: Composition
    This class HAS A Recognizer object inside it.

    Composition = "has-a" relationship
    Inheritance = "is-a" relationship

    SpeechToText HAS A Recognizer (composition)
    LocalTTS IS A TextToSpeechBase (inheritance)
    """

    def __init__(self):
        self._recognizer  = sr.Recognizer()
        self._microphone  = None
        self._setup_microphone()

    def _setup_microphone(self):
        """Sets up mic and adjusts for background noise."""
        try:
            self._microphone = sr.Microphone()
            with self._microphone as source:
                print("[SpeechToText] Adjusting for background noise...")
                self._recognizer.adjust_for_ambient_noise(source, duration=1)
            print("[SpeechToText] Microphone ready")
        except Exception as e:
            print(f"[SpeechToText] Mic setup error: {e}")
            print("[SpeechToText] Switching to keyboard input mode")
            self._microphone = None

    def listen(self, timeout: int = 10) -> str:
        """
        Listens to mic and returns transcribed text.
        Falls back to keyboard input if no mic available.
        """
        if not self._microphone:
            return input("[YOU TYPE]: ").strip()

        print("[Listening... speak now]")
        failed_attempts = 0

        while failed_attempts < 2:
            print("[Listening... speak now]")
            try:
                with self._microphone as source:
                    audio = self._recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=30
                    )
                print("[Processing...]")
                text = self._recognizer.recognize_google(audio)
                print(f"\n[YOU SAID]: {text}\n")
                return text

            except sr.WaitTimeoutError:
                print("[SpeechToText] No speech detected")
                return ""

    def is_available(self) -> bool:
        return self._microphone is not None

    def __repr__(self):
        return f"SpeechToText(mic={self.is_available()})"


# ─────────────────────────────────────────────
# FACTORY FUNCTION
# ─────────────────────────────────────────────

def get_tts_engine() -> TextToSpeechBase:
    """
    OOP Concept: Factory Function

    Decides WHICH TTS class to create and returns it.
    Caller doesn't need to know which one -- just calls .speak()

    This is the Factory Pattern:
    A function that creates and returns objects.
    Hides the creation complexity from the caller.
    """
    engine = LocalTTS()
    if engine.is_available():
        print("[AudioUtils] Using LocalTTS")
        return engine

    print("[AudioUtils] No TTS engine available -- text only mode")
    return engine