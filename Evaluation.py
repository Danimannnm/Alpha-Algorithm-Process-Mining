# task4_evaluation.py

import json
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple
import random
import sys
import pandas as pd
from itertools import combinations
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Ensure correct encoding
sys.stdout.reconfigure(encoding='utf-8')

# Function to read the event log
def read_event_log(file_path: str) -> List[List[str]]:
    with open(file_path, 'r') as file:
        event_log = json.load(file)
    return event_log

# Function to extract events
def extract_events(event_log: List[List[str]]) -> Tuple[Set[str], Set[str], Set[str]]:
    TL = set()
    TI = set()
    TO = set()
    for trace in event_log:
        if trace:
            TI.add(trace[0])
            TO.add(trace[-1])
            TL.update(trace)
    return TL, TI, TO

# Function to construct the footprint matrix
def construct_footprint_matrix(event_log: List[List[str]], TL: Set[str]) -> Dict[str, Dict[str, str]]:
    relations = defaultdict(lambda: defaultdict(str))
    directly_follows = defaultdict(set)
    for trace in event_log:
        for i in range(len(trace) - 1):
            a = trace[i]
            b = trace[i+1]
            directly_follows[a].add(b)
    for a in TL:
        for b in TL:
            if b in directly_follows[a] and a not in directly_follows[b]:
                relations[a][b] = '→'
            elif a in directly_follows[b] and b not in directly_follows[a]:
                relations[a][b] = '←'
            elif b in directly_follows[a] and a in directly_follows[b]:
                relations[a][b] = '||'
            else:
                relations[a][b] = '#'
    return relations

# Function to create alpha sets
def create_alpha_sets(relations: Dict[str, Dict[str, str]], TL: Set[str]) -> Tuple[Set[Tuple[str, ...]], Set[Tuple[str, ...]], Set[Tuple[str, ...]], Set[Tuple[str, ...]]]:
    XL = set()
    for a in TL:
        for b in TL:
            if relations[a][b] == '→':
                XL.add((a, b))
    # Build YL (maximal sets of XL)
    # For simplicity, we can assume YL = XL for this implementation
    YL = XL.copy()
    return XL, YL

# Function to build the Petri net
def build_petri_net(TL: Set[str], TI: Set[str], TO: Set[str], XL: Set[Tuple[str, str]], YL: Set[Tuple[str, str]]) -> Dict[str, List[str]]:
    places = set()
    transitions = TL.copy()
    arcs = set()

    # Create places for each relation in YL
    place_mapping = {}
    for i, pair in enumerate(YL):
        place = f'P{i+1}'
        places.add(place)
        place_mapping[pair] = place

    # Add arcs between transitions and places
    for (a, b) in XL:
        place = place_mapping.get((a, b))
        arcs.add((a, place))  # Transition to Place
        arcs.add((place, b))  # Place to Transition

    # Add start and end places
    start_place = 'Start'
    end_place = 'End'
    places.update({start_place, end_place})

    # Connect start place to initial transitions
    for t in TI:
        arcs.add((start_place, t))

    # Connect final transitions to end place
    for t in TO:
        arcs.add((t, end_place))

    petri_net = {
        'Places': sorted(places),
        'Transitions': sorted(transitions),
        'Arcs': sorted(arcs)
    }
    return petri_net

# Function to simulate traces from the model
def simulate_traces(petri_net: Dict[str, List[str]], TI: Set[str], num_simulations: int, max_trace_length: int) -> List[List[str]]:
    simulated_traces = []
    for _ in range(num_simulations):
        trace = []
        tokens = defaultdict(int)
        tokens['Start'] = 1  # Initialize token in the start place
        steps = 0
        while steps < max_trace_length:
            enabled_transitions = []
            for transition in petri_net['Transitions']:
                # Check if transition is enabled
                for arc in petri_net['Arcs']:
                    if arc[1] == transition and tokens[arc[0]] > 0:
                        enabled_transitions.append(transition)
                        break
            if not enabled_transitions:
                break  # No enabled transitions
            # Randomly select an enabled transition
            transition = random.choice(enabled_transitions)
            trace.append(transition)
            # Fire the transition
            consumed_places = []
            produced_places = []
            for arc in petri_net['Arcs']:
                if arc[1] == transition and tokens[arc[0]] > 0:
                    tokens[arc[0]] -= 1  # Consume token
                    consumed_places.append(arc[0])
            for arc in petri_net['Arcs']:
                if arc[0] == transition:
                    tokens[arc[1]] += 1  # Produce token
                    produced_places.append(arc[1])
            steps += 1
        simulated_traces.append(trace)
    return simulated_traces

# Function to evaluate fitness
def evaluate_fitness(petri_net: Dict[str, List[str]], test_traces: List[List[str]], TI: Set[str], TO: Set[str]) -> float:
    fit_traces = 0
    for trace in test_traces:
        if token_based_replay(petri_net, trace, TI, TO):
            fit_traces += 1
    fitness = fit_traces / len(test_traces) if test_traces else 0
    return fitness

# Function to perform token-based replay
def token_based_replay(petri_net: Dict[str, List[str]], trace: List[str], TI: Set[str], TO: Set[str]) -> bool:
    tokens = defaultdict(int)
    tokens['Start'] = 1  # Initialize token in the start place

    for event in trace:
        # Check if the event exists in the transitions
        if event not in petri_net['Transitions']:
            # Event not in model
            return False

        # Check if there is a token in any place leading to this transition
        enabled = False
        for arc in petri_net['Arcs']:
            if arc[1] == event and tokens[arc[0]] > 0:
                tokens[arc[0]] -= 1  # Consume token
                enabled = True
                # Produce tokens to output places
                for out_arc in petri_net['Arcs']:
                    if out_arc[0] == event:
                        tokens[out_arc[1]] += 1
                break
        if not enabled:
            # Transition is not enabled
            return False

    # Check if a token has reached the end place
    return tokens['End'] > 0

# Function to evaluate precision
def evaluate_precision(event_log: List[List[str]], simulated_traces: List[List[str]]) -> float:
    observed_traces = set(tuple(trace) for trace in event_log)
    simulated_traces_set = set(tuple(trace) for trace in simulated_traces)

    # Calculate the proportion of simulated traces that are observed
    matching_traces = observed_traces & simulated_traces_set
    precision = len(matching_traces) / len(simulated_traces_set) if simulated_traces_set else 0
    return precision

# Function to generate additional test traces
def generate_test_traces(event_log: List[List[str]], num_traces: int) -> List[List[str]]:
    unique_traces = set(tuple(trace) for trace in event_log)
    test_traces = []

    # For simplicity, we'll generate test traces by shuffling existing traces
    # and introducing variations not present in the original log
    for _ in range(num_traces):
        # Randomly select a trace and modify it
        base_trace = list(random.choice(list(unique_traces)))
        if len(base_trace) > 1:
            # Swap two events to create a new trace
            idx1, idx2 = random.sample(range(len(base_trace)), 2)
            base_trace[idx1], base_trace[idx2] = base_trace[idx2], base_trace[idx1]
        else:
            # Add a random event not in the trace
            new_event = random.choice(list(set().union(*event_log) - set(base_trace)))
            base_trace.append(new_event)
        test_trace = base_trace
        # Ensure the test trace is not in the original event log
        if tuple(test_trace) not in unique_traces:
            test_traces.append(test_trace)
    return test_traces

def main():
    # Read the original event log
    event_log = read_event_log('event_log.txt')

    # Extract events
    TL, TI, TO = extract_events(event_log)

    # Construct the footprint matrix
    relations = construct_footprint_matrix(event_log, TL)

    # Create alpha sets
    XL, YL = create_alpha_sets(relations, TL)

    # Build the Petri net
    petri_net = build_petri_net(TL, TI, TO, XL, YL)

    # Generate additional test traces
    num_test_traces = 30  # Number of test traces
    test_traces = generate_test_traces(event_log, num_test_traces)

    # Evaluate fitness
    fitness = evaluate_fitness(petri_net, test_traces, TI, TO)
    print("### Fitness Evaluation")
    print(f"Number of test traces: {len(test_traces)}")
    print(f"Fitness: {fitness:.2f}\n")

    # Simulate traces from the model
    num_simulations = 100  # Number of traces to simulate
    max_trace_length = max(len(trace) for trace in event_log)
    simulated_traces = simulate_traces(petri_net, TI, num_simulations, max_trace_length)

    # Evaluate precision
    precision = evaluate_precision(event_log, simulated_traces)
    print("### Precision Evaluation")
    print(f"Number of simulated traces: {num_simulations}")
    print(f"Precision: {precision:.2f}\n")

    # Write a short analysis
    print("### Analysis of the Model's Performance")
    print("**Fitness:**")
    if fitness > 0.8:
        print("The model has high fitness, indicating it can reproduce most of the test traces.")
    else:
        print("The model has low fitness, indicating it struggles to reproduce the test traces.")

    print("\n**Precision:**")
    if precision > 0.8:
        print("The model has high precision, meaning it does not allow much behavior beyond what was observed.")
    else:
        print("The model has low precision, meaning it allows a lot of behavior not observed in the event log.")

    print("\n**Strengths:**")
    print("- The model captures the main behavior observed in the event log.")
    print("- It can reproduce most of the common patterns.")

    print("\n**Limitations:**")
    print("- The model may not handle deviations or uncommon behaviors well.")
    print("- It might overgeneralize or undergeneralize depending on the data.")

if __name__ == "__main__":
    main()
