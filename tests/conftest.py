import pytest

def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--image-name",
        action="store",
        default=None, 
        help="Docker image name to test"
    )