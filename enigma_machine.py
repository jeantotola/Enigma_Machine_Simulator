LABEL = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

ROTORS_DB = {
"Beta":  {"wiring": "LEYJVCNIXWPBQMDRTAKZGFUHOS", "notch": ""},
"Gamma": {"wiring": "FSOKANUERHMBTIYCWLQPZXVGJD", "notch": ""},
"I":   {"wiring": "EKMFLGDQVZNTOWYHXUSPAIBRCJ", "notch": "Q"},
"II":  {"wiring": "AJDKSIRUXBLHWTMCQGZNPYFVOE", "notch": "E"},
"III": {"wiring": "BDFHJLCPRTXVZNYEIWGAKMUSQO", "notch": "V"},
"IV":  {"wiring": "ESOVPZJAYQUIRHXLNFTGKDCMWB", "notch": "J"},
"V":   {"wiring": "VZBRGITYUPSDNHLXAWMJQOFECK", "notch": "Z"},
"A": {"wiring": "EJMZALYXVBWFCRQUONTSPIKHGD"},
"B": {"wiring": "YRUHQSLDPXNGOKMIEBFZCWVJAT"},
"C": {"wiring": "FVPJIAOYEDRZXWGCTKUQSBNMHL"},
}

def _letter_to_index(letter: str):
    """Converts a character to 0-25 index."""
    return LABEL.find(letter.upper())

def _index_to_letter(index: int):
    """Converts a 0-25 index to a letter."""
    return LABEL[index % 26]

def _parse_sequence(value):
    """Converts various input formats into a list of strings."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, str):
        if value == "":
            return []
        if ',' in value:
            parts = [part.strip() for part in value.split(',')]
        else:
            parts = [part.strip() for part in value.split()]
        return parts

def _parse_rings(value):
    """Converts ring entries into an integer list."""
    parts = _parse_sequence(value)
    return [int(part) for part in parts]


class Rotor:
    """Represents an Enigma rotor with ring and position configurations."""
    def __init__(self, name: str, position: str = 'A', ring: int = 1):
        # validation: check if rotor exists in our database
        if name not in ROTORS_DB:
            raise ValueError(f"Rotor {name} is not a valid rotor name.")

        # validation: ring setting must be between 1 and 26
        if not (1 <= ring <= 26):
            raise ValueError("Ring setting must be between 1 and 26.")

        self.name = name
        data = ROTORS_DB[name]
        self.wiring = data['wiring']
        self.notch = data.get('notch', '')

        # convert initial position (A-Z) and ring (1-26) to 0-25 logic
        self.position = _letter_to_index(position)
        self.ring = ring - 1

        #forward_map: index of wiring letters
        self.forward_map = [_letter_to_index(char) for char in self.wiring]

        #backward_map: reverse look-up (to avoid searching during encryption)
        self.backward_map = [0] * 26
        for i, val in enumerate(self.forward_map):
            self.backward_map[val] = i

    def is_at_notch(self):
        """Checks if the rotor is currently at its notch position."""
        if not self.notch:
            return False
        return _index_to_letter(self.position) == self.notch

    def step(self, steps: int = 1):
        """Advances rotor by one step."""
        self.position = (self.position + steps) % 26

    def _encode(self, index:int, mapping):
        """
        Internal signal processing logic. Calculates the offset between the rotor's
        internal wiring, its current position, and the ring setting.
        """
        # total shift is position minus ring setting
        shift = self.position - self.ring

        # enters the rotor: adjusts index by shift
        index = (index + shift) % 26

        # passes through internal wiring
        index = mapping[index]

        # exits the rotor: reverses the shift
        return (index - shift) % 26

    def encode_forward(self, index):
        """Signal path: Right to Left."""
        return self._encode(index, self.forward_map)

    def encode_backward(self, index):
        """Signal path: Left to Right."""
        return self._encode(index, self.backward_map)

    def __str__(self):
        """Returns the rotor name instead of object representation."""
        return self.name

class PlugLead:
    """Represents a physical cable connecting two letters on the plugboard."""
    def __init__(self, pair: str):
        if len(pair) != 2 or pair[0] == pair[1]:
            raise ValueError("PlugLead requires 2 different letters.")
        self.pair = pair.upper()
        self.first = _letter_to_index(pair[0])
        self.second = _letter_to_index(pair[1])

    def encode(self, index):
        """If the signal hits one end of the lead, it exits through the other."""
        if index == self.first:
            return self.second
        elif index == self.second:
            return self.first
        return index

class Plugboard:
    """Manages a collection of PlugLeads. """
    MAX_LEADS = 10

    def __init__(self, leads = None):
        self.leads = []
        self._map = {}

        if leads:
            for pair in leads.upper().split():
                self.add(pair)

    def add(self, lead_or_pair):
        """Inserts a lead, checking for capacity and occupied plugs."""
        if isinstance(lead_or_pair, str):
            lead = PlugLead(lead_or_pair)
        else:
            lead = lead_or_pair

        # check capacity
        if len(self.leads) >= self.MAX_LEADS:
            raise ValueError("Plugboard has reached 10-plug capacity.")

        # check if plugs are free (using the set 'pair' from PlugLead)
        for letter in lead.pair:
            if letter in self._map:
                raise ValueError(f"Plug '{letter}' is already occupied.")

        # update internal state
        self.leads.append(lead)

        # update the letter map
        chars = list(lead.pair)
        self._map[chars[0]] = chars[1]
        self._map[chars[1]] = chars[0]

    def encode(self, index: int):
        """Passes the signal through every lead installed."""
        for lead in self.leads:
            new_index = lead.encode(index)
            # if the index changed, it means it hit a lead and was swapped
            if new_index != index:
                return new_index
        return index

    def __str__(self):
        if not self.leads:
            return "no plugs connected in the board."
        # sorting for clean output
        pairs = ["".join(sorted(list(l.pair))) for l in self.leads]
        return " ".join(sorted(pairs))

class Reflector:
    """Simulates the Enigma's reflector"""
    def __init__(self, name: str):
        data = ROTORS_DB[name]
        self.wiring = data['wiring']
        # mapping input and output indices
        self.mapping = [_letter_to_index(char) for char in self.wiring]

    def reflect(self, index):
        """Returns the reflected index."""
        return self.mapping[index]

class EnigmaMachine:
    """Assembly of all parts: Rotors, Reflector, and Plugboard."""
    def __init__ (self, rotor_names, positions = ("A", "A", "A"), rings = (1, 1, 1), reflector_name: str = 'B', plugboard = None):
        rotor_names = _parse_sequence(rotor_names)
        positions = _parse_sequence(positions)
        rings = _parse_rings(rings)

        # basic validations
        if not 3 <= len(rotor_names) <= 4:
            raise ValueError("Please make sure to insert exactly three or four rotors in the machine.")


        if positions and len(positions) != len(rotor_names):
            raise ValueError("Each rotor must be in a single position.")

        if rings and len(rings) != len(rotor_names):
            raise ValueError("Each rotor must have a single ring configuration.")

        # historical M4 validations:
        # 1. fourth rotor (leftmost) must be "thin" (Beta or Gamma)
        if len(rotor_names) == 4 and rotor_names[0] not in ["Beta", "Gamma"]:
                raise ValueError(
                    f"In a 4-rotor setup, the leftmost rotor must be Beta or Gamma. {rotor_names[0]} is not allowed.")

        # 2. Beta and Gamma can't be in the standard moving slots (the last 3 slots).
        standard_slots = rotor_names[1:] if len(rotor_names) == 4 else rotor_names
        for name in standard_slots:
            if name in ["Beta", "Gamma"]:
                raise ValueError(
                    f"Rotor {name} is a 'thin' rotor and can only be placed in the fourth (leftmost) position.")

        # validation: no reflector is installed in the rotors' slots (A, B, C are reflectors)
        for rotor_name in rotor_names:
            if rotor_name in ['A', 'B', 'C']:
                raise ValueError(f"Can't install reflector {rotor_name} in a rotor slot.")

        # validation: no rotor is installed in the reflector's slot
        if reflector_name not in ['A', 'B', 'C']:
            raise ValueError(f"Can't install {reflector_name} in the reflector's slot.")

        # validation: no duplicate rotors
        if len(rotor_names) != len(set(rotor_names)):
            raise ValueError("Can't install the same rotor twice.")

        # installing components
        self._rotors = list()

        for i in range(len(rotor_names)):
            position = positions[i] if positions else 'A'
            ring = rings[i] if rings else 1
            self._rotors.append(Rotor(rotor_names[i], position, ring))

        self._reflector = Reflector(reflector_name)

        self._plugboard = plugboard if isinstance(plugboard, Plugboard) else Plugboard(plugboard)

    def _step(self):
        """
        Rightmost rotor always steps.
        If a rotor is at its notch, the one to its left will step
        """
        num_rotors = len(self._rotors)

        # determines which rotors can step (in 4-rotor machines, the first one never steps):
        left_moving = 1 if num_rotors == 4 else 0
        middle_moving = left_moving + 1

        # we save the state BEFORE stepping, thus preventing checking if a rotor
        # is at its' notch AFTER it has already moved.
        middle_at_notch = self._rotors[middle_moving].is_at_notch()
        right_at_notch = self._rotors[-1].is_at_notch()

        # if the middle rotor triggers the step, there will be a double-step and
        # ALL the rotors will step (rightmost will be solved separately).
        if middle_at_notch:
            self._rotors[left_moving].step()
            self._rotors[middle_moving].step()

        # normal stepping: middle steps, left doesn't.
        if right_at_notch and not middle_at_notch:
            self._rotors[middle_moving].step()

        # in any case, rightmost one will step.
        self._rotors[-1].step()

    def press_key(self, letter: str):
        """Processes a single character through the full signal path."""
        if not isinstance(letter, str) or not letter.isalpha():
            raise TypeError("Press_key expects a single character.")

        letter = letter.upper()

        # upon pressing the key, rotor steps.
        self._step()

        # going through the plugboard:
        index = _letter_to_index(letter)
        index = self._plugboard.encode(index)

        # going forward through rotors:
        for rotor in reversed(self._rotors):
            index = rotor.encode_forward(index)

        # going through the reflector:
        index = self._reflector.reflect(index)

        # coming back through rotors:
        for rotor in self._rotors:
            index = rotor.encode_backward(index)

        # back to plugboard:
        index = self._plugboard.encode(index)

        # and generating the output
        return _index_to_letter(index)

    def encode_text(self, text: str):
        """Encrypts or decrypts a full block of text."""
        return "".join([self.press_key(char) if char.isalpha() else char for char in text])