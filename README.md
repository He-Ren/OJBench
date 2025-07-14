# OJBench
Official repository for the paper [OJBench: A Competition Level Code Benchmark For Large Language Models](https://arxiv.org/pdf/2506.16395)


## 📘 Introduction

**OJBench** is a comprehensive and challenging benchmark designed to evaluate the code reasoning capabilities of large language models (LLMs) at the competition level. Our dataset focuses exclusively on human programming contests and comprises 232 rigorously-selected competition problems sourced from **China’s National Olympiad in Informatics (NOI)** and the **International Collegiate Programming Contest (ICPC)**. Each problem is meticulously categorized into three difficulty levels—**Easy**, **Medium**, and **Hard**—based on contestant votes and real-world submission data. OJBench supports bilingual evaluation in both **Python** and **C++**, enabling a broad and realistic assessment. We benchmark a wide range of models on OJBench, spanning both **open-source and closed-source**, **reasoning and non-reasoning** types, with sizes ranging from **7B to 671B** parameters.


## 🔥News

- *2025-7*: We have open-sourced our evaluation code and are continually improving it.

- *2025-6*: We have released the OJBench dataset and our paper.


## 📊 Key Findings: Performance of State-of-the-Art Models

> ⚠️ **State-of-the-Art Models Struggle**  
> Even advanced reasoning-oriented models, such as o4-mini and Gemini-2.5-pro-exp, struggle with highly challenging competition-level problems.

> 📈 **Reasoning Models Outperform**  
> Reasoning-oriented models significantly outperformed non-reasoning-oriented models in competitive coding tasks.

> 🔄 **Open-Source vs Closed-Source Gap**  
> Open-source models were observed to still lag behind closed-source models in terms of code reasoning ability.

> ⚡ **C++ Performance Advantage**  
> For most long-chain-of-thought (CoT) models, using C++ resulted in better performance compared to Python.

> 🛠️ **Feedback Utilization**  
> Models are capable of leveraging feedback from the code execution environment to refine their erroneous solutions.

> 📄 **For More Details**  
> Please refer to the full paper for experimental design, evaluation metrics, and comprehensive analysis.

## 🧰 Prerequisites

Before installing OJBench, make sure your system has the following tools installed:

* **C++17-compatible compiler**, such as `g++` version **7.0 or later**
* **PyPy3 interpreter**

You can check their versions using:

```bash
g++ --version
pypy3 --version
```

## 💾 Installation

### 1. Install DMOJ

Clone the DMOJ repository, check out a specific commit, and install it:

```bash
git clone https://github.com/DMOJ/judge-server.git
cd judge-server
git checkout f098cd3a49a60186d1fadde5132329ec5f4f2213
pip install .
cd ..
```

> *Tip: You can install in editable mode with `pip install -e .` during development.*

---

### 2. Clone and Configure OJBench

Clone the OJBench repository:

```bash
git clone git@github.com:He-Ren/OJBench.git
```

#### Runtime Configuration

OJBench uses a runtime configuration file to locate these tools. Open:

```
OJBench/ojbench/runtime.yaml
```

It should look like this by default:

```yaml
g++17: /usr/bin/g++
pypy3: /usr/bin/pypy3
```

Update these paths to point to the actual locations of `g++` and `pypy3` on your system.

To find their paths, run:

```bash
which g++
which pypy3
```

#### Install OJBench

After configuring paths, install the library in editable mode:

```bash
pip install -e OJBench
```

> 📁 Make sure you're in the parent directory of `OJBench` when running this command.

---

### 3. Download Test Data

Test inputs are hosted on Hugging Face:
[https://huggingface.co/datasets/He-Ren/OJBench\_testdata](https://huggingface.co/datasets/He-Ren/OJBench_testdata)

If you don't have Git LFS, install it first:

```bash
git lfs install
```

Then clone the dataset:

```bash
git clone https://huggingface.co/datasets/He-Ren/OJBench_testdata
```

The data is structured as follows:

```
OJBench_testdata/
├── ICPC/
├── NOI/
└── prompts/
    └── full.jsonl
```

* `ICPC/` and `NOI/` contain the test cases.
* `prompts/full.jsonl` contains model prompts for all tasks. These prompts include task descriptions as well as constraints on the format of the model's response.

---

## Generating Model Responses

The `full.jsonl` file contains one prompt per line, each formatted as a JSON object with the following fields:

* `id`: Unique problem ID
* `prompt`: The text prompt to provide to the model
* `dataset`: `"ICPC"` or `"NOI"`
* `language`: `"cpp"` or `"python"`
* `difficulty`: `"easy"`, `"medium"`, or `"hard"`

Each problem has both a C++ and Python version.

You should generate a new `.jsonl` file with all of the above fields, and add:

* `content`: A string containing the model's full response

> **Note**: If your model response follows the format given in the prompt, the library can extract the code automatically. You do **not** need to parse it manually.

Example output:

```json
{"id": 1000, "prompt": "...", "dataset": "NOI", "language": "cpp", "difficulty": "hard", "content": "Here is the code: ..."}
{"id": 1001, "prompt": "...", "dataset": "ICPC", "language": "python", "difficulty": "easy", "content": "The server is busy. Please try again later."}
```

---

## 📚 API

### `init(problem_dirs, config_path=..., runtime_path=..., compile_lock_path=...) -> None`

Initializes the judging environment. This function must be called **before** any judging operations.

It sets up the internal configuration, compiler/runtime paths, and compilation lock required for running tests. Only `problem_dirs` is mandatory; the other arguments have reasonable defaults and typically do not need to be modified.

#### Parameters:

* **`problem_dirs`** (`Union[str, Path, Iterable[Union[str, Path]]]`):
  A path or list of paths pointing to problem directories.

* **`config_path`** (`str | Path`, optional):
  Path to the internal configuration file (`config.yaml`).
  Defaults to the built-in config file in the `ojbench` package.

* **`runtime_path`** (`str | Path`, optional):
  Path to the runtime definition file (`runtime.yaml`).
  Make sure this file reflects the actual paths to compilers/interpreters on your machine.
  Defaults to `ojbench/runtime.yaml`.

* **`compile_lock_path`** (`str | Path`, optional):
  Path to a lock file used to synchronize compilation steps between parallel workers.
  Defaults to the built-in file in the `ojbench` package.

#### Example:

```python
from pathlib import Path
import ojbench

ojbench.init(problem_dirs=[
    Path('OJBench_testdata/NOI'),
    Path('OJBench_testdata/ICPC'),
])
```

> This function only needs to be called once at the start of your evaluation script.

---

### `judge_jsonl(input_path, output_path=None, num_workers=16, worker_log_path=None, identifier=None) -> List[Dict]`

Evaluates a `.jsonl` file of model-generated answers and returns the judging results.

This function reads the input JSONL file, where each line represents model response of a task. It performs automatic code extraction and judging, then returns a list of result dictionaries.

If `output_path` is specified, the results are also saved to that file in `.jsonl` format.

#### Input Format

Each line in the input file must be a JSON object with the following keys:

* `id`: Problem ID
* `content`: The model’s response string

> The library will extract code from `content` automatically.

#### Output Format

Each output dictionary contains:

* All original fields (`id`, `content`, etc.)
* `verdict`: Final verdict string (e.g., `"AC"`, `"WA"`, `"RE"`)
* `is_passed`: Boolean indicating whether `verdict == "AC"`
* `detailed_results`: Per-testcase judging results, including verdict and message for each test
* `1/8verdict`, `1/4verdict`, `1/2verdict`: Verdicts computed using only the first 1/8, 1/4, and 1/2 of testcases, respectively
* `1/8is_passed`, `1/4is_passed`, `1/2is_passed`: Corresponding boolean pass flags

> These partial verdicts are useful for progressive evaluation and analysis of model performance.

#### Parameters

* **`input_path`** (`str | Path`):
  Path to the input `.jsonl` file containing model's response.

* **`output_path`** (`str | Path | None`, default: `None`):
  Path to save the judged results as a `.jsonl` file.
  If `None`, the results are not written to disk, only returned.

* **`num_workers`** (`int`, default: `16`):
  Number of parallel processes used for judging.
  Adjust this based on available CPU cores and memory.

* **`worker_log_path`** (`str | Path | None`, default: `None`):
  Directory where each worker will write logs.
  If `None`, logs are suppressed (redirected to `/dev/null`).

* **`identifier`** (`str | None`, default: `None`):
  Optional identifier string shown in logs, useful for debugging or labeling experiments.

#### Example

```python
ojbench.judge_jsonl(
    input_path="model_response.jsonl",
    output_path="judged.jsonl",
    num_workers=8,
    worker_log_path="logs/",
    identifier="run1"
)
```

---

### `judge_jsonl_data(input, num_workers=16, worker_log_path=None, identifier=None) -> List[Dict]`

Judges a list of model-generated responses (in memory) and returns the evaluation results.

This function is equivalent to `judge_jsonl`, but instead of reading from a file, it accepts a list of dictionaries directly.

The input and output formats are identical to those of `judge_jsonl`.

#### Parameters

* **`input`** (`List[Dict]`):
  A list of model responses, each in the same format as a single line from a `.jsonl` input file.

* **`num_workers`** (`int`, default: `16`):
  Number of parallel worker processes used for judging.
  Adjust this based on system resources.

* **`worker_log_path`** (`str | Path | None`, default: `None`):
  Directory where each worker writes its log.
  If `None`, logs are discarded (written to `/dev/null`).

* **`identifier`** (`str | None`, default: `None`):
  Optional identifier string shown in worker logs, useful for debugging or labeling experiments.

#### Example

```python
responses = [
    {
        "id": 1234,
        "prompt": "Write a function to add two integers...",
        "dataset": "ICPC",
        "language": "python",
        "difficulty": "easy",
        "content": "Here is the code:\n```python\ndef add(a, b): return a + b\n```"
    }
]
results = ojbench.judge_jsonl_data(responses, num_workers=4)
```

---

## 📝 Example

Suppose your directory structure looks like:

```
OJBench_testdata/
├── ICPC/
├── NOI/
└── prompts/
    └── full.jsonl
test.py
model_response.jsonl
```

Then your test script `test.py` can look like:

```python
import ojbench
from pathlib import Path

ojbench.init(problem_dirs=[
    Path('OJBench_testdata/NOI'),
    Path('OJBench_testdata/ICPC'),
])

ojbench.judge_jsonl('model_response.jsonl', 'judged.jsonl')
```

After running:

```bash
python test.py
```

You will get `judged.jsonl` in the current directory with the results.

---

## 💬 Citation
If you find our work interesting and meaningful, welcome to give a 🌟 to our repo and cite our paper.
```
@misc{wang2025ojbenchcompetitionlevelcode,
      title={OJBench: A Competition Level Code Benchmark For Large Language Models}, 
      author={Zhexu Wang and Yiping Liu and Yejie Wang and Wenyang He and Bofei Gao and Muxi Diao and Yanxu Chen and Kelin Fu and Flood Sung and Zhilin Yang and Tianyu Liu and Weiran Xu},
      year={2025},
      eprint={2506.16395},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2506.16395}, 
}
```