import os
import subprocess
import compiler_envs
from glob import glob
from typing import List
from logger import logger
from compiler_output_schema import CompilerOutputSchema

def compile() -> CompilerOutputSchema:
    src_path = compiler_envs.SRC
    lib_path = compiler_envs.LIB
    compiled_program_path = compiler_envs.BIN
    info_file_path = compiler_envs.INF

    # todo =====================================================================
    name_patterns = ["*.cpp", "*.cc", "*.cxx", "*.c++", "*.C", "*.CPP", "*.c"] # not a must have
    # * ========================================================================

    all_src_files: List[str] = []
    for pattern in name_patterns:
        all_src_files.extend(glob(os.path.join(src_path, pattern)))
        all_src_files.extend(glob(os.path.join(lib_path, pattern)))

    if not all_src_files:
        result = CompilerOutputSchema(success= False, return_code=1)
        with open(compiler_envs.OUT, "w", encoding="utf-8") as out_file:
            out_file.write(result.model_dump_json())
        with open(info_file_path, "w", encoding="utf-8") as info_file:
            info_file.write("No files found to compile\n")    
        logger.error("No files found to compile")
        return result
    
    # todo =====================================================================
    cmd = [
        "g++",
        "-Wall", 
        "-Wextra", 
        "-Wpedantic",
        "-fdiagnostics-color=always",
        "-I", lib_path,
        "-I", src_path,
        "-std=c++17",
        "-o", compiled_program_path
    ] + all_src_files
    # * ========================================================================

    with open(info_file_path, "w", encoding="utf-8") as info_file:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=info_file
        )
    
    return_code = result.returncode
    success = return_code == 0

    if success:
        if not os.path.isfile(compiled_program_path):
            logger.error("Compilation failed: binary was not created")
            success = False
    else:
        logger.error("Compilation failed with return code %d", return_code)

    result = CompilerOutputSchema(success= success, return_code=return_code)
    with open(compiler_envs.OUT, "w", encoding="utf-8") as out_file:
        out_file.write(result.model_dump_json())
    return result

        

if __name__ == "__main__":
    logger.info("Starting compilation process")
    compile()
    logger.info("Compilation process finished")
    