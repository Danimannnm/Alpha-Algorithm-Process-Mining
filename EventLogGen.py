# generate_event_log.py

import random
import string
from typing import List, Dict, Set
import json

class ProcessModel:
    def __init__(self, tasks: Dict[str, List[str]]):
        """
        Initialize the process model.

        :param tasks: A dictionary where keys are task names and values are lists of successor task names.
        """
        self.tasks = tasks
        self.start_tasks = self.find_start_tasks()
        self.end_tasks = self.find_end_tasks()
        self.all_paths = self.find_all_paths()

    def find_start_tasks(self) -> List[str]:
        """
        Find tasks with no predecessors.

        :return: List of start task names.
        """
        all_successors = set()
        for successors in self.tasks.values():
            all_successors.update(successors)
        start_tasks = [task for task in self.tasks if task not in all_successors]
        return start_tasks

    def find_end_tasks(self) -> List[str]:
        """
        Find tasks with no successors.

        :return: List of end task names.
        """
        end_tasks = [task for task, successors in self.tasks.items() if not successors]
        return end_tasks

    def find_all_paths(self) -> List[List[str]]:
        """
        Find all possible paths from start tasks to end tasks.

        :return: List of paths, each path is a list of task names.
        """
        paths = []
        for start in self.start_tasks:
            self.dfs(start, [start], paths)
        return paths

    def dfs(self, current: str, path: List[str], paths: List[List[str]]):
        """
        Depth-First Search to find all paths.

        :param current: Current task name.
        :param path: Current path.
        :param paths: List to store all paths.
        """
        if current in self.end_tasks:
            paths.append(path.copy())
            return
        for successor in self.tasks.get(current, []):
            if successor not in path:  # Avoid cycles
                self.dfs(successor, path + [successor], paths)

class EventLogGenerator:
    def __init__(self, process_model: ProcessModel, noise_level: float = 0.05,
                 uncommon_path_freq: float = 0.1, missing_event_prob: float = 0.05,
                 noise_event_pool: List[str] = None):
        """
        Initialize the event log generator.

        :param process_model: An instance of ProcessModel.
        :param noise_level: Fraction of noise events to add.
        :param uncommon_path_freq: Probability of selecting an uncommon path.
        :param missing_event_prob: Probability of an event being missing.
        :param noise_event_pool: List of possible noise events.
        """
        self.process_model = process_model
        self.noise_level = noise_level
        self.uncommon_path_freq = uncommon_path_freq
        self.missing_event_prob = missing_event_prob
        self.noise_event_pool = noise_event_pool or self.generate_noise_pool()

    def generate_noise_pool(self) -> List[str]:
        """
        Generate a pool of noise events.

        :return: List of noise event names.
        """
        # For simplicity, generate random strings
        noise_pool = []
        for _ in range(20):
            noise_event = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
            noise_pool.append(noise_event)
        return noise_pool

    def select_path(self) -> List[str]:
        """
        Select a path based on uncommon path frequency.

        :return: A list of task names representing the selected path.
        """
        if random.random() < self.uncommon_path_freq and len(self.process_model.all_paths) > 1:
            # Select a random uncommon path
            path = random.choice(self.process_model.all_paths)
            return path
        else:
            # Select the most common path (first path)
            return self.process_model.all_paths[0]

    def introduce_missing_events(self, trace: List[str]) -> List[str]:
        """
        Remove events from the trace based on missing_event_prob.

        :param trace: Original trace.
        :return: Trace with some events removed.
        """
        return [event for event in trace if random.random() > self.missing_event_prob]

    def introduce_noise(self, trace: List[str]) -> List[str]:
        """
        Insert noise events into the trace based on noise_level.

        :param trace: Original trace.
        :return: Trace with noise events inserted.
        """
        noisy_trace = trace.copy()
        num_noise = int(len(trace) * self.noise_level)
        for _ in range(num_noise):
            noise_event = random.choice(self.noise_event_pool)
            insert_position = random.randint(0, len(noisy_trace))
            noisy_trace.insert(insert_position, noise_event)
        return noisy_trace

    def generate_trace(self) -> List[str]:
        """
        Generate a single trace with possible noise and missing events.

        :return: A list of events representing the trace.
        """
        path = self.select_path()
        # Introduce missing events
        path_with_missing = self.introduce_missing_events(path)
        # Introduce noise
        noisy_trace = self.introduce_noise(path_with_missing)
        return noisy_trace

    def generate_event_log(self, num_traces: int) -> List[List[str]]:
        """
        Generate an event log containing multiple traces.

        :param num_traces: Number of traces to generate.
        :return: List of traces, each trace is a list of events.
        """
        event_log = []
        for _ in range(num_traces):
            trace = self.generate_trace()
            event_log.append(trace)
        return event_log

def main():
    # Example process description
    # This should be replaced with actual input parsing as needed
    process_description = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["D", "E"],
        "D": ["E"],
        "E": []
    }

    # Initialize the process model
    process_model = ProcessModel(tasks=process_description)

    # Define generator parameters
    num_traces = 100  # You can adjust this as needed
    noise_level = 0.1  # 10% of the trace will be noise
    uncommon_path_freq = 0.2  # 20% of the traces will use uncommon paths
    missing_event_prob = 0.1  # 10% chance to miss an event

    # Initialize the event log generator
    generator = EventLogGenerator(
        process_model=process_model,
        noise_level=noise_level,
        uncommon_path_freq=uncommon_path_freq,
        missing_event_prob=missing_event_prob
    )

    # Generate the event log
    event_log = generator.generate_event_log(num_traces=num_traces)

    # Save the event log to a text file in JSON format
    with open('event_log.txt', 'w') as file:
        json.dump(event_log, file, indent=2)

    print(f"Event log generated with {num_traces} traces and saved to 'event_log.txt'.")

if __name__ == "__main__":
    main()
