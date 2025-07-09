import json
from typing import Tuple, Union, Iterable, List, Dict
from pathlib import Path

def truncate_string(s: str, limit: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length and append a suffix if truncated.
    """
    return s[:limit] + (suffix if len(s) > limit else "")

def assert_directory_exists(dir_path: Union[str, Path]):
    dir_path = Path(dir_path)
    if not dir_path.exists():
        raise FileNotFoundError(f"The directory '{dir_path}' does not exist.")
    if not dir_path.is_dir():
        raise NotADirectoryError(f"The path '{dir_path}' is not a directory.")

def assert_file_exists(file_path: Union[str, Path]):
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"The file '{file_path}' does not exist.")
    if not file_path.is_file():
        raise IsADirectoryError(f"The path '{file_path}' is not a file.")

def ensure_list_of_paths(paths: Union[str, Path, Iterable[Union[str, Path]]]) -> List[Path]:
    if isinstance(paths, (str, Path)):
        return [Path(paths)]
    elif isinstance(paths, Iterable):
        return [Path(p) for p in paths]
    else:
        raise TypeError(f"Unsupported type: {type(paths)}")

def read_jsonl(path: Path) -> List[Dict]:
    with open(path, "r") as f:
        return [json.loads(line) for line in f]

def write_jsonl(data: List[Dict], path: Path):
    with open(path, "w") as f:
        for item in data:
           f.write(json.dumps(item) + "\n")

def proc_code(code: str, lang: str):
    """Extract the code content.
    """
    # code = code.partition(f'```{lang}\n')[2].rpartition('```')[0]
    # return code
    code = code.split(f'```{lang}\n')[-1].split('\n```')[0]
    if code.count("def main():") == 1 and code.count("main()") == 1:
        code += "\nmain()"
    return code

def get_id(entry: dict) -> str:
    if 'id' in entry:
        return entry['id']
    elif 'problem' in entry and 'id' in entry['problem']:
        return entry['problem']['id']
    else:
        raise ValueError(f'Id not found: {entry}')

def get_lang(entry: dict) -> str:
    if 'lang' in entry:
        return entry['lang']
    elif 'language' in entry:
        return entry['language']
    elif 'problem' in entry and 'language' in entry['problem']:
        return entry['problem']['language']
    else:
        raise ValueError(f'Lang not found: {entry}')

def get_content_original(entry: dict) -> str:
    if 'content' in entry:
        return entry['content']
    elif 'response' in entry:
        return entry['response']
    else:
        raise ValueError(f'Content not found: {entry}')