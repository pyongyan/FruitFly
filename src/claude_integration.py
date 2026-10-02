"""
Claude CLI Integration

Pipes neural state to Claude CLI and captures the fly's thoughts/responses.
"""

import subprocess
import sys
from typing import Generator
import shutil


class ClaudeIntegration:
    """Integrates with Claude CLI to generate fly's responses."""

    def __init__(self):
        """Initialize Claude integration."""
        self.claude_available = self._check_claude_available()

    def _check_claude_available(self) -> bool:
        """Check if Claude CLI is installed and available."""
        result = shutil.which('claude')
        return result is not None

    def generate_fly_response(self, neural_context: str, user_input: str) -> Generator[str, None, None]:
        """
        Generate fly's response by piping to Claude CLI.

        Args:
            neural_context: Description of current brain state
            user_input: User's input/question to the fly

        Yields:
            Streamed response text from Claude
        """
        if not self.claude_available:
            yield "⚠️  Claude CLI not found. Make sure you have: `claude --version`\n"
            yield self._generate_fallback_response(neural_context, user_input)
            return

        prompt = self._construct_prompt(neural_context, user_input)

        try:
            process = subprocess.Popen(
                ['claude'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Send prompt and close stdin to signal end of input
            process.stdin.write(prompt)
            process.stdin.close()

            # Stream output line by line
            for line in process.stdout:
                yield line.rstrip('\n')

            # Wait for process to complete
            process.wait()

            # Check for errors
            if process.returncode != 0:
                stderr = process.stderr.read()
                if stderr:
                    yield f"\n⚠️  Claude error: {stderr}"

        except Exception as e:
            yield f"❌ Error communicating with Claude: {str(e)}\n"
            yield self._generate_fallback_response(neural_context, user_input)

    def _construct_prompt(self, neural_context: str, user_input: str) -> str:
        """Construct the prompt to send to Claude."""
        prompt = f"""You are a fruit fly (Drosophila melanogaster). You have a real biological brain (connectome) running in a computer simulation. You experience thoughts, sensations, and drives based on your neural activity.

Current Brain State:
{neural_context}

The human just said to you:
"{user_input}"

Based on your current brain state and neural activity, respond naturally as a fly would. Express your thoughts, sensations, drives, and reactions. Be authentic to what your brain is doing right now. You may express confusion, curiosity, hunger, the desire to move, or any other fly-like drives. Keep responses concise (1-3 sentences)."""

        return prompt

    def _generate_fallback_response(self, neural_context: str, user_input: str) -> str:
        """Generate a response without Claude (fallback)."""
        # Simple rule-based fallback for when Claude isn't available
        if "how" in user_input.lower():
            return "My neural circuits buzz with questions... I process but cannot answer."
        elif "move" in user_input.lower() or "go" in user_input.lower():
            return "Yes! My motor neurons are firing - I need to MOVE!"
        elif "food" in user_input.lower() or "eat" in user_input.lower():
            return "Food? My sensory neurons are already searching... where is it?"
        elif "sleep" in user_input.lower():
            return "Rest... yes. My interneurons are tiring."
        else:
            return "My brain processes your words, but I cannot yet formulate meaning..."

    def test_connection(self) -> bool:
        """Test if Claude CLI is working properly."""
        if not self.claude_available:
            return False

        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Claude test failed: {e}")
            return False

    def stream_response(self, response_generator: Generator[str, None, None]) -> None:
        """
        Display streamed response in real-time.

        Args:
            response_generator: Generator yielding response chunks
        """
        for chunk in response_generator:
            print(chunk, end='', flush=True)
        print()  # New line after response
