# STOS 2025 Compiler Subcontainer Image Template Repository

### Overview
- This implementation is only a suggestion; the only hard requirement is that the resulting container image satisfies the IO contract documented below.
- The sample pipeline is built around `g++` (C++17 with `-Wall -Wextra -Wpedantic`) and demonstrates a full flow: read sources, run compilation, publish the binary, persist metadata/logs.
- Recommended run steps:
  1. Build the image: `docker build -t template_comp ./comp_image_template `
  2. Execute the contract tests: `pytest`
- You can use the `--image-name` flag, e.g. `pytest --image-name template_comp`, to specify the Docker image, or define a default image name in the test code.
- Areas intentionally left for customization are marked with `# todo`. Use a project-wide search for `# todo` to locate and adjust every placeholder.
- The repo includes JSON validation (Pydantic) and explicit environment requirements to make swapping `g++` for another toolchain straightforward.


This repository includes GitHub Actions workflows (see `.github/workflows/`) that automate common tasks:
- Build the container image used by the tests
- Run the contract tests (`pytest`) against the built image
- Optionally publish a container image to a registry (configured in the workflow)


---


## IO Requirements for the Compiler Image
Communication between the parent container and its child containers is handled by specifying input and output locations in the environment variables of those containers. The directories referenced by these variables already exist because they are bind-mounted from the host; however, the output files inside those directories must be created by the process (they are not created automatically).

### Example Environment Variables

```env
environment = {
    "SRC": "/data/src",                     # Read-only directory with source files
    "LIB": "/data/lib",                     # Read-only directory with additional libraries
    "MAINFILE": submission.mainfile or "main.py",

    "OUT": "/data/out/comp.json",           # JSON output describing compilation result
    "INF": "/data/out/info.txt",            # Human-readable info file (ANSI supported)
    "BIN": "/data/bin/program",             # Compiled binary output
    "LOG": "/data/logs/compilation.log",    # Full compilation log
}
```

### Container Input and Output Control

#### **Input**

| ENV | Description | Type | Access |
|-----|-------------|------|--------|
| `SRC` | Directory containing user source code | Folder path | Read-only |
| `LIB` | Directory with source code of extra files | Folder path | Read-only |
| `MAINFILE` | Entry point filename selected by user or default, used in scripts | File name | - |

#### **Output**

| ENV | Description | Type | Notes |
|-----|-------------|------|-------|
| `OUT` | Location of the compiler output summary | File path (`.json`) | Result of container execution |
| `BIN` | Location of the compiled executable | File path | Created only if compilation succeeds |
| `INF` | Human-readable information file | File path (`.txt`) | Raw stdout/stderr from the compiler, supports ANSI formatting |
| `LOG` | Location of the compilation log | File path (`.log`) | Logs from container |

---

### `OUT` File Format

The `OUT` file must be a JSON file matching the following Pydantic schema:

```python
from typing import Optional
from pydantic import BaseModel

class CompilerOutputSchema(BaseModel):
    success: bool = False
    return_code: Optional[int] = None
    compilation_time_ms: Optional[int] = None
```

**Notes:**

- `success` indicates whether the compilation was successful (`True` if yes, `False` if no).  
- `return_code` is optional; if not set, the consumer may assume compilation failed.  
- `compilation_time_ms` is optional and can be used to store the compilation duration in milliseconds.  
- This schema ensures consistent parsing of the `OUT` file by downstream systems.

> **Note:** Most compilers return `0` on success and a non-zero value on failure.  
> The `success` field provides a convenient boolean abstraction so that downstream systems can quickly determine if the compilation succeeded, without interpreting specific return codes.  
> This also allows different error codes to be preserved in `return_code` for diagnostics or debugging purposes.

