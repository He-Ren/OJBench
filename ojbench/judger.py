import sys
import copy
import loguru
import multiprocessing as mp
from tqdm import tqdm
from pathlib import Path
from typing import Optional, Union, Iterable, List, Tuple, Dict
from filelock import FileLock

from .utils.result import Result
from .utils.judger_config import Config
from .utils.judger_utils import ensure_list_of_paths, read_jsonl, write_jsonl

logger = loguru.logger
config: Optional[Config] = None

_root = Path(__file__).parent
_default_runtime_path = _root / 'runtime.yaml'
_default_config_path = _root / 'config.yaml'
_default_compile_lock_path = _root / 'compile_lock.lock'

_skip_id = {'nwerc2023_H', 'swerc2023_L', 'loj-3897'}

def init(
    problem_dirs: Union[str, Path, Iterable[Union[str, Path]]],
    config_path: Union[str, Path] = _default_config_path,
    runtime_path: Union[str, Path] = _default_runtime_path,
    compile_lock_path: Union[str, Path] = _default_compile_lock_path
):
    """
    Initialize the judger environment.

    This function must be called once before performing any judging tasks.

    Args:
        problem_dirs (Union[str, Path, Iterable[Union[str, Path]]]):
            A path or list of paths to problem set directories. Each directory should
            contain a set of problems to be judged. This is the **only required parameter**.
        
        config_path (Union[str, Path], optional):
            Path to the internal config file.
            Usually does not need to be changed. Defaults to `config.yaml` in the source root.
        
        runtime_path (Union[str, Path], optional):
            Path to the file that defines runtime commands for each language.
            Defaults to `runtime.yaml` in the source root.
        
        compile_lock_path (Union[str, Path], optional):
            Path to a lock file used internally to synchronize compilation processes.
            Usually does not need to be changed. Defaults to `compile_lock.lock` in the source root.
    """

    global config

    if config is not None:
        logger.error('The \'init\' function can only be called once.')
        raise RuntimeError('The \'init\' function can only be called once.') 
    
    problem_dirs: List[Path] = ensure_list_of_paths(problem_dirs)
    config_path = Path(config_path)
    compile_lock_path = Path(compile_lock_path)

    config = Config(config_path=config_path,
                    runtime_path=runtime_path,
                    problem_dirs=problem_dirs,
                    compile_lock_path=compile_lock_path,
                    logger=logger)

    logger.info('Initializing DMOJ judger')

    _init_dmoj_env()
    _init_dmoj_executors()
    _init_dmoj_contrib_modules()

    logger.info('DMOJ judger initialized')

def assert_initialized():
    if config is None:
        logger.error('The \'init\' function have not been called.')
        raise RuntimeError('The \'init\' function have not been called.')

def _init_dmoj_env():
    import dmoj.judgeenv as judgeenv

    judgeenv._problem_dirs_cache = config.problem_dirs.copy()
    judgeenv.skip_self_test = False
    judgeenv.only_executors = set(config.supported_languages)
    judgeenv.env.update(config.runtime_paths.copy())

def _init_dmoj_executors():
    from dmoj.executors import load_executors, executors
    load_executors()
    missing = set(config.supported_languages) - executors.keys()
    if missing:
        logger.error(f"Missing executors: {missing}")
        raise ValueError(f"Required languages not loaded: {missing}")

def _init_dmoj_contrib_modules():
    from dmoj.contrib import load_contrib_modules
    load_contrib_modules()

def judge(problem_id: str, time_limit: float, memory_limit: int, language: str, source: str, stop_when_fail: bool = True, use_tqdm = True) -> Tuple[str,List]:
    from dmoj.error import CompileError, InternalError, OutputLimitExceeded, InvalidCommandException
    from dmoj.problem import Problem
    from dmoj.result import Result

    assert_initialized()

    problem = Problem(problem_id=problem_id, time_limit=time_limit, memory_limit=memory_limit, meta={})
    grader = None
    readable_main_code = 'AC'
    skip_rest: bool = False
    try:
        with FileLock(config.compile_lock_path):
            grader = problem.grader_class(judge=None, problem=problem, language=language, source=source)
    except CompileError:
        readable_main_code = 'CE'
        skip_rest = True
        logger.warning(f'Compile error for problem: {problem_id}, language: {language}')
    except InternalError:
        readable_main_code = 'IE'
        skip_rest = True
        logger.warning(f'Internal error for problem: {problem_id}, language: {language}')
    except OutputLimitExceeded:
        readable_main_code = 'OLE'
        skip_rest = True
        logger.warning(f'Output limit exceeded for problem: {problem_id}, language: {language}')
    except InvalidCommandException:
        readable_main_code = 'IE'
        skip_rest = True
        logger.warning(f'Invalid command exception for problem: {problem_id}, language: {language}')

    results = []
    if grader is not None:
        cases = problem.cases()
        for case in tqdm(cases, desc='Grading', unit='case', disable = not use_tqdm):
            if skip_rest:
                r = Result(case, result_flag=Result.SC)
            else:
                try:
                    r = grader.grade(case=case)
                except Exception as e:
                    r = Result(case,
                               result_flag=Result.IE,
                               feedback = f'Exception {type(e).__name__}: {str(e)}')
            
            if readable_main_code == 'AC':
                readable_main_code = r.readable_codes()[0]
            
            if r.readable_codes()[0] != 'AC' and stop_when_fail:
                skip_rest = True

            result = {
                'in_file': case.config.get('in'),
                'out_file': case.config.get('out'),
                'result_flag': r.result_flag,
                'readable_main_code': r.readable_codes()[0],
                'readable_codes': r.readable_codes(),
                'execution_time': r.execution_time,
                'wall_clock_time': r.wall_clock_time,
                'context_switches': r.context_switches,
                'runtime_version': r.runtime_version,
                'max_memory': r.max_memory,
                'output': r.output,
                'feedback': r.feedback,
                'extended_feedback': r.extended_feedback,
                'points': r.points,
                'total_points': r.total_points,
            }
            results.append(result)
        logger.info(f'Judged problem {problem_id}, language {language}, main code {readable_main_code}')
    return (readable_main_code, results)

def judge_entry(entry: dict, use_tqdm: bool = True) -> Tuple[str,List]:
    """
    Judge a single entry and return the result.

    Args:
        entry (dict): A dictionary of submission data.
        use_tqdm (bool, optional): Whether to display a tqdm progress bar during judging. Defaults to True.

    Returns:
        Tuple[str, List]: A tuple containing:
            - str: Status.
            - List: Detailed results.
    """

    from .utils.judger_utils import get_id, get_lang, get_content_original, proc_code, truncate_string

    logger.info('Testing entry')

    id: str = get_id(entry)
    lang: str = get_lang(entry)
    content_original: str = get_content_original(entry) 

    content = proc_code(content_original, lang)

    logger.info(f'id: {id}, lang: {lang}, content (first 50 letters): {repr(truncate_string(content))}')

    if id in _skip_id:
        logger.warning(f'Skip {id}')
        return ('Skip', [])
         
    lang_in_dmoj = config.language_dict[lang]

    result = judge(
        problem_id = id,
        time_limit = 10,
        memory_limit = 1024 * 1024, # 1GB
        language = lang_in_dmoj,
        source = content,
        stop_when_fail = False,
        use_tqdm = use_tqdm
    )

    return result

def worker(worker_id: int, log_path: Path, task_queue: mp.Queue, result_queue: mp.Queue):

    log_file = open(log_path, 'w')
    logger.remove()
    logger.add(log_path, enqueue = True)
    sys.stdout = log_file
    sys.stderr = log_file

    while True:
        logger.info('Waiting for getting from queue...')
        task = task_queue.get()
        logger.info(f'Get, type = {type(task)}')
        if task is None:
            break

        (entry, lineid) = task
        
        result_queue.put(('m', worker_id, f'Start line {lineid + 1}'))

        result = judge_entry(entry, lineid)

        result_queue.put(('m', worker_id, f'Complete line {lineid + 1}'))
        result_queue.put(('r', worker_id, lineid, result))
    
    result_queue.put(('m', worker_id, f'Worker {worker_id} quit'))
    logger.info(f'Worker {worker_id} quit')
    log_file.close()

def judge_jsonl_data(input: List[Dict], num_workers: int = 16, worker_log_path: Union[str, Path, None] = None, identifier: Union[str, None] = None) -> List[Dict]:
    """
    Judge a list of entries and return the list with results added.

    Args:
        input (List[Dict]): A list of entries.
        num_workers (int): Number of worker processes to use for judging.
        worker_log_path (Union[str, Path, None]): Directory path where worker logs are stored. '/dev/null' will be used if set to None. Default to None.
        identifier (Union[srt, None]): An identifier for this test group, just used for printing the log. Default to None.

    Returns:
        List[Dict]: The result.
    """
    output: List = copy.deepcopy(input)

    for t in input:
        from .utils.judger_utils import get_id
        from dmoj.judgeenv import get_problem_root

        id = get_id(t)
        if type(id) == int:
            id = 'loj-' + str(id)
        t['id'] = id
        
        if id not in _skip_id:
            assert get_problem_root(id) is not None, f'Problem {id} not found'
    
    task_queue: mp.Queue = mp.Queue()
    result_queue: mp.Queue = mp.Queue()
    
    num_tasks = len(input)
    for i in range(num_tasks):
        task_queue.put((input[i], i))
    for _ in range(num_workers * 2 + 10):
        task_queue.put(None)
    
    workers: List[mp.Process] = []
    if worker_log_path is not None:
        worker_log_path = Path(worker_log_path)
        worker_log_path.mkdir(exist_ok = True)
    for wid in range(num_workers):
        log_path = worker_log_path / f'worker{wid}.log' if worker_log_path is not None else Path('/dev/null')
        p = mp.Process(target=worker, args=(wid, log_path, task_queue, result_queue))
        p.daemon = True
        p.start()
        workers.append(p)
    
    from .utils.progress_tracker import ProgressTracker

    ptracker = ProgressTracker(total = num_tasks)
    while not ptracker.is_complete():
        
        logger.info(f'---------------------------')

        message = result_queue.get()
        if message[0] == 'm':
            logger.info(f'Worker {message[1]}: {message[2]}')
            continue

        if message[0] == 'r':
            (_, wid, i, result) = message
            result = Result(result[0], result[1])

            ptracker.update()
            if identifier is not None:
                logger.info(f'Testing: [{identifier}]')
            logger.info(f'Worker {wid} finished line {i + 1} / {len(input)}')
            logger.info(ptracker.get_progress())

            result.write_to_entry(output[i])

            for scale_type in [8, 4, 2, 1]:
                scale_verdict = result.verdict_after_scale(1 / scale_type)
                scale_text = f'1/{scale_type}' if scale_type != 1 else '1'
                scale_text_prefix = f'1/{scale_type}' if scale_type != 1 else ''

                output[i][f'{scale_text_prefix}is_passed'] = (scale_verdict == 'AC')
                output[i][f'{scale_text_prefix}verdict'] = scale_verdict

                logger.info(f'scale = {scale_text}, verdict = {scale_verdict}')
    
    assert len(workers) == num_workers
    for p in workers:
        p.terminate()
        p.join()
    
    task_queue.close()
    result_queue.close()
    
    return output

def judge_jsonl(input_path: Union[str, Path], output_path: Union[str, Path, None] = None, num_workers: int = 16, worker_log_path: Union[str, Path, None] = None, identifier: Union[str, None] = None) -> List[Dict]:
    if identifier is None:
        identifier = str(input_path)
    input = read_jsonl(input_path)
    output = judge_jsonl_data(input = input,
                              num_workers = num_workers,
                              worker_log_path = worker_log_path,
                              identifier = identifier)
    if output_path is not None:
        write_jsonl(output, output_path)
    return output