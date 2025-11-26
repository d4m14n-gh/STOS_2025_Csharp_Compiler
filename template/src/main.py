import os
import shutil
import subprocess
import compiler_envs
from glob import glob
from typing import List
from logger import logger
from compiler_output_schema import CompilerOutputSchema


def save_csproj_file(csproj_path: str) -> None:
    TARGET_FRAMEWORK = "net8.0"
    TARGET_ARCH = "linux-x64"
    template = f"""
        <Project Sdk="Microsoft.NET.Sdk">
            <PropertyGroup>
                <OutputType>Exe</OutputType>
                <TargetFramework>{TARGET_FRAMEWORK}</TargetFramework>
                <RuntimeIdentifier>{TARGET_ARCH}</RuntimeIdentifier>
            </PropertyGroup>
        </Project>
    """
    logger.info("Generated .csproj file content:\n%s", template)
    with open(csproj_path, "w", encoding="utf-8") as csproj_file:
        csproj_file.write(template)


def compile() -> CompilerOutputSchema:
    src_path = compiler_envs.SRC
    lib_path = compiler_envs.LIB
    compiled_program_path = compiler_envs.BIN
    info_file_path = compiler_envs.INF
    tmp_src_dir = "./tmp_src"
    binary_name = "base"  # assuming the project name is 'base'
    base_csproj_path = os.path.join(tmp_src_dir, "base.csproj")
    tmp_artifact_dir = "./tmp_artifacts"

    # todo =====================================================================
    name_patterns = ["*.cs"] # not a must have
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
    os.umask(0o000)
    os.makedirs(tmp_src_dir, exist_ok=True)
    os.makedirs(tmp_artifact_dir, exist_ok=True)
    for src_file in all_src_files:
        shutil.copy(src_file, tmp_src_dir)
    save_csproj_file(base_csproj_path)

    cmd = [
        "dotnet",
        "publish",
        "-c", "Release",
        "-r", "linux-x64",
        "--self-contained", "true",
        "/p:PublishSingleFile=true",
        "/p:IncludeNativeLibrariesForSelfExtract=true",
        "-o", tmp_artifact_dir,
        base_csproj_path
    ]
    # * ========================================================================

    with open(info_file_path, "w", encoding="utf-8") as info_file:
        result = subprocess.run(
            cmd,
            stdout=info_file,
            stderr=info_file
        )
    

    return_code = result.returncode
    success = return_code == 0

    # print info file content to log
    with open(info_file_path, "r", encoding="utf-8") as info_file:
        info_content = info_file.read()
        logger.info("Compilation info:\n%s", info_content)

    if success:
        compiled_binary_tmp_path = os.path.join(tmp_artifact_dir, binary_name)

        if os.path.isfile(compiled_binary_tmp_path):
            shutil.copy(compiled_binary_tmp_path, compiled_program_path)
            os.chmod(compiled_program_path, 0o777)
        else:
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
    