"""
run_local.py - Entry Point for Mode 1

This is the file you actually RUN.
It's kept simple on purpose -- just picks a scenario and starts.

To run:
    python run_local.py
"""

from src.scenarios.scenarios import ScenarioLibrary
from src.modes.local_mode import LocalMode


def main():
    print("\n" + "=" * 60)
    print("PGAI VOICE BOT -- LOCAL TEST MODE")
    print("=" * 60)

    # Show all available scenarios
    scenarios = ScenarioLibrary.get_all()
    print("\nAvailable Scenarios:\n")
    for i, scenario in enumerate(scenarios, 1):
        print(f"  {i:2}. [{scenario.id}] {scenario.name}")

    print("\n" + "=" * 60)

    # Ask user to pick one
    while True:
        try:
            choice = input("\nPick a scenario number (1-10): ").strip()
            index  = int(choice) - 1
            if 0 <= index < len(scenarios):
                selected = scenarios[index]
                break
            else:
                print("Please enter a number between 1 and 10")
        except ValueError:
            print("Please enter a valid number")

    print(f"\nSelected: {selected.name}")
    print(f"Patient : {selected.persona.name}, age {selected.persona.age}")
    print(f"Goal    : {selected.goal}")

    # Ask input mode
    print("\nInput Mode:")
    print("  1. Keyboard -- you type what the agent says")
    print("  2. Microphone -- you speak what the agent says")

    mic_choice = input("\nPick input mode (1 or 2): ").strip()
    use_mic    = mic_choice == "2"

    # Start the conversation
    mode = LocalMode(scenario=selected, use_mic=use_mic)
    mode.run()


if __name__ == "__main__":
    main()