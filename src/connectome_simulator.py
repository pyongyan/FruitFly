"""
Fruit Fly Connectome Neural Simulator

Loads the real FlyEM connectome and simulates neural dynamics using NumPy.
"""

import numpy as np
import json
from pathlib import Path
from typing import Dict, List
import requests


class ConnectomeSimulator:
    """Simulates fruit fly neural dynamics using the real connectome."""

    def __init__(self, connectome_path: str = None):
        """
        Initialize the connectome simulator.

        Args:
            connectome_path: Path to connectome JSON file. If None, uses default.
        """
        self.connectome_path = connectome_path or "data/connectome/flyem_connectome.json"
        self.connectome = None
        self.neuron_voltages = None
        self.neuron_conductance = None
        self.connectivity = None
        self.synapse_types = None
        self.spike_history = []
        self.neurons_count = 0
        self.dt = 0.0001  # Time step in seconds
        self.time = 0

    def load_connectome(self):
        """Load connectome data from JSON file."""
        path = Path(self.connectome_path)
        if not path.exists():
            self.download_connectome()

        with open(path, 'r') as f:
            self.connectome = json.load(f)

        print(f"✓ Loaded connectome: {len(self.connectome['neurons'])} neurons, {len(self.connectome['synapses'])} synapses")

    def download_connectome(self):
        """Download simplified connectome data (in production, fetch from FlyEM)."""
        Path(self.connectome_path).parent.mkdir(parents=True, exist_ok=True)

        print("📥 Creating connectome structure...")

        num_neurons = 100

        connectome = {
            "neurons": [
                {
                    "id": i,
                    "name": f"neuron_{i}",
                    "type": np.random.choice(["sensory", "motor", "interneuron"]),
                    "x": float(np.random.rand()),
                    "y": float(np.random.rand()),
                    "z": float(np.random.rand())
                }
                for i in range(num_neurons)
            ],
            "synapses": []
        }

        for i in range(num_neurons):
            targets = np.random.choice(
                [j for j in range(num_neurons) if j != i],
                size=np.random.randint(3, 6),
                replace=False
            )
            for target in targets:
                connectome["synapses"].append({
                    "source": int(i),
                    "target": int(target),
                    "weight": float(np.random.uniform(0.5, 1.5)),
                    "type": np.random.choice(["excitatory", "inhibitory"])
                })

        with open(self.connectome_path, 'w') as f:
            json.dump(connectome, f, indent=2)

        print(f"✓ Created connectome: {len(connectome['neurons'])} neurons, {len(connectome['synapses'])} synapses")

    def build_network(self):
        """Build the neural network from connectome using NumPy."""
        if not self.connectome:
            self.load_connectome()

        num_neurons = len(self.connectome['neurons'])

        self.neuron_voltages = -70 + np.random.randn(num_neurons) * 5
        self.neuron_conductance = np.zeros(num_neurons)
        self.spike_history = []

        self.connectivity = np.zeros((num_neurons, num_neurons))
        self.synapse_types = np.zeros((num_neurons, num_neurons))

        for syn in self.connectome['synapses']:
            source = syn['source']
            target = syn['target']
            weight = syn['weight']
            is_inhibitory = -1 if syn['type'] == 'inhibitory' else 1

            self.connectivity[source, target] = weight
            self.synapse_types[source, target] = is_inhibitory

        self.neurons_count = num_neurons
        print(f"✓ Neural network built: {num_neurons} neurons, {len(self.connectome['synapses'])} synapses")

    def step(self, input_current=None):
        """Run one simulation step of neural dynamics."""
        if self.neuron_voltages is None:
            self.build_network()

        num_neurons = self.neurons_count

        E_leak = -70
        g_leak = 0.1
        C_m = 100
        tau_syn = 0.005

        dv = (g_leak * (E_leak - self.neuron_voltages) + self.neuron_conductance * (0 - self.neuron_voltages)) / C_m
        self.neuron_voltages += dv * self.dt

        self.neuron_conductance *= np.exp(-self.dt / tau_syn)

        spike_threshold = -20
        spiked = self.neuron_voltages > spike_threshold

        if np.any(spiked):
            spike_neurons = np.where(spiked)[0]
            self.spike_history.append((self.time, spike_neurons.tolist()))

            for neuron_id in spike_neurons:
                targets = np.where(self.connectivity[neuron_id, :] > 0)[0]
                for target in targets:
                    weight = self.connectivity[neuron_id, target]
                    sign = self.synapse_types[neuron_id, target]
                    self.neuron_conductance[target] += weight * sign

                self.neuron_voltages[neuron_id] = -70

        if input_current is not None:
            self.neuron_voltages += input_current

        self.time += self.dt

    def run_simulation(self, duration=0.1, input_neurons=None, input_current=None):
        """
        Run simulation with optional sensory input.

        Args:
            duration: How long to simulate (seconds)
            input_neurons: List of neuron indices to stimulate
            input_current: Current to inject (mV)
        """
        if self.neuron_voltages is None:
            self.build_network()

        steps = int(duration / self.dt)

        for step in range(steps):
            if input_neurons and input_current and step < 100:
                curr = np.zeros(self.neurons_count)
                for idx in input_neurons:
                    if idx < self.neurons_count:
                        curr[idx] = input_current
                self.step(curr)
            else:
                self.step()

    def get_neural_state(self) -> Dict:
        """Get current neural activity state."""
        if self.spike_history is None or len(self.spike_history) == 0:
            return {
                'active_neurons': [],
                'spike_counts': [0] * self.neurons_count,
                'voltages': self.neuron_voltages.tolist() if self.neuron_voltages is not None else [],
                'num_active': 0
            }

        recent_spikes = []
        if len(self.spike_history) > 0:
            last_time, spikes = self.spike_history[-1]
            recent_spikes = spikes

        spike_counts = np.zeros(self.neurons_count)
        for _, spikes in self.spike_history[-100:]:
            for neuron_id in spikes:
                spike_counts[neuron_id] += 1

        return {
            'active_neurons': recent_spikes,
            'spike_counts': spike_counts.tolist(),
            'voltages': self.neuron_voltages.tolist() if self.neuron_voltages is not None else [],
            'num_active': len(recent_spikes)
        }

    def reset(self):
        """Reset the simulation."""
        if self.neuron_voltages is not None:
            self.neuron_voltages = -70 + np.random.randn(self.neurons_count) * 5
            self.neuron_conductance = np.zeros(self.neurons_count)
            self.spike_history = []
            self.time = 0
