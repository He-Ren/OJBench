# OJBench
Official repository for the paper [OJBench: A Competition Level Code Benchmark For Large Language Models](https://arxiv.org/pdf/2506.16395)


## Introduction
OJBench is a comprehensive and challenging benchmark specifically designed to assess LLMs’ code-reasoning capabilities at the competition level. Our dataset focuses exclusively on human programming contests and comprises 232 rigorously-selected competition problems sourced from China’s National Olympiad in Informatics (NOI) and the International Collegiate Programming Contest (ICPC). These problems are meticulously classified into three difficulty tiers-Easy, Medium, and Hard—derived from contestant voting and real-world submission statistics, and span across bilingual evaluation in both Python and C++.We evaluate numerous models on OJBench, covering open-source/closed-source, reasoning/non-reasoning, 7 B–671 B models.



## 🔥News

- *2025-7*: We have open-sourced our evaluation code and are continually improving it.

- *2025-6*: We have released the OJBench dataset and our paper.


## Key Findings: Performance of State-of-the-Art Models

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

### Prerequisites

OJBench is a benchmark designed to evaluate a model's ability to solve competitive programming tasks.

## Installation

### 1. Install DMOJ

Clone the DMOJ repository, check out the specific commit, and install it:

```bash
git clone https://github.com/DMOJ/judge-server.git
cd judge-server
git checkout f098cd3a49a60186d1fadde5132329ec5f4f2213
pip install .
cd ..
```

### 2. Install OJBench

Clone the OJBench library:

```bash
git clone git@github.com:He-Ren/OJBench.git
```

Next, open `OJBench/ojbench/runtime.yaml` to verify the paths for `g++17` and `pypy3`. By default, these are set as follows:
```yaml
g++17: /usr/bin/g++
pypy3: /usr/bin/pypy3
```
You can modify this file to change their paths.

Install OJBench:

``` bash
pip install -e OJBench
```

### 3. Download Test Data

Test inputs are hosted on Hugging Face under `https://huggingface.co/He-Ren/OJBench_testdata`. You can clone it with Git LFS.

If you don't have Git LFS installed, run `git lfs install` first.

Run:

```bash
git clone https://huggingface.co/He-Ren/OJBench_testdata
```

The test data has the following structure:
```
OJBench_testdata/
├── ICPC/
├── NOI/
└── prompts/
    └── full.jsonl
```
Here, `ICPC/` and `NOI/` contain test data for ICPC and NOI tasks, respectively, and `prompts/full.jsonl` contains prompts for those tasks.

## Generate answer

`OJBench_testdata/prompts/full.jsonl` is a `jsonl` file of prompts. Each line of this file is a json structure containing the following fields:
- `prompt`: The prompt you should provide to your model. This prompts contains the problem discription and the language that your model should use to write the code.
- `id`: Problem id.
- `dataset`: `NOI` or `ICPC`.
- `language`: `cpp` or `python`, the same language as in `prompt`.
- `difficulty`: `easy`, `medium` or `hard`, representing the difficulty of this task.

Note that in this file, each problem has both a `cpp` version and a `python` version.

To judge the answer, you should generate a jsonl file, containing **all the fields above**, and also the following key:
- `content`: A string, representing the response of your model.

*Note that, you do not have to extract the code manually from the response. The liabriary will extract it automaticaly if the answer of your model follows the format given by the prompt.*

For example, an answer file might be looking like this:
```json
{"id": 1000, "prompt": "...", "dataset": "NOI", "language": "cpp", "difficulty": "hard", "content": "Here is the code: ..."}
{"id": 1001, "prompt": "...", "dataset": "ICPC", "language": "python", "difficulty": "easy", "content": "The server is busy. Please try again later."}
```

## API

### `def init(problem_dirs, config_path = ..., runtime_path = ..., compile_lock_path = ...) -> None`

Set up the judging environment. Every parameters except `problem_dirs` has a default setting, which usually does not need to be changed. Parameters:
- `problem_dirs`: A list of problem directories.
- `config_path`: Path to the internal config file.
- `runtime_path`: Path to the file that defines runtime commands for each language.
- `compile_lock_path`: Path to a lock file used internally to synchronize compilation processes.

### `def judge_jsonl(input_path, output_path = None, num_worker = 16, worker_log_path = None, identifier = None) -> List[Dict]:`

Judge the answer file. Return the judged result. The result is a jsonl file stored in a list of dictionary. It keeps all the keys in the original answer file, and adds the followings:
- `detailed_results`: The detailed results, including the final verdict, and the verdict and judging message for each test cases.
- `verdict`: A string, representing the judging verdict of your answer.
- `is_passed`: A boolean value, representing if your answer has passed (i.e. if `verdict` is `AC`).
- `1/8verdict`, `1/8is_passed`, `1/4verdict`, `1/4is_passed`, `1/2verdict`, `1/2is_passed`: The same as above, but only keep the first $1/8$, $1/4$ and $1/2$ ratio of test cases, respectively.

The judging will be done is a multiprocess manner. For the details, please see the parameters.

Parameters:
- `input_path`: The path of input file (the answer of the model).
- `output_path`: The path of result. Defaut to `None`. If it is set to `None`, the result will not be written. Note that whenever it is `None` or not, the function will always return the result.
- `num_worker`: The number of worker processes. Defaut to $16$.
- `worker_log_path`: The path where workers print their log. Default to `None`. Note that it should be a path to a **folder** or `None`, if it is `None`, the worker will print their log to `/dev/null`.
- `identifier`: An identifier, just used to be shown in the log. Default to `None`.