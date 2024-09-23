import yaml
from typing import List
import importlib
import importlib.util
from acidrunner.token_bucket import TokenBucket
from acidrunner.types.custom_types import AcidBoolResult, AcidCosineResult, CorrosiveTask
from acidrunner.utils.ast_utils import parse_ast_tree 
from acidrunner.corrosive_pool import CorrosivePool
import sys
import ast
import time
import asyncio
import pprint
import tracemalloc
from asyncio import Lock

class AcidRunner:
    class Settings:
        def __init__(self, systems_under_test, buckets, file_settings):
            self.systems_under_test = systems_under_test
            self.buckets = buckets
            self.file_settings = file_settings

        @classmethod
        def from_dict(cls, config_dict):
            # Sanitize and validate systems_under_test
            systems = config_dict.get('systems_under_test', [])
            sanitized_systems = [
                {
                    'name': system.get('name'),
                    'entrypoint_benchmarks': system.get('entrypoint_benchmarks'),
                    'entrypoint_tests': system.get('entrypoint_tests'),
                    'tracemalloc_enabled': system.get('tracemalloc_enabled')
                }
                for system in systems
            ]

            # Sanitize and validate buckets
            buckets = config_dict.get('buckets', [])
            sanitized_buckets = [
                {
                    'name': bucket.get('name'),
                    'rpm': bucket.get('rpm')
                }
                for bucket in buckets
            ]

            # Sanitize and validate file_settings
            file_settings = config_dict.get('file_settings', [])
            sanitized_file_settings = [
                {
                    'data_dir': setting.get('data_dir')
                }
                for setting in file_settings
            ]

            return cls(sanitized_systems, sanitized_buckets, sanitized_file_settings)

        def __repr__(self):
            return (f"Settings(systems_under_test={self.systems_under_test}, "
                    f"buckets={self.buckets}, file_settings={self.file_settings})")

    def __init__(self, config_path):
        self.config_path = config_path
        self.settings: AcidRunner.Settings | None = None
        self.global_buckets = {}
        self.systems_under_test = {}
        self.semaphore = asyncio.Semaphore(10)# change to setting later
        self.corrosive_pool_async = None
        self.corrosive_pool_sync = None
        self.meta_data = {}

    def load_settings(self):
        with open(self.config_path, 'r') as file:
            config_dict = yaml.safe_load(file)
        self.settings = AcidRunner.Settings.from_dict(config_dict)
        return self.settings

    def setup_buckets(self):
        if self.settings:
            if self.settings.buckets:
                print("Setting up buckets")
                for settings_bucket in self.settings.buckets:
                    name = settings_bucket['name']
                    rpm = settings_bucket['rpm']
                    capacity = rpm # for simplicity use the rpm as capicaty might make more granular in future
                    token_bucket = TokenBucket(capacity, rpm / 60)
                    self.global_buckets[name] = token_bucket

                return
            print("No buckets found in config, exiting")
        sys.exit(0xcc)

    def scan_and_load_entrypoints(self, runs):
        if self.settings:
            if self.settings.systems_under_test:
                for sut in self.settings.systems_under_test:
                    name_sut = sut.get('name')
                    print(f"Scanning entrypoints for system: {name_sut}")
                    entrypoint = sut.get('entrypoint_benchmarks')

                    try:
                        with open(entrypoint, 'r') as file:
                            smoke_tree = ast.parse(file.read())
                            functions_under_test, async_functions_under_test = parse_ast_tree(smoke_tree, name_sut)
                    except Exception as e:
                        print(f"Couldn't scan file {entrypoint}. Make sure you are executing acidrunner from the correct directory \nError:\n {e}")
                        break

                    if len(functions_under_test) == 0 and len(async_functions_under_test) == 0: 
                        print(f"No entrypoints found in file: {entrypoint}, exiting...")
                        sys.exit(0x00)
                    
                    self.corrosive_pool_async = CorrosivePool.from_function_info_list(async_functions_under_test, runs)
                    self.corrosive_pool_sync =  CorrosivePool.from_function_info_list(functions_under_test, runs)
                    
                    print(f"Loading file {entrypoint} as module")
                    module = self.import_from_path(name_sut, entrypoint)
                    self.systems_under_test.setdefault(name_sut, {})
                    self.systems_under_test[name_sut]['module'] = module
                return
            print("No systems found in config, exiting...")
        sys.exit(0xcc)

    def import_from_path(self, module_name, file_path):
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            #sys.modules[module_name] = module
            if spec.loader:
                spec.loader.exec_module(module)
                return module
        print("Unable to load module: {module_name} at {file_path}")
        sys.exit(0x01)           
                    
    async def wait_for_tokens(self, bucket_name):
        wait_time = 0.01  # start with a small wait time
        max_wait_time = 1  # upper bound for waiting

        bucket_instance = self.global_buckets.get(bucket_name)

        if not bucket_instance:
            print(f"Fatal error {bucket_name} not found, exiting...")
            sys.exit(0x01)

        while 0x01:
            if await bucket_instance.get_tokens(1):
                break
            else:
                await asyncio.sleep(wait_time)
                wait_time = min(max_wait_time, wait_time * 2)  # exponential backoff

    async def async_task(self, coro_task: CorrosiveTask):
        await self.wait_for_tokens(coro_task.func.bucket_name)

        module = self.systems_under_test[coro_task.func.name_sut]['module']

        if hasattr(module, coro_task.func.function_name):
            func = getattr(module, coro_task.func.function_name)
            try:
                coro_task.data.t0 = time.time_ns()
                res = await func(*coro_task.args)
                coro_task.data.t1 = time.time_ns()
                coro_task.data.meta_data = res.meta_data

                if type(res) == AcidBoolResult:
                    coro_task.data.result = res.result
                elif type(res) == AcidCosineResult:
                    pass

                print(f"[{coro_task.func.function_name}][{coro_task.func.bucket_name}][{coro_task.name}]:")
                print(f"{coro_task.task_id}")
                print(f"{coro_task.args}")
                print(f"Test passed: {coro_task.data.result}")
                print(f"Meta_Data: {coro_task.data.meta_data}")

                coro_task.succes = True

            except Exception as e:
                print(f"Error executing func {e}")
        else:
            print(f"Function {coro_task.func.function_name} not found in module {module.__name__}")

    async def run_async_tasks(self, extended_coro_pool):
        async def wrapped_task(coro_task):
            async with self.semaphore:
                return await self.async_task(coro_task)

        coroutines = [wrapped_task(coro_task) for coro_task in extended_coro_pool]
        results = await asyncio.gather(*coroutines)
        return results

    
    def run(self, runs):
        tracemalloc.start()
        print(f"Running AcidRunner with settings: {self.settings}")
        print(42*"*")
        self.runs = runs
        self.setup_buckets()
        self.scan_and_load_entrypoints(runs)

        t0 = time.time_ns()
        _ = asyncio.run(self.run_async_tasks(self.corrosive_pool_async.pool), debug=True)       
        elapsed = time.time_ns() - t0
        print(f"Tasks executed in {elapsed/1_000_000_000} seconds")
        
        print(f"Succes Rate Tasks (execution): {self.corrosive_pool_async.calculate_success_rate()}")
        print(f"Average runtime: {self.corrosive_pool_async.calculate_average_runtime()}")
        print("*"*42)
        success_percent = self.corrosive_pool_async.calculate_success_rate_passed()
        print(f"Percentage of tasks passed: {success_percent}")
        #print("List of tasks that didn't pass the bench:")
        #print(77*"*")
        #failed_tasks = self.corrosive_pool_async.filter_unsuccessful_tasks()
        #pprint.pprint(failed_tasks, indent=2)
        #print(77*"*")
        #print("List of tasks that passed the bench:")
        #success_tasks = self.corrosive_pool_async.filter_successful_tasks()
        #pprint.pprint(success_tasks, indent=2)
        
        print("jump for joy")
