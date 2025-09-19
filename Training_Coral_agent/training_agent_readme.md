## [Training Agent](https://github.com/Coral-Protocol/Training-Coral-Agent)

The Training Agent is an open-source agent designed for ML model training script generation.

## Responsibility
The Training Agent is an open-source agent designed for generating machine learning training scripts and code. It provides ready-to-use Python code with minimal dependencies for training selected ML models using a multi-agent architecture.

## Details
- **Framework**: LangChain
- **Tools used**: Mistral API, Coral Server Tools
- **AI model**: Mistral AI (mistral-small-latest)
- **Date added**: September 17, 2025
- **License**: MIT

## Setup the Agent

### 1. Clone & Install Dependencies

<details>

Ensure that the [Coral Server](https://github.com/Coral-Protocol/coral-server) is running on your system. If you are trying to run Training agent and require an input, you can either create your agent which communicates on the coral server or run and register the [Interface Agent](https://github.com/Coral-Protocol/Coral-Interface-Agent) on the Coral Server

```bash
# In a new terminal clone the repository:
git clone https://github.com/Coral-Protocol/Training-Coral-Agent.git

# Navigate to the project directory:
cd Training-Coral-Agent

# Download and run the UV installer, setting the installation directory to the current one
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(pwd) sh

# Create a virtual environment named `.venv` using UV
uv venv .venv

# Activate the virtual environment
source .venv/bin/activate

# install uv
pip install uv

# Install dependencies from `pyproject.toml` using `uv`:
uv sync
```

</details>

### 2. Configure Environment Variables

<details>

Get the API Key:
[Mistral AI](https://console.mistral.ai/) || 
[OpenAI](https://platform.openai.com/api-keys)

```bash
# Create .env file in project root
cp -r .env_sample .env
```

Check if the .env file has correct URL for Coral Server and adjust the parameters accordingly.

</details>

## Run the Agent

You can run in either of the below modes to get your system running.  

- The Executable Model is part of the Coral Protocol Orchestrator which works with [Coral Studio UI](https://github.com/Coral-Protocol/coral-studio).  
- The Dev Mode allows the Coral Server and all agents to be separately running on each terminal without UI support.  

### 1. Executable Mode

<details>

For Linux or MAC:

```bash
registry:
  # ... your other agents
  training_agent:
    options:
      - name: "MODEL_API_KEY"
        type: "string"
        description: "API key for the model service"
      - name: "MISTRAL_API_KEY"
        type: "string"
        description: "Mistral API KEY for the service"
      - name: "MODEL_NAME"
        type: "string"
        description: "What model to use (e.g 'mistral-small-latest')"
        default: "mistral-small-latest"
      - name: "MODEL_PROVIDER"
        type: "string"
        description: "What model provider to use (e.g 'mistral', etc)"
        default: "mistral"
      - name: "MODEL_MAX_TOKENS"
        type: "string"
        description: "Max tokens to use"
        default: "1024"
      - name: "MODEL_TEMPERATURE"
        type: "string"
        description: "What model temperature to use"
        default: "0.2"
      - name: "MISTRAL_API_URL"
        type: "string"
        description: "Mistral API URL"
        default: "https://api.mistral.ai"
      - name: "MISTRAL_MODEL"
        type: "string"
        description: "Mistral model name"
        default: "mistral-small-latest"
    runtime:
      type: "executable"
      command: ["bash", "-c", "<replace with path to this agent>/run_agent.sh main.py"]
      environment:
        - option: "MODEL_API_KEY"
        - option: "MISTRAL_API_KEY"
        - option: "MODEL_NAME"
        - option: "MODEL_PROVIDER"
        - option: "MODEL_MAX_TOKENS"
        - option: "MODEL_TEMPERATURE"
        - option: "MISTRAL_API_URL"
        - option: "MISTRAL_MODEL"
```

</details>

### 2. Dev Mode

<details>

```bash
# Run the agent using `uv`:
uv run python main.py
```

</details>

## Example

<details>

```bash
# Input:
Generate training code for Random Forest model on student grades dataset

#Output:
```python
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load your dataset
# df = pd.read_csv('student_grades.csv')
# X = df[['hours_studied', 'attendance_percentage']]
# y = df['final_grade']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, predictions)
print(f"Mean Squared Error: {mse}")
```

Usage: Replace the commented data loading section with your actual dataset path.
```

</details>

### Creator Details
- **Name**: ML Mentor System
- **Affiliation**: Coral Protocol
- **Contact**: [Discord](https://discord.com/invite/Xjm892dtt3)
