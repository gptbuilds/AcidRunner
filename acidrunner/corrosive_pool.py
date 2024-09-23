from typing import List, Optional, Dict
from acidrunner.types.custom_types import CorrosiveTask, FunctionInfo, CorrosiveTaskData, CorrosiveSimilarity
import yaml
import uuid
import copy

class CorrosivePool:
    def __init__(self, pool: List[CorrosiveTask], meta_data: Optional[Dict] = None):
        self.pool = pool
        self.meta_data = meta_data if meta_data else {}

    @classmethod
    def from_function_info_list(cls, function_info_list: List[FunctionInfo], runs: int):
        tasks = []
        for run in range (0, runs):
            for func_info in function_info_list:
                task_data = CorrosiveTaskData()

                for filename in func_info.filenames:
                    with open(filename, 'r') as file:
                        yaml_data = yaml.safe_load(file)
                        for test in yaml_data["tests"]:
                            task_id = str(uuid.uuid4())  # Generate a unique task ID
                            args = [test['args'][arg] for arg in test['args']]
                            if 'similarity' in test:
                                sim = test['similarity']
                                similarity = CorrosiveSimilarity(
                                    embedder=sim['embedder'],
                                    score_against=sim['score_against'],
                                    min_similarity=sim.get('min_similarity', 0.0),
                                    max_distance=sim.get('max_distance', 0.0)
                                )
                                tasks.append(CorrosiveTask(
                                    task_id=task_id,
                                    name=test['name'],
                                    func=func_info,
                                    data=copy.deepcopy(task_data),
                                    args=args,
                                    similarity=similarity,
                                    run=run
                                ))
                            else:
                                tasks.append(CorrosiveTask(
                                    task_id=task_id,
                                    name=test['name'],
                                    func=func_info,
                                    data=copy.deepcopy(task_data),
                                    args=args,
                                    run=run
                                ))

        # Create a corrosive pool with the collected tasks
        return cls(pool=tasks)

    def calculate_success_rate(self) -> float:
        total_tasks = len(self.pool)
        if total_tasks == 0:
            return 0.0
        successful_tasks = sum(1 for task in self.pool if task.succes)
        return (successful_tasks / total_tasks) * 100

    def calculate_success_rate_passed(self) -> float:
        total_tasks = len(self.pool)
        if total_tasks == 0:
            return 0.0
        successful_tasks = sum(1 for task in self.pool if task.data.result == True)
        return (successful_tasks / total_tasks) * 100

    def calculate_average_runtime(self) -> float:
        total_runtime = 0
        count = 0
        for task in self.pool:
            if task.data.t0 is not None and task.data.t1 is not None:
                runtime = task.data.t1 - task.data.t0
                total_runtime += runtime
                count += 1
        return (total_runtime / count) if count > 0 else 0.0

    def filter_successful_tasks(self) -> List[CorrosiveTask]:
        return [task for task in self.pool if task.data.result]

    def filter_unsuccessful_tasks(self) -> List[CorrosiveTask]:
        return [task for task in self.pool if not task.data.result]

    def filter_tasks_by_runtime(self, min_runtime: int, max_runtime: int) -> List[CorrosiveTask]:
        filtered_tasks = []
        for task in self.pool:
            if task.data.t0 is not None and task.data.t1 is not None:
                runtime = task.data.t1 - task.data.t0
                if min_runtime <= runtime <= max_runtime:
                    filtered_tasks.append(task)
        return filtered_tasks
