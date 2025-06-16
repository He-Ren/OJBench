import copy
from typing import List, Dict

class Result:
    full_verdict: str
    results: List[Dict]
    first_not_ac: int
    def __init__ (self, full_verdict: str, results: List[Dict]):
        self.full_verdict = copy.deepcopy(full_verdict)
        self.results = copy.deepcopy(results)
        self.first_not_ac = len(self.results)
        for i, l in enumerate(self.results):
            if l['readable_main_code'] != 'AC':
                self.first_not_ac = i
                break
    
    def verdict_after_scale(self, ratio: float) -> str:
        if len(self.results) == 0:
            return self.full_verdict
        else:
            n = len(self.results)
            new_n = round(n * ratio)
            return self.full_verdict if self.first_not_ac < new_n else 'AC'

    def passed_after_scale(self, ratio: float) -> bool:
        return self.verdict_after_scale(ratio) == 'AC'
    
    def scale(self, ratio: float):
        if len(self.results) == 0:
            return Result(
                full_verdict = self.full_verdict,
                results = self.results
            )
        
        n = len(self.results)
        new_n = round(n * ratio)
        new_results = self.results[:new_n]
        new_full_verdict = 'AC'
        for t in new_results:
            c = t['readable_main_code']
            if c != 'AC':
                new_full_verdict = t
                break
        return Result(
            full_verdict = new_full_verdict,
            results = new_results
        )

    @classmethod
    def parse_from_entry(cls, entry: Dict) -> 'Result':
        detailed_results: dict | list = entry['detailed_results']
        if type(detailed_results) == dict:
            return Result(
                detailed_results['final_verdict'],
                detailed_results['results']
            )
        detailed_results: list

        if len(detailed_results) == 0:
            return Result('CE', [])
        for t in detailed_results:
            if t['readable_main_code'] != 'AC':
                return Result(t['readable_main_code'], detailed_results)
    
    def write_to_entry(self, entry: Dict):
        if self.full_verdict == 'Skip':
            entry['is_skip'] = True
        entry['detailed_results'] = {
            'final_verdict': self.full_verdict,
            'results': self.results
        }
        entry['is_passed'] = self.full_verdict == 'AC'
        