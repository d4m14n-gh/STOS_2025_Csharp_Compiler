import os
import pytest
import subprocess
import test_utils as utils

# you can also use local path for debug: e.g.: os.path.join(os.path.dirname(os.path.realpath(__file__)), "mock")

# use -s option to see print outputs
# you can change IMAGE_NAME to your built image for debugging

# utils.gen_env_paths(mock_env.base_path) generates the env paths using host paths visible to the host system
# utils.gen_env_paths("/data") generates the env paths using inner container paths

# todo =========================================================================
IMAGE_NAME = "template_comp"


ASSETS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
VALID_SRC_PATH = os.path.join(ASSETS_PATH, "valid_src")
INVALID_SRC_PATH = os.path.join(ASSETS_PATH, "invalid_src")
# * ============================================================================


@pytest.fixture(scope="function")
def mock_env(tmp_path: str, pytestconfig: pytest.Config) -> utils.CompilerEnvMock: 
    os.chmod(tmp_path, 0o777)
    utils.init_mock_files(tmp_path, VALID_SRC_PATH)
    envs = utils.gen_env_paths("/data")
    bindings = utils.gen_bindings("/data", tmp_path)
    image_name: str = str(pytestconfig.getoption("image_name") or IMAGE_NAME)
    run_command = utils.gen_run_command(envs, bindings, image_name)
    return utils.CompilerEnvMock(tmp_path, envs, bindings, run_command, image_name)


def test_image_when_exists_should_be_found(mock_env: utils.CompilerEnvMock):
    result = subprocess.run(
        ["docker", "images", "-q", mock_env.image_name],
        capture_output=True,
        text=True,
        check=True,
    )

    assert result.stdout.strip(), f"Docker image {mock_env.image_name} does not exist"


def test_container_when_started_should_run_successfully(mock_env: utils.CompilerEnvMock):
    result = subprocess.run(mock_env.run_command, check=True)
    assert result.returncode == 0, "Container failed to run successfully"


def test_container_when_src_env_missing_should_fail(mock_env: utils.CompilerEnvMock):
    envs = mock_env.envs.copy()
    del envs["SRC"]
    container_run_command = utils.gen_run_command(envs, mock_env.bindings, mock_env.image_name)
    
    result = subprocess.run(container_run_command, check=False)
    assert result.returncode != 0, "Container should fail on start due to missing SRC environment variable"


def test_container_when_no_src_files_should_save_output(mock_env: utils.CompilerEnvMock):
    src_path = os.path.join(utils.gen_env_paths(mock_env.base_path)["SRC"])
    for file in os.listdir(src_path):
        os.remove(os.path.join(src_path, file))
    
    subprocess.run(mock_env.run_command, check=True)
    output = utils.fetch_compilation_output(utils.gen_env_paths(mock_env.base_path)["OUT"])
    assert not output.success, "Container should not fail and save output file when no src files are present"


def test_container_when_valid_src_should_compile_successfully(mock_env: utils.CompilerEnvMock):
    subprocess.run(mock_env.run_command, check=True)
    output = utils.fetch_compilation_output(utils.gen_env_paths(mock_env.base_path)["OUT"])
    assert output.success, "Container failed to compile valid src files successfully"


def test_container_when_compilation_successful_should_create_binary(mock_env: utils.CompilerEnvMock):
    subprocess.run(mock_env.run_command, check=True)
    envs = utils.gen_env_paths(mock_env.base_path)
    binary_path = envs["BIN"]
    assert os.path.isfile(binary_path), "Compiled binary file was not created in the expected location"


def test_container_when_compilation_should_create_info_file(mock_env: utils.CompilerEnvMock):
    subprocess.run(mock_env.run_command, check=True)
    envs = utils.gen_env_paths(mock_env.base_path)
    info_file_path = envs["INF"]
    assert os.path.isfile(info_file_path), "Info file was not created in the expected location"


def test_container_when_compile_error_should_write_info_file(mock_env: utils.CompilerEnvMock):
    host_env_paths = utils.gen_env_paths(mock_env.base_path)
    utils.init_mock_files(mock_env.base_path, INVALID_SRC_PATH)
    
    subprocess.run(mock_env.run_command, check=True)
    assert os.path.getsize(host_env_paths["INF"]) > 0, "Info file is empty despite compilation errors"


def test_container_when_compilation_should_create_output_file(mock_env: utils.CompilerEnvMock):
    subprocess.run(mock_env.run_command, check=True)
    output_file_path = utils.gen_env_paths(mock_env.base_path)["OUT"]
    assert os.path.isfile(output_file_path), "Output JSON file was not created in the expected location"


def test_container_when_output_created_should_contain_valid_json(mock_env: utils.CompilerEnvMock):
    subprocess.run(mock_env.run_command, check=True)
    output_file_path = utils.gen_env_paths(mock_env.base_path)["OUT"]
    output = utils.fetch_compilation_output(output_file_path)
    assert isinstance(output.success, bool), "Output JSON file does not contain valid 'success' field"