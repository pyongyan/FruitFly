"""
Fruit Fly Agent - Main Entry Point

Orchestrates connectome simulator, neural interpreter, Claude integration, and terminal UI.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from connectome_simulator import ConnectomeSimulator
from neural_interpreter import NeuralInterpreter
from claude_integration import ClaudeIntegration
from terminal_ui import FlyTerminalUI


class FruitFlyAgent:
    """Main orchestrator for the fruit fly agent."""

    def __init__(self):
        """Initialize all components."""
        self.ui = FlyTerminalUI()
        self.simulator = None
        self.interpreter = None
        self.claude = None
        self.running = True

    def initialize(self):
        """Initialize all components."""
        self.ui.show_welcome()

        try:
            # Initialize simulator
            self.ui.show_status_update("Loading connectome...")
            self.simulator = ConnectomeSimulator()
            self.simulator.load_connectome()
            self.simulator.build_network()

            # Initialize interpreter
            self.ui.show_status_update("Initializing neural interpreter...")
            self.interpreter = NeuralInterpreter()

            # Initialize Claude integration
            self.ui.show_status_update("Checking Claude CLI connection...")
            self.claude = ClaudeIntegration()
            if not self.claude.test_connection():
                self.ui.display_error("Claude CLI not available - using fallback mode")
            else:
                self.ui.display_info("Claude CLI connected successfully!")

            self.ui.show_commands_hint()
            self.ui.console.print()

        except Exception as e:
            self.ui.display_error(f"Initialization failed: {str(e)}")
            raise

    def process_sensory_input(self, user_input: str):
        """
        Process user input as sensory stimulus.

        Args:
            user_input: The user's input string
        """
        # Convert text to sensory activation (simplified)
        # In real version, would use NLP to map input to neuron activation
        num_input_neurons = min(len(user_input), 10)

        # Activate some sensory neurons based on input length
        self.simulator.run_simulation(
            duration=0.1,
            input_neurons=list(range(min(num_input_neurons, 20))),
            input_current=5
        )

    def run_interaction_loop(self):
        """Main interaction loop."""
        self.ui.show_status_update("Brain is alive. Talk to the fly!")
        self.ui.console.print()

        iteration = 0

        while self.running:
            try:
                # Get current neural state
                neural_state = self.simulator.get_neural_state()
                interpretation = self.interpreter.interpret_state(neural_state)

                # Display neural state
                self.ui.display_neural_state(interpretation)

                # Get user input
                user_input = self.ui.get_user_input()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.lower() == 'quit':
                    self.running = False
                    break
                elif user_input.lower() == 'reset':
                    self.ui.show_status_update("Resetting fly's brain...")
                    self.simulator.reset()
                    continue
                elif user_input.lower() == 'status':
                    continue

                # Process input as sensory stimulus
                self.ui.show_status_update("Fly processing your words...")
                self.process_sensory_input(user_input)

                # Get updated neural state
                neural_state = self.simulator.get_neural_state()
                interpretation = self.interpreter.interpret_state(neural_state)
                neural_context = self.interpreter.generate_prompt_context(neural_state)

                # Generate fly's response via Claude
                self.ui.show_status_update("Fly is thinking...")
                self.ui.display_fly_thought("", is_streaming=True)

                response_generator = self.claude.generate_fly_response(neural_context, user_input)
                self.claude.stream_response(response_generator)

                iteration += 1

            except KeyboardInterrupt:
                self.ui.console.print("\n[yellow]Interrupted by user[/yellow]")
                self.running = False
                break
            except Exception as e:
                self.ui.display_error(f"Error in interaction loop: {str(e)}")
                continue

    def shutdown(self):
        """Shutdown the fly agent."""
        self.ui.show_goodbye()


def main():
    """Main entry point."""
    fly = FruitFlyAgent()

    try:
        fly.initialize()
        fly.run_interaction_loop()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        fly.shutdown()


if __name__ == "__main__":
    main()
