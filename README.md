# Enigma Machine Simulation

This project is a Python implementation of the Enigma Machine, developed as a final project for the discipline **Programming for Artificial Intelligence**, within the **MSc in Artificial Intelligence** at the **University of Bath**. 

It simulates the M3 and M4 models, bridging historical cryptography with modern programming.
## Overview

The primary goal was to create a simulator that reflects the original hardware. This project replicates the exact electrical signal path:
Plugboard → Rotors (Forward) → Reflector → Rotors (Backward) → Plugboard.

### Core Components
- **EnigmaMachine**: The central unit. Manages the hardware assembly and the stepping logic.
- **Rotor**: Simulates individual rotors, including ring settings and initial position.
- **Plugboard**: Replicates the manual system with its' 10-lead capacity limit.
- **Reflector**: Allows for the system's reciprocal nature, so that the same settings can encrypt and decrypt.

### Features
Efficiency was a key consideration in the development process:
- **Index-Based Processing**: The machine processes integer indices (0-25) rather than string manipulations.
- **Mapping**: The "backward" path through the rotors is pre-calculated during initialization. This eliminates expensive search operations during the encryption of long texts.
- **Double-stepping**: It implements the specific mechanical feature of the Enigma, where the middle rotor can advance twice in a single cycle.
- **The M4 "Thin" Architecture**: The simulator handles the 4-rotor Naval variant. In this mode, only three rotors were part of the active mechanism.
- **Physical Validation**: The system prevents impossible configurations, such as placing a reflector in a rotor slot or using "thin" rotors in the standard rotors positions.

## Usage

To operate the machine, instantiate the `EnigmaMachine` class with your desired hardware setup:

```python
from enigma_machine import EnigmaMachine

# Configure the machine: Rotors, Start Positions, Ring Settings, Reflector, Plugboard
machine = EnigmaMachine(
    rotor_names="I II III",
    positions="A B C",
    rings="1 1 1",
    reflector_name="B",
    plugboard="AK BZ"
)

message = "SECRET MESSAGE"
cipher = machine.encode_text(message)
print(f"Result: {cipher}")