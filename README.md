# Process Mining System - Alpha Algorithm Implementation

A comprehensive Python-based process mining system that implements the Alpha Algorithm for discovering process models from event logs, along with tools for event log generation and model evaluation.

## Overview

This project provides a complete workflow for process mining tasks:
- **Event Log Generation** with configurable noise and variations
- **Alpha Algorithm** implementation for Petri net discovery
- **Model Evaluation** with fitness and precision metrics
- **Visualization** of discovered Petri nets

## Features

### 1. Event Log Generator (`EventLogGen.py`)
- Generate synthetic event logs from process descriptions
- Configurable parameters:
  - Noise level for introducing random events
  - Uncommon path frequency for variant generation
  - Missing event probability for incomplete traces
- Customizable process models with multiple paths
- Output in JSON format

### 2. Alpha Algorithm (`AlphaAlgo.py`)
- Implementation of the classic Alpha Algorithm for process discovery
- Key functionalities:
  - Trace frequency analysis
  - Event extraction (unique, initial, and final events)
  - Footprint matrix construction
  - Causal and parallel relationship detection
  - Petri net model generation
  - Network visualization using NetworkX and Matplotlib

### 3. Model Evaluation (`Evaluation.py`)
- Comprehensive model quality assessment
- **Fitness Evaluation**: Measures how well the model reproduces observed behavior
- **Precision Evaluation**: Measures how much extra behavior the model allows
- Token-based replay for trace validation
- Simulation-based analysis
- Performance metrics and detailed analysis reports

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Dependencies

```bash
pip install pandas networkx matplotlib
```

Or install all dependencies at once:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Generate Event Log

```python
python EventLogGen.py
```

This generates `event_log.txt` with synthetic traces based on the defined process model. Customize the process by modifying the `process_description` dictionary:

```python
process_description = {
    "A": ["B", "C"],
    "B": ["D", "E"],
    "C": ["D", "E"],
    "D": ["E"],
    "E": []
}
```

### 2. Discover Process Model

```python
python AlphaAlgo.py
```

This reads the event log and:
- Displays unique traces with frequencies
- Shows extracted events (TL, TI, TO)
- Constructs and displays the footprint matrix
- Builds the Petri net model
- Visualizes the discovered process model

### 3. Evaluate Model Performance

```python
python Evaluation.py
```

This evaluates the discovered model:
- Calculates fitness score (0.0 to 1.0)
- Calculates precision score (0.0 to 1.0)
- Provides detailed analysis of strengths and limitations

## Output Examples

### Footprint Matrix
The algorithm constructs a footprint matrix showing relationships between events:
- `→` : Causal relationship (a followed by b)
- `||` : Parallel relationship (concurrent events)
- `#` : No direct relationship

### Petri Net Visualization
- **Circles**: Places (connecting transitions)
- **Squares**: Transitions (activities)
- **Arrows**: Flow relations

### Evaluation Metrics
- **Fitness > 0.8**: High quality - model reproduces most observed behavior
- **Precision > 0.8**: Low overfitting - model doesn't allow excessive extra behavior

## File Structure

```
PMS_Final/
├── EventLogGen.py       # Event log generation with noise
├── AlphaAlgo.py         # Alpha Algorithm implementation
├── Evaluation.py        # Model fitness and precision evaluation
├── event_log.txt        # Generated event log (JSON format)
└── README.md           # Project documentation
```

## Configuration

### Event Log Generator Parameters

```python
num_traces = 100              # Number of traces to generate
noise_level = 0.1             # 10% noise events
uncommon_path_freq = 0.2      # 20% uncommon paths
missing_event_prob = 0.1      # 10% chance to skip events
```

### Evaluation Parameters

```python
num_test_traces = 30          # Test traces for fitness
num_simulations = 100         # Simulated traces for precision
```

## Algorithm Workflow

1. **Event Log Input** → Read traces from file
2. **Trace Analysis** → Extract unique events and patterns
3. **Footprint Construction** → Build relationship matrix
4. **Petri Net Discovery** → Apply Alpha Algorithm
5. **Model Visualization** → Display discovered model
6. **Quality Evaluation** → Assess fitness and precision

## Use Cases

- Process discovery from real-world event logs
- Business process analysis and optimization
- Conformance checking and compliance verification
- Educational purposes for learning process mining
- Research in workflow management systems

## Limitations

- The Alpha Algorithm works best with structured, well-formed logs
- Cannot handle all types of process patterns (e.g., duplicate tasks, short loops)
- Noise and incomplete data may affect model quality
- Assumes a sound workflow net structure

## Contributing

This project was developed as part of a Process Simulation course. Feel free to fork and enhance!

## License

This project is available for educational and research purposes.

## Author

Developed for Process Simulation (Semester 5)

## References

- Alpha Algorithm: van der Aalst, W., Weijters, T., & Maruster, L. (2004). "Workflow mining: Discovering process models from event logs"
- Process Mining: van der Aalst, W. (2016). "Process Mining: Data Science in Action"
