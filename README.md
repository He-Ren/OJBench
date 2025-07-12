## Introduction

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

### Running Judging on JSONL Input

To evaluate submissions in batches, call the function `judge_jsonl_data`.

```python
def judge_jsonl_data(input: List[Dict], num_workers: int = 16, worker_log_path: Union[str, Path, None] = None, identifier: Union[str, None] = None) -> List[Dict]:
```

Parameters:
- `input`: the 
