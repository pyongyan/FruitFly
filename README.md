# Fruit Fly Agent 🪰

An AI agent powered by the **actual fruit fly connectome** (real neurobiology) that thinks and talks to you via Claude CLI.

## Concept

The fruit fly (*Drosophila melanogaster*) has a fully mapped connectome: ~3,000 neurons and ~500,000 synapses. This project simulates that real brain and connects it to Claude AI to generate the fly's thoughts.

**How it works:**
1. You ask the fly a question or describe a scenario
2. The connectome simulator processes sensory input → neural activity cascade
3. The neural interpreter extracts what's happening in the fly's "brain"
4. Claude CLI interprets the neural state and generates the fly's response
5. You see the fly thinking in real-time

## Architecture

```
User Input (Terminal)
    ↓
Terminal UI (Rich)
    ↓
Neural Interpreter
    ↓
Connectome Simulator (brian2)
    ↓
Claude CLI Integration
    ↓
Fly's Response (streamed)
```

## Project Structure

```
FruitFly/
├── src/
│   ├── connectome_simulator.py    # Load & simulate fruit fly brain
│   ├── neural_interpreter.py      # Extract signals from neural activity
│   ├── claude_integration.py      # Claude CLI piping
│   ├── terminal_ui.py             # Terminal interface (Rich)
│   └── main.py                    # Entry point
├── data/
│   └── connectome/                # FlyEM connectome data
├── requirements.txt               # Python dependencies
└── README.md                       # This file
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download connectome data (automatic on first run)
python src/main.py

# Interact with the fly
# Follow terminal prompts
```

## Components

### Connectome Simulator
- Loads real fruit fly connectome from FlyEM dataset
- Simulates neuron dynamics using brian2
- Processes sensory inputs → neural cascades
- Generates neural activation patterns

### Neural Interpreter
- Monitors ~3,000 neurons in real-time
- Extracts key signals: motor activity, sensory input, internal state
- Generates English descriptions of brain activity
- Feeds summaries to Claude

### Claude Integration
- Pipes neural state + user input to Claude CLI
- Captures streaming responses
- Formats fly's thoughts in real-time

### Terminal UI
- Displays current neural state
- Shows fly's thoughts as they're generated
- Accepts user input
- Continuous interaction loop

## Status

🚀 **In Development** - Building now!

## References

- **FlyEM Connectome:** https://www.janelia.org/project-team/flyem
- **Fruit Fly Neuroscience:** https://fruit-fly-brain.org
- **Brian2:** https://brian2.readthedocs.io/

---

Built with Claude Code 🤖
