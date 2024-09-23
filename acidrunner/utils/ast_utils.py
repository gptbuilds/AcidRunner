import ast
import sys
from typing import List, Tuple

from acidrunner.types.custom_types import AcidBoolResult, AcidCosineResult, AcidFloatResult,  AcidTestType
from acidrunner.types.custom_types import FunctionInfo

def extract_decorators_and_return_type(node, name_sut: str) -> FunctionInfo:
    """Extracts decorator information and checks function return type."""
    bucket_name = None
    filenames = []
    return_type = AcidBoolResult

    # Extract decorator info
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'id'):
            # Handle use_bucket decorator
            if decorator.func.id == 'use_bucket': #### CHECK LATER
                bucket_name = decorator.args[0].s if decorator.args else None

            # Handle in_files decorator
            elif decorator.func.id == 'in_files':
                filenames = [arg.s for arg in decorator.args[0].elts] if decorator.args else []

    # Determine the return type of the function
    if node.returns:
        if isinstance(node.returns, ast.Name) and node.returns.id == 'AcidBoolResult':
            return_type =  AcidBoolResult
        elif isinstance(node.returns, ast.Name) and node.returns.id == 'AcidCosineResult':
            return_type = AcidBoolResult
        elif isinstance(node.returns, ast.Name) and node.returns.id == 'AcidFloatResult':
            return_type = AcidBoolResult
        else:
            print("Fatal error {node.name} has incorrect return type it can only be an AcidBoolResult, AcidCosineResult or AcidFloatResult please import from acidrunner.types.custom_types")
            print("Exiting...")
            print(ast.Name)
            print(node.returns.id)
            sys.exit("0x01")

    return FunctionInfo(node.name, bucket_name, filenames, return_type, name_sut)

def parse_ast_tree(tree, name_sut: str) -> Tuple[List[FunctionInfo], List[FunctionInfo]]:
    """Parses the AST tree and returns two lists: one for synchronous and one for asynchronous functions."""
    print("Parsing ast tree")
    functions_under_test = []
    async_functions_under_test = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith("_bench"):
            print(f"Found benchmark: {node.name}")
            functions_under_test.append(extract_decorators_and_return_type(node, name_sut))

        elif isinstance(node, ast.AsyncFunctionDef) and node.name.startswith("_bench"):
            print(f"Found benchmark(async): {node.name}")
            async_functions_under_test.append(extract_decorators_and_return_type(node, name_sut))

    return (functions_under_test, async_functions_under_test)

