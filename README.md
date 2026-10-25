# TreeMind

This repository contains the implementation of **TreeMind: Automatically Reproducing Android Bug Reports via LLM-empowered Monte Carlo Tree Search**, accepted to **ACM Transactions on Software Engineering and Methodology (TOSEM)**.

TreeMind combines large language models (LLMs) with Monte Carlo Tree Search (MCTS) to reproduce Android app crashes from textual bug reports. It uses two agents: an **Expander** proposes candidate interactions based on the bug report, UI hierarchy, screenshots, and exploration history; a **Simulator** evaluates the resulting states to guide subsequent exploration.

This release provides the source code and prompts. Experimental datasets, per-case results, and execution logs are not included.

## Requirements

- Python and the dependencies listed in `TreeMind/requirements.txt`.
- Android SDK Platform-Tools, with `adb` available on `PATH`.
- A running Android emulator or connected device with the target app installed.
- Access to a vision-capable model through an OpenAI-compatible or Qwen endpoint.
- A local text file containing the bug report to reproduce.

## Running the tool

### 1. Install dependencies

```bash
git clone https://github.com/Vermouth-hub/TreeMind.git
cd TreeMind
python -m venv .venv
```

Activate the environment:

```bash
# Linux / macOS
source .venv/bin/activate
```

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install the dependencies and enter the implementation directory:

```bash
python -m pip install -r TreeMind/requirements.txt
cd TreeMind
```

Run the following commands from this inner `TreeMind/` directory, since configuration and prompt paths are resolved relative to the working directory.

### 2. Configure the model

Edit `config.yaml` to select your provider, endpoint, and model. The default provider is `OpenAI`, with `OPENAI_API_MODEL: "gpt-4o"` and `TEMPERATURE: 0.3`. Choose a model that supports image inputs and is available through your endpoint.

Set your API key in the environment:

```bash
# Linux / macOS
export OPENAI_API_KEY="your-api-key"
```

```powershell
# Windows PowerShell
$env:OPENAI_API_KEY = "your-api-key"
```

For Qwen, set `MODEL: "Qwen"`, configure `QWEN_API_BASE` and `QWEN_API_MODEL`, and provide `QWEN_API_KEY` or `DASHSCOPE_API_KEY` in the environment. Values explicitly added to `config.yaml` override environment variables; keep API keys out of committed files.

### 3. Prepare the app

Verify the device connection:

```bash
adb devices
```

Install and open the target app, complete any required setup, and navigate to the intended initial state. Keep only one device connected, as some app restart commands currently use `adb` without a device selector.

### 4. Start reproduction

```bash
python reproduction.py <app_name> <report_file_path> [device_port]
```

For example, replacing the report path with your own file:

```bash
python reproduction.py my_app /absolute/path/to/bug_report.txt emulator-5554
```

- `app_name`: a label used for the output directory. The target package is obtained from the foreground app.
- `report_file_path`: the path to the textual bug report.
- `device_port`: the ADB device serial; defaults to `emulator-5554`.

To display the command-line usage:

```bash
python reproduction.py --help
```

## Outputs

TreeMind writes screenshots and `record.txt` beneath `apps/<app_name>/` in the implementation directory. On success, the record contains the action sequence; when the search is exhausted without success, it contains an empty record. Agent responses and execution diagnostics are printed to the console.

Save each run separately if you need to retain its results: running again with the same app name overwrites `record.txt`. Review the detected crash and action sequence against the target bug report. The entry point performs one search and does not implement the paper's five-run evaluation orchestration or enforce its 30-minute time limit.

## Code structure

| File | Purpose |
| --- | --- |
| `TreeMind/reproduction.py` | Main reproduction loop and command-line entry point |
| `TreeMind/mcts.py` | Search tree, branch selection, expansion, and backpropagation |
| `TreeMind/handler.py` | Agent orchestration, candidate action parsing, and simulation scoring |
| `TreeMind/controller.py` | UI hierarchy processing and device interaction |
| `TreeMind/ElementTree_hepler.py` | UI hierarchy helpers |
| `TreeMind/model.py` | OpenAI and Qwen model adapters |
| `TreeMind/utils.py` | Configuration loading, app restart, replay, and crash detection |
| `TreeMind/config.yaml` | Provider, model, temperature, and retry settings |
| `TreeMind/prompts/` | Expander and Simulator prompts |

## Paper

Zhengyu Chen, Zhaoyi Meng, Wenxiang Zhao, Wansen Wang, Wenchao Huang, Jie Cui, Hong Zhong, and Yan Xiong. **TreeMind: Automatically Reproducing Android Bug Reports via LLM-empowered Monte Carlo Tree Search.** Accepted to *ACM Transactions on Software Engineering and Methodology (TOSEM)*.

## Acknowledgments

TreeMind builds on UI processing ideas and implementation from [ReBL](https://github.com/datareviewtest/ReBL), and uses [UIAutomator2](https://github.com/openatx/uiautomator2) for Android device interaction.
