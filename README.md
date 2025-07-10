## Introduction

OJBench is a benchmark designed to evaluate a model's ability to solve competitive programming tasks.

## Installation

### 1. Install DMOJ

Clone the DMOJ repository, check out the specific commit, and install it:

```bash
# Clone the repository
git clone https://github.com/DMOJ/judge-server.git
cd judge-server

# Pin to a known stable version
git checkout f098cd3a49a60186d1fadde5132329ec5f4f2213

# Install into the current Python environment
pip install .
```
### 2. Install OJBench

Clone the OJBench library and install it:

```bash
# Clone the OJBench repository
git clone git@github.com:He-Ren/OJBench.git
cd OJBench
```

Next, open `ojbench/runtime.yaml` to verify the paths for `g++17` and `pypy3`. By default, these are set as follows:
```yaml
g++17: /usr/bin/g++
pypy3: /usr/bin/pypy3
```
You can modify this file to change their paths.

``` bash
# Install into the current Python environment
pip install -e .
```

### 3. Download Test Data

Test inputs are hosted on Hugging Face under `He-Ren/OJBench_testdata`. You can clone with Git LFS.

If you don't have Git LFS installed, run `git lfs install` first.

Run:

```bash
git clone https://huggingface.co/He-Ren/OJBench_testdata
```

## Usage

### Initialization

Use the `init` function to set up the judging environment. Provide one or more problem directories (for example, `data/NOI` and `data/ICPC`).

### Running Judging on JSONL Input

To evaluate submissions in batches, call the function `judge_jsonl_data`
