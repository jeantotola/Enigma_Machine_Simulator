"""
Technical validation for the Enigma Machine.
Focus: mechanical constraints and signal path.
"""

from enigma_machine import EnigmaMachine, Plugboard, PlugLead, Rotor

def test_low_level_components():
    """Checks individual component logic using index-based encoding."""
    # PlugLead: basic swap
    lead = PlugLead("AB")
    assert lead.encode(0) == 1
    assert lead.encode(1) == 0

    # Plugboard: mapping integrity
    board = Plugboard("AB CD")
    assert board.encode(0) == 1
    assert board.encode(2) == 3
    assert board.encode(25) == 25

    # Rotor: initialization and manual stepping
    rotor = Rotor("I", position="A", ring=1)
    assert rotor.position == 0
    rotor.step()
    assert rotor.position == 1

def test_historical_outputs():
    """Validates the machine against known fixed configurations."""
    # Using M4 setup (4 rotors) to ensure the 4th rotor logic works
    m4 = EnigmaMachine(
        rotor_names="Beta I II III",
        positions="Q E V Z",
        rings="7 11 15 19",
        reflector_name="C"
    )
    assert m4.press_key("Z") == "V"

def test_loopback_integrity():
    """Checks if decryption recovers the original message (reciprocity)."""
    settings = {
        "rotor_names": "I II III",
        "positions": "A B C",
        "rings": "1 1 1",
        "reflector_name": "B",
        "plugboard": "AK BZ"
    }

    text = "ENIGMA"
    ciphertext = EnigmaMachine(**settings).encode_text(text)
    assert EnigmaMachine(**settings).encode_text(ciphertext) == text

def test_security_constraints():
    """Ensures the machine rejects invalid physical assemblies."""
    # Duplicate rotors
    try:
        EnigmaMachine(rotor_names="I I III")
        raise AssertionError("Failed to catch duplicate rotors")
    except ValueError:
        pass

    # Reflector in rotor slot
    try:
        EnigmaMachine(rotor_names="A II III")
        raise AssertionError("Failed to catch reflector in rotor slot")
    except ValueError:
        pass

if __name__ == "__main__":
    test_low_level_components()
    test_historical_outputs()
    test_loopback_integrity()
    test_security_constraints()
    print("All tests passed: Logic, M4 mechanics, and constraints are consistent.")