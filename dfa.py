import re
from collections import defaultdict


def regex_to_dfa(regex):
    alphabet = set(re.findall(r"[a-zA-Z0-9]", regex))
    regex = f"({regex}#)"
    substrings = sorted(
        {regex[:i] for i in range(1, len(regex) + 1)}, key=len, reverse=True
    )

    states = [s for s in substrings]
    state_transitions = defaultdict(dict)

    def find_next_state(state, symbol):
        for s in substrings:
            if state + symbol == s[-len(state) - 1 :]:
                return s
        return None

    for state in states:
        for symbol in alphabet:
            next_state_name = find_next_state(state, symbol)
            if next_state_name is not None:
                state_transitions[state][symbol] = next_state_name

    return states, alphabet, state_transitions


def simulate_dfa(states, alphabet, state_transitions, start_state, input_string):
    current_state = start_state

    for symbol in input_string:
        if symbol not in alphabet:
            return False
        current_state = state_transitions[current_state].get(symbol)
        if current_state is None:
            return False

    return "#" in current_state


def print_dfa(states, alphabet, state_transitions):
    print("States:")
    for state in states:
        print(state)
    print("\nAlphabet:")
    for symbol in alphabet:
        print(symbol)
    print("\nState Transitions:")
    for state, transitions in state_transitions.items():
        for symbol, next_state in transitions.items():
            print(f"{state} --{symbol}--> {next_state}")


# Define your regex and input string here
regex = "(a*|b*)c"
input_string = "aaac"

states, alphabet, state_transitions = regex_to_dfa(regex)
start_state = states[-1]

print_dfa(states, alphabet, state_transitions)

result = simulate_dfa(states, alphabet, state_transitions, start_state, input_string)
print("\nInput accepted" if result else "Input rejected")
