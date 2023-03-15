from collections import deque, OrderedDict
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
    g = Digraph("finite_state_machine", filename="dfa1.gv")
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
    states = [start_state]  # Use a list to maintain state order
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
                states.append(next_state)  # Append new states to end of list
                stack.append(next_state)
            if current_state not in transitions:
                transitions[current_state] = {}
            transitions[current_state][symbol] = next_state
        if set(nfa.accepting_states).intersection(current_state):
            accepting_states.append(current_state)
    dfa = DFA(states, alphabet, transitions, start_state, accepting_states)
    return dfa


def print_dfa(dfa):
    # Print header row
    print("DFA STATE\tTYPE\ta\tb")
    # Loop through states
    for i, state in enumerate(dfa.states):
        # Determine state type (accept or non-accept)
        state_type = "accept" if state in dfa.accepting_states else ""
        # Print subset, state type, and transitions for a and b
        print(
            "{%s}\t\t%s\t%s\t%s"
            % (
                ",".join(str(s) for s in state),
                state_type,
                dfa.transitions[state].get("a", ""),
                dfa.transitions[state].get("b", ""),
            )
        )


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


def minimize(self):
    # Step 1: remove unreachable states
    reachable_states = set()
    stack = [self.start_state]
    while stack:
        state = stack.pop()
        reachable_states.add(state)
        for symbol in self.alphabet:
            next_state = self.transitions.get(state, {}).get(symbol, None)
            if next_state and next_state not in reachable_states:
                stack.append(next_state)
    new_states = reachable_states.intersection(self.states)

    # Step 2: group states into accepting and non-accepting sets
    accepting_set = set(self.accepting_states)
    non_accepting_set = new_states - accepting_set
    groups = [non_accepting_set, accepting_set]

    # Step 3: iteratively split groups based on transition subgroups
    while True:
        new_groups = []
        for group in groups:
            subgroups = {}
            for state in group:
                subgroup_key = tuple(
                    self.transitions.get(state, {}).get(symbol, None)
                    for symbol in self.alphabet
                )
                if subgroup_key in subgroups:
                    subgroups[subgroup_key].add(state)
                else:
                    subgroups[subgroup_key] = set([state])
            for subgroup in subgroups.values():
                new_groups.append(subgroup)
        if new_groups == groups:
            break
        groups = new_groups

    # Step 4: create a new DFA using the resulting groups as states
    new_states = [frozenset(group) for group in groups]
    new_transitions = {}
    for state in new_states:
        for symbol in self.alphabet:
            next_state = self.transitions.get(next(iter(state)), {}).get(symbol, None)
            for group in new_states:
                if next_state in group:
                    new_transitions[state] = new_transitions.get(state, {})
                    new_transitions[state][symbol] = group
                    break
    new_start_state = next(group for group in new_states if self.start_state in group)
    new_accepting_states = [
        group for group in new_states if group.intersection(self.accepting_states)
    ]
    return DFA(
        new_states,
        self.alphabet,
        new_transitions,
        new_start_state,
        new_accepting_states,
    )


# example usage:
# nfa1 = NFA(
#     states={"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"},
#     alphabet={"a", "b", "c"},
#     transitions={
#         "0": {"ε": {"1", "5"}},
#         "1": {"ε": {"2", "4"}},
#         "2": {"a": {"3"}},
#         "3": {"ε": {"2", "4"}},
#         "4": {"ε": {"9"}},
#         "5": {"ε": {"6", "8"}},
#         "6": {"b": {"7"}},
#         "7": {"ε": {"6", "8"}},
#         "8": {"ε": {"9"}},
#         "9": {"c": {"10"}},
#     },
#     start_state="0",
#     accepting_states={"10"},
# )

# example usage:
nfa2 = NFA(
    states={
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11",
        "12",
        "13",
        "14",
        "15",
        "16",
        "17",
    },
    alphabet={"a", "b"},
    transitions={
        "0": {"ε": {"1", "7"}},
        "1": {"ε": {"2", "4"}},
        "2": {"b": {"3"}},
        "3": {"ε": {"6"}},
        "4": {"b": {"5"}},
        "5": {"ε": {"6"}},
        "6": {"ε": {"7", "1"}},
        "7": {"a": {"8"}},
        "8": {"b": {"9"}},
        "9": {"b": {"10"}},
        "10": {"ε": {"11", "17"}},
        "11": {"ε": {"12", "14"}},
        "12": {"a": {"13"}},
        "13": {"ε": {"16"}},
        "14": {"b": {"15"}},
        "15": {"ε": {"16"}},
        "16": {"ε": {"17", "11"}},
    },
    start_state="0",
    accepting_states={"17"},
)


dfa = nfa_to_dfa(nfa2)
print_dfa(dfa)
mini = minimize(dfa)
draw_dfa(dfa)

# draw_dfa(mini)

# draw_dfa(dfa)
# print("DFA states: ", dfa.states)
# print("DFA transitions: ", dfa.transitions)
# print("DFA start state: ", dfa.start_state)
# print("DFA accepting states: ", dfa.accepting_states)

# Simulacion AFN
input_string = "abbbca"
result = simulate_nfa(nfa2, input_string)
print("\nSimulacion AFN")
print(f"\nEl input {input_string} {'es' if result else 'no es '}aceptada por el AFN.")

# Simulacion AFD
input_string = "c"
is_accepted = run_dfa(dfa, input_string)
print("\nSimulacion AFD")
print(
    f"\nEl input {input_string} {'es ' if is_accepted else 'no es '}aceptada por el AFD.\n"
)
