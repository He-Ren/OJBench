from typing import Optional, Union, Iterable, List, Dict
from pathlib import Path
import loguru
import yaml

def truncate_string(s: str, limit: int = 50, suffix: str = "...") -> str:
    """Truncate a string to a maximum length and append a suffix if truncated.

    Args:
        s (str): The input string.
        limit (int, optional): The maximum length before truncation. Defaults to 50.
        suffix (str, optional): The string to append if truncation occurs. Defaults to '...'.

    Returns:
        str: The truncated string with suffix if necessary.
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

def proc_code(code: str, lang: str):
    """Extract the code content.
    """
    # code = code.partition(f'```{lang}\n')[2].rpartition('```')[0]
    # return code
    code = code.split(f'```{lang}\n')[-1].split('\n```')[0]
    if code.count("def main():") == 1 and code.count("main()") == 1:
        code += "\nmain()"
    return code

def extract_verdicts(result: Tuple[str, List[Dict]], key: str = 'readable_main_code') -> Tuple[str, List[str]]:
    (final_verdict, results) = result
    main_codes = []
    for entry in results:
        main_codes.append(entry.get(key, 'NA'))
    return (final_verdict, main_codes)

def get_final_verdict(result: Tuple[str, List[str]]) -> str:
    (final_verdict, verdicts) = result
    if len(verdicts) == 0:
        return final_verdict
    for t in verdicts:
        if t != 'AC':
            return t
    return 'AC'

def make_scale(original: Tuple[str, List], scale: float) -> Tuple[str, List]:
    (a, b) = original
    return (a, b[0: math.floor(len(b) * scale)])