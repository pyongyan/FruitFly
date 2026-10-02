"""
Neural State Interpreter

Extracts meaningful signals from connectome activity and generates
English descriptions of the fly's brain state.
"""

import json
from pathlib import Path
from typing import Dict, List
import numpy as np


class NeuralInterpreter:
    """Interprets neural activity and generates descriptive summaries."""

    def __init__(self, connectome_path: str = None):
        """Initialize with connectome for neuron metadata."""
        self.connectome_path = connectome_path or "data/connectome/flyem_connectome.json"
        self.connectome = None
        self.neuron_regions = {}
        self._load_connectome()

    def _load_connectome(self):
        """Load connectome for neuron type information."""
        path = Path(self.connectome_path)
        if path.exists():
            with open(path, 'r') as f:
                self.connectome = json.load(f)
            self._categorize_neurons()

    def _categorize_neurons(self):
        """Categorize neurons by region/type."""
        if not self.connectome:
            return

        for neuron in self.connectome['neurons']:
            neuron_type = neuron.get('type', 'interneuron')
            self.neuron_regions[neuron['id']] = {
                'type': neuron_type,
                'name': neuron.get('name', f'neuron_{neuron["id"]}')
            }

    def interpret_state(self, neural_state: Dict) -> Dict:
        """
        Interpret neural state and generate descriptive summary.

        Args:
            neural_state: Dict with 'active_neurons', 'spike_counts', 'voltages'

        Returns:
            Dict with interpretation summary
        """
        if not neural_state or 'active_neurons' not in neural_state:
            return self._default_interpretation()

        active = neural_state.get('active_neurons', [])
        spike_counts = neural_state.get('spike_counts', [])

        # Categorize activity by neuron type
        sensory_activity = 0
        motor_activity = 0
        interneuron_activity = 0

        for neuron_id in active:
            if neuron_id < len(self.neuron_regions):
                neuron_type = self.neuron_regions.get(neuron_id, {}).get('type', 'interneuron')
                if neuron_type == 'sensory':
                    sensory_activity += 1
                elif neuron_type == 'motor':
                    motor_activity += 1
                else:
                    interneuron_activity += 1

        # Determine overall state
        total_active = len(active)
        activity_level = self._classify_activity(total_active)

        # Generate interpretation
        interpretation = {
            'activity_level': activity_level,
            'num_active_neurons': total_active,
            'sensory_activity': sensory_activity,
            'motor_activity': motor_activity,
            'interneuron_activity': interneuron_activity,
            'primary_state': self._determine_primary_state(
                sensory_activity, motor_activity, interneuron_activity
            ),
            'description': self._generate_description(
                activity_level, sensory_activity, motor_activity, interneuron_activity, total_active
            )
        }

        return interpretation

    def _classify_activity(self, num_active: int) -> str:
        """Classify activity level based on number of active neurons."""
        if num_active == 0:
            return "dormant"
        elif num_active < 5:
            return "minimal"
        elif num_active < 15:
            return "moderate"
        elif num_active < 30:
            return "high"
        else:
            return "very high"

    def _determine_primary_state(self, sensory: int, motor: int, interneuron: int) -> str:
        """Determine primary behavioral state from neural activity."""
        if sensory > motor and sensory > interneuron:
            return "perceiving"
        elif motor > sensory and motor > interneuron:
            return "acting"
        elif interneuron > sensory and interneuron > motor:
            return "thinking"
        else:
            return "processing"

    def _generate_description(self, activity_level: str, sensory: int, motor: int,
                             interneuron: int, total: int) -> str:
        """Generate English description of neural state."""
        descriptions = []

        # Activity level description
        if activity_level == "dormant":
            descriptions.append("My brain is quiet, barely active.")
        elif activity_level == "minimal":
            descriptions.append("I'm mostly resting, just some neurons flickering.")
        elif activity_level == "moderate":
            descriptions.append("I'm awake and processing things.")
        elif activity_level == "high":
            descriptions.append("My brain is buzzing with activity!")
        else:
            descriptions.append("My brain is FIRING ON ALL CYLINDERS!")

        # Sensory description
        if sensory > motor and sensory > 0:
            descriptions.append("I'm picking up sensory information.")
        elif sensory > 0:
            descriptions.append("I'm sensing my environment.")

        # Motor description
        if motor > sensory and motor > 0:
            descriptions.append("My motor circuits are active - I want to move!")
        elif motor > 0:
            descriptions.append("I'm preparing to act.")

        # Internal processing
        if interneuron > 0 and interneuron > total // 3:
            descriptions.append("I'm doing a lot of internal processing.")

        return " ".join(descriptions)

    def _default_interpretation(self) -> Dict:
        """Return default interpretation when no data available."""
        return {
            'activity_level': 'unknown',
            'num_active_neurons': 0,
            'sensory_activity': 0,
            'motor_activity': 0,
            'interneuron_activity': 0,
            'primary_state': 'idle',
            'description': 'My brain is offline or initializing...'
        }

    def generate_prompt_context(self, neural_state: Dict) -> str:
        """
        Generate context string for Claude prompt based on neural state.

        Args:
            neural_state: Dict with neural activity data

        Returns:
            String describing fly's current brain state
        """
        interpretation = self.interpret_state(neural_state)

        context = f"""
Brain State Analysis:
- Activity Level: {interpretation['activity_level']}
- Active Neurons: {interpretation['num_active_neurons']}
- Sensory Input Processing: {'Yes' if interpretation['sensory_activity'] > 0 else 'No'}
- Motor Circuits Engaged: {'Yes' if interpretation['motor_activity'] > 0 else 'No'}
- Internal Processing: {interpretation['interneuron_activity']} interneurons active
- Primary State: {interpretation['primary_state']}

What the Fly Perceives:
{interpretation['description']}
"""
        return context.strip()
