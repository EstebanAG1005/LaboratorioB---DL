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


def minimize_dfa(dfa):
    # First, we create the set of final states and non-final states
    final_states = set(state for state in dfa.states if state in dfa.accepting_states)
    non_final_states = set(dfa.states) - final_states

    # We initialize the partition with these two sets
    partition = [final_states, non_final_states]

    while True:
        # We create a new partition to compare with the old partition
        new_partition = []

        # We iterate through each set in the old partition
        for group in partition:
            # We create a dictionary to store which group each state belongs to
            state_groups = {}

            # We iterate through each state in the group
            for state in group:
                # We get the transitions for the state and sort them
                if state in dfa.transitions:
                    transitions = tuple(sorted(dfa.transitions[state].items()))
                else:
                    transitions = ()

                # We iterate through each set in the new partition
                for i, new_group in enumerate(new_partition):
                    try:
                        new_transitions = tuple(
                            sorted(dfa.transitions[next(iter(new_group))].items())
                        )
                    except KeyError:
                        new_transitions = ()

                    # If the transitions are the same, we add the state to the group
                    if transitions == new_transitions:
                        state_groups[state] = i
                        break
                else:
                    # If the transitions are not the same for any existing group, we create a new group
                    state_groups[state] = len(new_partition)
                    new_partition.append(set([state]))

            # We iterate through each set in the state_groups dictionary
            for group_idx in set(state_groups.values()):
                # We create a new group and add each state in the state_groups dictionary to the group
                new_group = set(
                    [state for state, idx in state_groups.items() if idx == group_idx]
                )

                # If the new group has more than one state, we add it to the new partition
                if len(new_group) > 1:
                    new_partition.append(new_group)

        # If the new partition is the same as the old partition, we are finished
        if len(new_partition) == len(partition):
            break

        # Otherwise, we update the partition and repeat the process
        partition = new_partition

    # We create a new DFA using the final partition
    new_states = [frozenset(group) for group in partition]
    new_start_state = next(
        iter([state for state in new_states if dfa.start_state in state])
    )
    new_final_states = set(
        [state for state in new_states if state.intersection(dfa.accepting_states)]
    )
    new_transitions = {}

    for state in new_states:
        for symbol in dfa.alphabet:
            if (
                next(iter(state)) in dfa.transitions
                and symbol in dfa.transitions[next(iter(state))]
            ):
                next_state = dfa.transitions[next(iter(state))][symbol]
            else:
                next_state = None
            for new_state in new_states:
                if next_state in new_state:
                    new_transitions[state] = new_transitions.get(state, {})
                    new_transitions[state][symbol] = new_state

    new_dfa = DFA(
        new_states, dfa.alphabet, new_transitions, new_start_state, new_final_states
    )

    return new_dfa


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
mini = minimize_dfa(dfa)
# draw_dfa1(dfa)
draw_dfa1(mini)

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
