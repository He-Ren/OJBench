## Prerequisites

Ensure you have Python 3.10+ installed, along with Git.

---

## 1. Install DMOJ

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

---

## 2. Install OJBench

Clone the OJBench library and install it in editable mode:

```bash
# Clone the OJBench repository
git clone git@github.com:He-Ren/OJBench.git
cd OJBench

# Install into the current Python environment
pip install .
```

---

## 3. Download Test Data

Test inputs are hosted on Hugging Face under `He-Ren/OJBench_testdata`. You can clone with Git LFS. Ensure Git LFS is installed (`git lfs install`), then run:

  ```bash
  git clone https://huggingface.co/He-Ren/OJBench_testdata
  ```

---

## 4. Usage / Testing

### Initialization

Use the `init` function to set up the judging environment. Provide one or more problem directories (for example, `data/NOI` and `data/ICPC`).

### Running Judging on JSONL Input

To evaluate submissions in batch, call `judge_jsonl_data`
