# alpha_algorithm.py
import sys
sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd
from collections import defaultdict, Counter
from itertools import combinations
import pprint
import json
from typing import List, Dict, Set, Tuple
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# Step 1: Read Event Log from a Text File
def read_event_log(file_path: str) -> List[List[str]]:
    """
    Read the event log from a JSON-formatted text file.

    :param file_path: Path to the event log text file.
    :return: List of traces, each trace is a list of events.
    """
    with open(file_path, 'r') as file:
        event_log = json.load(file)
    return event_log

# Step 1: Convert Event Log into Unique Traces and Frequencies
def get_unique_traces(event_log: List[List[str]]) -> Counter:
    trace_counter = Counter()
    for trace in event_log:
        if trace:  # Exclude empty traces if desired
            trace_tuple = tuple(trace)  # Convert list to tuple to make it hashable
            trace_counter[trace_tuple] += 1
    return trace_counter

# Display Unique Traces and Frequencies in a Tabular Format
def display_unique_traces(trace_counter: Counter):
    data = {
        'Trace': [
            ' -> '.join(trace) if trace else 'Empty Trace' 
            for trace in trace_counter.keys()
        ],
        'Frequency': list(trace_counter.values())
    }
    df = pd.DataFrame(data)
    print("### Step 1: Unique Traces and Frequencies")
    print(df.to_string(index=False))
    print("\n")

# Step 2: Extract Unique Events (TL), Initial Events (TI), and Final Events (TO)
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

# Display Events
def display_events(TL: Set[str], TI: Set[str], TO: Set[str]):
    print("### Step 2: Events")
    print(f"Unique Events (TL): {sorted(TL)}")
    print(f"Initial Events (TI): {sorted(TI)}")
    print(f"Final Events (TO): {sorted(TO)}\n")

# Step 3: Construct the Footprint Matrix
def construct_footprint_matrix(event_log: List[List[str]], TL: Set[str]) -> Dict[str, Dict[str, str]]:
    relations = defaultdict(lambda: defaultdict(str))
    # Initialize matrix
    for a in TL:
        for b in TL:
            if a == b:
                relations[a][b] = '>'
            else:
                relations[a][b] = '#'

    # Determine direct succession
    for trace in event_log:
        for i in range(len(trace)-1):
            a = trace[i]
            b = trace[i+1]
            relations[a][b] = '→'

    # Determine causal and parallel relationships
    for a, b in combinations(TL, 2):
        if relations[a][b] == '→' and relations[b][a] != '→':
            relations[a][b] = '→'
            relations[b][a] = '#'
        elif relations[a][b] == '→' and relations[b][a] == '→':
            relations[a][b] = '||'
            relations[b][a] = '||'
        else:
            # Retain existing relations
            relations[a][b] = relations[a][b]
            relations[b][a] = relations[b][a]

    # Convert to DataFrame for better visualization
    footprint_data = {
        a: [relations[a][b] for b in sorted(TL)]
        for a in sorted(TL)
    }
    footprint_df = pd.DataFrame(footprint_data, index=sorted(TL))
    print("### Step 3: Footprint Matrix")
    print(footprint_df)
    print("\n")
    return relations

# Step 4: Create Sets for Petri Net Construction
def create_alpha_sets(relations: Dict[str, Dict[str, str]], TL: Set[str]) -> Tuple[Set[Tuple[str, str]], Set[Tuple[str, str]], Set[Tuple[str, str]], Set[Tuple[str, str]], Dict[Tuple[str, str], str]]:
    XL = set()
    YL = set()
    for a in TL:
        for b in TL:
            if relations[a][b] == '→':
                XL.add((a, b))
            elif relations[a][b] == '||':
                YL.add((a, b))
    # Remove duplicates in YL by sorting
    YL = set([tuple(sorted(pair)) for pair in YL])

    # Create Place Set (PL) based on XL and YL
    PL = set()
    for a, b in XL:
        PL.add((a, b))
    for a, b in YL:
        PL.add((a, b))

    # Assign unique identifiers to places
    place_mapping = {place: f"P{i}" for i, place in enumerate(sorted(PL), 1)}

    # Flow Relation (FL)
    FL = set()
    for place in PL:
        a, b = place
        FL.add((a, place_mapping[place]))  # a -> Pi
        FL.add((place_mapping[place], b))  # Pi -> b

    return XL, YL, PL, FL, place_mapping

# Display the sets
def display_alpha_sets(XL: Set[Tuple[str, str]], YL: Set[Tuple[str, str]], PL: Set[Tuple[str, str]], FL: Set[Tuple[str, str]]):
    print("### Step 4: Alpha Sets")
    print(f"Causal Relationships (XL): {sorted(XL)}")
    print(f"Maximal Pairs (YL): {sorted(YL)}")
    print(f"Place Set (PL): {sorted(PL)}")
    print(f"Flow Relation (FL): {sorted(FL, key=lambda x: str(x))}\n")

# Step 5: Build the Petri Net (α(L)) Model
def build_petri_net(TL: Set[str], TI: Set[str], TO: Set[str], PL: Set[Tuple[str, str]], FL: Set[Tuple[str, str]], place_mapping: Dict[Tuple[str, str], str]) -> Dict[str, List[str]]:
    # Places, Transitions, and Arcs
    places = set([place_mapping[place] for place in PL])
    transitions = set(TL)
    arcs = set(FL)

    # Define the Petri Net components
    petri_net = {
        'Places': sorted(places),
        'Transitions': sorted(transitions),
        'Arcs': sorted(arcs)
    }

    print("### Step 5: Petri Net (α(L)) Model")
    print("Places:")
    pprint.pprint(petri_net['Places'])
    print("\nTransitions:")
    pprint.pprint(petri_net['Transitions'])
    print("\nArcs:")
    pprint.pprint(petri_net['Arcs'])
    print("\n")
    return petri_net

# Optionally, display the Petri Net in a more readable format
def display_petri_net(petri_net: Dict[str, List[str]], place_mapping: Dict[Tuple[str, str], str], TI: Set[str], TO: Set[str]):
    print("### Petri Net Details")
    print(f"Initial Places (connected to initial events {sorted(TI)}):")
    for place in petri_net['Places']:
        for ti in TI:
            # Check if there's an arc from ti to place
            if (ti, place) in petri_net['Arcs']:
                print(f"  {ti} → {place}")
    print(f"\nFinal Places (connected to final events {sorted(TO)}):")
    for place in petri_net['Places']:
        for to in TO:
            # Check if there's an arc from place to to
            if (place, to) in petri_net['Arcs']:
                print(f"  {place} → {to}")
    print("\nComplete Arcs:")
    for arc in petri_net['Arcs']:
        print(f"  {arc[0]} → {arc[1]}")
    print("\n")

# Step 6: Visualize the Petri Net
def visualize_petri_net(petri_net: Dict[str, List[str]]):
    """
    Visualize the Petri net using networkx and matplotlib.

    :param petri_net: Dictionary containing 'Places', 'Transitions', and 'Arcs'.
    """
    G = nx.DiGraph()

    # Add Places and Transitions as nodes with different shapes
    for place in petri_net['Places']:
        G.add_node(place, shape='circle', color='lightblue', label=place, type='Place')
    for transition in petri_net['Transitions']:
        G.add_node(transition, shape='square', color='lightgreen', label=transition, type='Transition')

    # Add Arcs
    for arc in petri_net['Arcs']:
        G.add_edge(arc[0], arc[1])

    # Position nodes using a spring layout for better visualization
    pos = nx.spring_layout(G, seed=42)  # Fixed seed for reproducibility

    # Separate nodes by type for styling
    places = [node for node, attr in G.nodes(data=True) if attr['type'] == 'Place']
    transitions = [node for node, attr in G.nodes(data=True) if attr['type'] == 'Transition']

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=places, node_shape='o', node_color='lightblue', node_size=1500, label='Places')
    nx.draw_networkx_nodes(G, pos, nodelist=transitions, node_shape='s', node_color='lightgreen', node_size=1500, label='Transitions')

    # Draw edges (arcs)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowstyle='->', arrowsize=20)

    # Draw labels
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

    # Create legend using Line2D with different markers
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Place',
               markerfacecolor='lightblue', markersize=15, markeredgecolor='black'),
        Line2D([0], [0], marker='s', color='w', label='Transition',
               markerfacecolor='lightgreen', markersize=15, markeredgecolor='black')
    ]
    plt.legend(handles=legend_elements, loc='upper right')

    plt.title("Discovered Petri Net")
    plt.axis('off')  # Hide axes
    plt.tight_layout()
    plt.show()

def main():
    # Read the event log from 'event_log.txt'
    event_log = read_event_log('event_log.txt')

    # Step 1: Unique Traces and Frequencies
    unique_traces = get_unique_traces(event_log)
    display_unique_traces(unique_traces)

    # Step 2: Extract Unique Events, Initial Events, and Final Events
    TL, TI, TO = extract_events(event_log)
    display_events(TL, TI, TO)

    # Step 3: Construct the Footprint Matrix
    relations = construct_footprint_matrix(event_log, TL)

    # Step 4: Create Sets for Petri Net Construction
    XL, YL, PL, FL, place_mapping = create_alpha_sets(relations, TL)
    display_alpha_sets(XL, YL, PL, FL)

    # Step 5: Build the Petri Net (α(L)) Model
    petri_net = build_petri_net(TL, TI, TO, PL, FL, place_mapping)

    # Display the Petri Net Details
    display_petri_net(petri_net, place_mapping, TI, TO)

    # Step 6: Visualize the Petri Net
    visualize_petri_net(petri_net)

if __name__ == "__main__":
    main()
