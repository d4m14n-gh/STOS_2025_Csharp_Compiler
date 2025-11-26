import os
from typing import Dict, List, NamedTuple
from compiler_output_schema import CompilerOutputSchema


class CompilerEnvMock(NamedTuple):
    base_path: str
    envs: Dict[str, str]
    bindings: Dict[str, str]
    run_command: List[str]
    image_name: str


def gen_env_paths(base_path: str) -> Dict[str, str]:
    return {
        "SRC": os.path.join(base_path, "src"),
        "LIB": os.path.join(base_path, "lib"),
    
        "OUT": os.path.join(base_path, "out", "output.json"),
        "BIN": os.path.join(base_path, "out", "program"),
        "INF": os.path.join(base_path, "out", "info.txt"),
        "LOG": os.path.join(base_path, "logs", "compilation.log"),
    }


def gen_bindings(local_base_path: str, host_base_path: str) -> Dict[str, str]:
    return {
        os.path.join(host_base_path, "src"):  os.path.join(local_base_path, "src"),
        os.path.join(host_base_path, "lib"): os.path.join(local_base_path, "lib"),
        os.path.join(host_base_path, "out"): os.path.join(local_base_path, "out"),
        os.path.join(host_base_path, "logs"): os.path.join(local_base_path, "logs")
}


def init_mock_files(mock_base_path: str, src_files_path: str) -> None:
    if os.path.exists(mock_base_path):
        import shutil
        shutil.rmtree(mock_base_path)
    os.umask(0o000)
    os.makedirs(os.path.join(mock_base_path, "src"), exist_ok=True)
    os.makedirs(os.path.join(mock_base_path, "lib"), exist_ok=True)
    os.makedirs(os.path.join(mock_base_path, "out"), exist_ok=True)
    os.makedirs(os.path.join(mock_base_path, "logs"), exist_ok=True)
    os.makedirs(os.path.join(mock_base_path, "empty"), exist_ok=True)
    for filename in os.listdir(src_files_path):
        src_file = os.path.join(src_files_path, filename)
        dest_file = os.path.join(mock_base_path, "src", filename)
        with open(src_file, "r") as f_src, open(dest_file, "w") as f_dest:
            f_dest.write(f_src.read())


def gen_run_command(envs: Dict[str, str], bindings: Dict[str, str], image_name: str) -> List[str]:
    container_run_command = ["docker", "run", "--rm"]
    for k, host_path in envs.items():
        container_run_command += ["-e", f"{k}={host_path}"]
    for host_path, container_path in bindings.items():
        container_run_command += ["-v", f"{host_path}:{container_path}"]
    container_run_command += [image_name]
    return container_run_command

    
def fetch_compilation_output(output_file_path: str) -> CompilerOutputSchema:
    with open(output_file_path, "r", encoding="utf-8") as output_file:
        return CompilerOutputSchema.model_validate_json(output_file.read())
    

