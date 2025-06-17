import loguru
import yaml
import sys
import traceback
import copy
from typing import List, Dict
from pathlib import Path

class Config:
    language_dict: Dict[str,str]
    supported_languages: List[str]
    runtime_paths: Dict
    problem_dirs: List[Path]
    compile_lock_path: Path

    def __init__(self,
                 config_path: Path,
                 runtime_path: Path,
                 problem_dirs: List[Path],
                 compile_lock_path: Path,
                 logger = loguru.logger
                 ):
        self.logger = logger
        self.logger.info('Initialing judge configuration')

        config_path = Path(config_path)
        self.logger.info(f'config_path: {config_path}')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            try:
                lang: Dict[str,str] = config['languages']
                self.language_dict = copy.deepcopy(lang)
                self.supported_languages = list(lang.values())
            except Exception as e:
                logger.error(f'{type(e).__name__}: {e}')
                logger.error(f'Please check the configuration file: {config_path}')
                traceback.print_exc()
                sys.exit(1)
        
        runtime_path = Path(runtime_path)
        self.logger.info(f'runtime_path: {runtime_path}')
        with open(runtime_path, 'r') as file:
            runtime = yaml.safe_load(file)
            try:
                self.runtime_paths = {'runtime': dict(runtime)}
            except Exception as e:
                logger.error(f'{type(e).__name__}: {e}')
                logger.error(f'Please check the runtime file: {runtime_path}')
                traceback.print_exc()
                sys.exit(1)

        
        problem_dirs = [Path(l) for l in problem_dirs]
        self.logger.info(f'problem_dirs: {problem_dirs}')
        for l in problem_dirs:
            assert l.exists(), f'Problem dir does not exist: {l}'
        self.problem_dirs = problem_dirs

        compile_lock_path = Path(compile_lock_path)
        self.logger.info(f'compile_lock_path: {compile_lock_path}')
        self.compile_lock_path = compile_lock_path
        compile_lock_path.touch(exist_ok = True)
        assert compile_lock_path.is_file(), f'{compile_lock_path} is not a file'

        self.logger.info(f'Judge configuration initialized')


    def get_supported_languages(self):
        return self.supported_languages.copy()
    
    def get_problem_dirs(self):
        return self.problem_dirs.copy()
    
    def get_runtime_paths(self):
        return self.runtime_paths.copy()