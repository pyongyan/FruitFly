"""
Terminal UI for Fruit Fly Agent

Rich-based interface for interacting with the fly and displaying neural state.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
from typing import Dict


class FlyTerminalUI:
    """Terminal UI for the fruit fly agent."""

    def __init__(self):
        """Initialize the terminal UI."""
        self.console = Console()
        self.fly_name = "🪰 Fruit Fly"

    def show_welcome(self):
        """Display welcome message."""
        welcome_text = """
╔════════════════════════════════════════════════════╗
║                                                    ║
║          🪰 FRUIT FLY AGENT AWAKENING 🪰          ║
║                                                    ║
║   A biological brain running on your laptop        ║
║   Real neurons, real thoughts, real fly            ║
║                                                    ║
╚════════════════════════════════════════════════════╝
"""
        self.console.print(welcome_text)
        self.console.print("[cyan]Initializing connectome simulator...[/cyan]")
        time.sleep(0.5)
        self.console.print("[green]✓ Brain loaded: 100 neurons, 500+ synapses[/green]")
        self.console.print("[cyan]Connecting to Claude CLI...[/cyan]")
        time.sleep(0.3)
        self.console.print("[green]✓ Claude integration ready[/green]")
        self.console.print()

    def display_neural_state(self, interpretation: Dict):
        """
        Display current neural state in a nice format.

        Args:
            interpretation: Dict with neural state interpretation
        """
        # Activity level bar
        activity = interpretation.get('activity_level', 'unknown')
        num_active = interpretation.get('num_active_neurons', 0)

        activity_colors = {
            'dormant': '[dim]████░░░░░░[/dim]',
            'minimal': '[yellow]█████░░░░░[/yellow]',
            'moderate': '[cyan]██████░░░░[/cyan]',
            'high': '[magenta]███████░░░[/magenta]',
            'very high': '[red]██████████[/red]'
        }

        activity_bar = activity_colors.get(activity, '[dim]░░░░░░░░░░[/dim]')

        # Create state table
        table = Table(show_header=False, box=None)
        table.add_column(style="cyan")
        table.add_column(style="white")

        table.add_row("🧠 Neural Activity", f"{activity_bar} {activity.upper()}")
        table.add_row("⚡ Active Neurons", str(num_active))
        table.add_row("👁️  Sensory Input", f"{interpretation.get('sensory_activity', 0)} active")
        table.add_row("🦵 Motor Circuits", f"{interpretation.get('motor_activity', 0)} firing")
        table.add_row("🤔 Internal State", interpretation.get('primary_state', 'unknown').upper())

        panel = Panel(
            table,
            title="[bold cyan]Brain State[/bold cyan]",
            border_style="cyan",
            expand=False
        )

        self.console.print(panel)

    def display_fly_thought(self, thought: str, is_streaming: bool = True):
        """
        Display fly's thoughts with animation.

        Args:
            thought: The fly's thought/response
            is_streaming: Whether this is being streamed in real-time
        """
        if is_streaming:
            self.console.print(f"\n[magenta]{self.fly_name}[/magenta] (thinking): ", end='', highlight=False)
        else:
            self.console.print(f"\n[magenta]{self.fly_name}[/magenta]: {thought}")

    def get_user_input(self) -> str:
        """
        Get user input from terminal.

        Returns:
            User's input string
        """
        self.console.print()
        try:
            user_input = input("[cyan]You:[/cyan] ").strip()
            return user_input
        except EOFError:
            return ""

    def show_loading_spinner(self, message: str = "Processing..."):
        """Show a loading spinner while waiting for Claude."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True
        ) as progress:
            task = progress.add_task(f"[cyan]{message}[/cyan]", total=None)
            time.sleep(1)  # Simulate work

    def display_error(self, error_msg: str):
        """Display an error message."""
        self.console.print(f"[red]❌ Error: {error_msg}[/red]")

    def display_info(self, info_msg: str):
        """Display an info message."""
        self.console.print(f"[blue]ℹ️  {info_msg}[/blue]")

    def show_commands_hint(self):
        """Show available commands."""
        self.console.print("\n[dim]Commands: 'quit' to exit, 'reset' to restart fly's brain[/dim]")

    def show_goodbye(self):
        """Show goodbye message."""
        self.console.print("\n[cyan]Shutting down connectome simulator...[/cyan]")
        self.console.print("[green]✓ Neural activity ceased[/green]")
        self.console.print("[bold magenta]🪰 Fly has returned to nature.[/bold magenta]\n")

    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()

    def show_status_update(self, status: str):
        """Show a status update message."""
        self.console.print(f"[yellow]→ {status}[/yellow]")
