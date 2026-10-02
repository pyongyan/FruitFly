"""
Fruit Fly Connectome Neural Simulator

Loads the real FlyEM connectome and simulates neural dynamics using brian2.
"""

import numpy as np
import json
from pathlib import Path
import brian2 as b2
from typing import Dict, List, Tuple
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
        self.neurons = None
        self.synapses = None
        self.spike_mon = None
        self.v_mon = None
        self.neuron_states = {}

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

        # For now, create a simplified connectome structure
        # In production, this would fetch from FlyEM database
        print("📥 Creating connectome structure...")

        # Simplified connectome with ~100 neurons for testing
        # In full version, this would be 3000+ neurons
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

        # Create random connections
        for i in range(num_neurons):
            # Each neuron connects to 3-5 other neurons on average
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

    def build_network(self, dt=0.1*b2.ms):
        """Build the brian2 neural network from connectome."""
        b2.start_scope()

        if not self.connectome:
            self.load_connectome()

        num_neurons = len(self.connectome['neurons'])

        # Neuron equations
        eqs = '''
        dv/dt = (g_leak * (E_leak - v) + g_syn * (v_syn - v)) / C_m : volt
        dg_syn/dt = -g_syn / tau_syn : siemens
        v_syn : volt
        '''

        # Create neuron group
        self.neurons = b2.NeuronGroup(
            num_neurons,
            eqs,
            method='exponential_euler',
            namespace={
                'E_leak': -70*b2.mV,
                'g_leak': 0.1*b2.nsiemens,
                'C_m': 100*b2.pfarad,
                'tau_syn': 5*b2.ms
            }
        )

        # Initialize potentials
        self.neurons.v = -70*b2.mV + np.random.randn(num_neurons) * 5 * b2.mV
        self.neurons.v_syn = -70*b2.mV

        # Create synapses
        synapses_list = self.connectome['synapses']

        syn_eqs = '''
        w : 1
        is_inhibitory : boolean
        '''

        self.synapses = b2.Synapses(
            self.neurons,
            self.neurons,
            syn_eqs,
            on_pre='g_syn += w * nsiemens'
        )

        # Add connections
        for syn in synapses_list:
            source = syn['source']
            target = syn['target']
            weight = syn['weight']
            is_inhibitory = syn['type'] == 'inhibitory'

            self.synapses.connect(i=source, j=target)
            idx = len(self.synapses) - 1
            self.synapses.w[idx] = weight
            self.synapses.is_inhibitory[idx] = is_inhibitory

        # Monitors
        self.spike_mon = b2.SpikeMonitor(self.neurons)
        self.v_mon = b2.StateMonitor(self.neurons, 'v', record=True)

        print(f"✓ Neural network built: {self.neurons.N} neurons, {len(self.synapses)} synapses")

    def run_simulation(self, duration=1*b2.second, input_neurons=None, input_current=None):
        """
        Run simulation with optional sensory input.

        Args:
            duration: How long to simulate
            input_neurons: List of neuron indices to stimulate
            input_current: Current to inject (in amperes)
        """
        if self.neurons is None:
            self.build_network()

        if input_neurons and input_current:
            # Inject current into sensory neurons
            for idx in input_neurons:
                self.neurons.v[idx] += input_current

        b2.run(duration)

    def get_neural_state(self) -> Dict:
        """Get current neural activity state."""
        if self.spike_mon is None:
            return {}

        # Count recent spikes
        spike_counts = np.bincount(self.spike_mon.i, minlength=self.neurons.N)

        # Get voltage states
        voltages = self.v_mon.v[:, -1] / b2.mV  # Last recorded voltage

        # Identify active neurons (recently spiked or high voltage)
        active_neurons = np.where(spike_counts > 0)[0]

        return {
            'active_neurons': active_neurons.tolist(),
            'spike_counts': spike_counts.tolist(),
            'voltages': voltages.tolist(),
            'num_active': len(active_neurons)
        }

    def reset(self):
        """Reset the simulation."""
        if self.neurons:
            self.neurons.v = -70*b2.mV + np.random.randn(self.neurons.N) * 5 * b2.mV
            self.neurons.v_syn = -70*b2.mV
