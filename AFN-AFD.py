from collections import deque
from graphviz import Digraph


class NFA:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = accepting_states


class DFA:
    def __init__(self, states, alphabet, transitions, start_state, accepting_states):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.start_state = start_state
        self.accepting_states = accepting_states


def e_closure(nfa, states):
    e_closure_set = set(states)
    stack = []
    for state in states:
        stack.append(state)
    while len(stack) != 0:
        current_state = stack.pop()
        if current_state in nfa.transitions and "ε" in nfa.transitions[current_state]:
            for state in nfa.transitions[current_state]["ε"]:
                if state not in e_closure_set:
                    e_closure_set.add(state)
                    stack.append(state)
    return e_closure_set


def move(nfa, states, symbol):
    move_set = set()
    for state in states:
        if state in nfa.transitions and symbol in nfa.transitions[state]:
            for next_state in nfa.transitions[state][symbol]:
                move_set.add(next_state)
    return move_set


def draw_dfa(dfa):
    node_map = {}
    node_id = 0
    g = Digraph("finite_state_machine", filename="dfa.gv")
    g.attr(rankdir="LR", size="8,5")

    for state in dfa.states:
        if state in dfa.accepting_states:
            g.attr("node", shape="doublecircle")
        else:
            g.attr("node", shape="circle")
        node_map[state] = node_id
        g.node(str(node_id))
        node_id += 1

    for state, transitions in dfa.transitions.items():
        for symbol, next_state in transitions.items():
            g.edge(str(node_map[state]), str(node_map[next_state]), label=symbol)

    g.view()


def draw_dfa1(dfa):
    node_map = {}
    g = Digraph("finite_state_machine", filename="dfa.gv")
    g.attr(rankdir="LR", size="8,5")

    for state in sorted(dfa.states):
        if state in dfa.accepting_states:
            g.attr("node", shape="doublecircle")
        else:
            g.attr("node", shape="circle")
        node_map[state] = str(sorted(list(state)))
        g.node(node_map[state])

    for state, transitions in dfa.transitions.items():
        for symbol, next_state in transitions.items():
            g.edge(node_map[state], node_map[next_state], label=symbol)

    g.view()


def nfa_to_dfa(nfa):
    start_state = frozenset(e_closure(nfa, [nfa.start_state]))
    states = set([start_state])
    alphabet = nfa.alphabet
    transitions = {}
    accepting_states = []
    stack = []
    stack.append(start_state)
    while len(stack) != 0:
        current_state = stack.pop()
        for symbol in alphabet:
            next_state = frozenset(e_closure(nfa, move(nfa, current_state, symbol)))
            if len(next_state) == 0:
                continue
            if next_state not in states:
                states.add(next_state)
                stack.append(next_state)
            if current_state not in transitions:
                transitions[current_state] = {}
            transitions[current_state][symbol] = next_state
        if set(nfa.accepting_states).intersection(current_state):
            accepting_states.append(current_state)
    sorted_states = sorted(list(states))  # Sort the states
    dfa = DFA(sorted_states, alphabet, transitions, start_state, accepting_states)
    return dfa


def simulate_nfa(nfa, s):
    current_states = e_closure(nfa, [nfa.start_state])
    for symbol in s:
        current_states = e_closure(nfa, move(nfa, current_states, symbol))
        if not current_states:
            return False
    return bool(set(nfa.accepting_states).intersection(current_states))


def run_dfa(dfa, input_string):
    current_state = dfa.start_state
    for symbol in input_string:
        if symbol not in dfa.alphabet or symbol not in dfa.transitions[current_state]:
            return False
        current_state = dfa.transitions[current_state][symbol]
    return current_state in dfa.accepting_states


# example usage:
nfa = NFA(
    states={"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"},
    alphabet={"a", "b", "c"},
    transitions={
        "0": {"ε": {"1", "5"}},
        "1": {"ε": {"2", "4"}},
        "2": {"a": {"3"}},
        "3": {"ε": {"2", "4"}},
        "4": {"ε": {"9"}},
        "5": {"ε": {"6", "8"}},
        "6": {"b": {"7"}},
        "7": {"ε": {"6", "8"}},
        "8": {"ε": {"9"}},
        "9": {"c": {"10"}},
    },
    start_state="0",
    accepting_states={"10"},
)

dfa = nfa_to_dfa(nfa)

draw_dfa1(dfa)
# draw_dfa(dfa)
# print("DFA states: ", dfa.states)
# print("DFA transitions: ", dfa.transitions)
# print("DFA start state: ", dfa.start_state)
# print("DFA accepting states: ", dfa.accepting_states)

# Simulacion AFN
input_string = "abbbca"
result = simulate_nfa(nfa, input_string)
print("\nSimulacion AFN")
print(f"\nEl input {input_string} {'es' if result else 'no es '}aceptada por el AFN.")

# Simulacion AFD
input_string = "c"
is_accepted = run_dfa(dfa, input_string)
print("\nSimulacion AFD")
print(
    f"\nEl input {input_string} {'es ' if is_accepted else 'no es '}aceptada por el AFD.\n"
)
