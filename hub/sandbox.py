"""Restricted execution for notebooks and submitted Python."""

import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile


def base_command(python, workspace, network=False):
    if not shutil.which("bwrap"):
        raise RuntimeError("Bubblewrap is required for isolated execution")
    python = Path(python).absolute()
    environment = python.parent.parent
    runtime = Path(sys.base_prefix)
    runtime_alias = Path(os.readlink(python)).parent.parent if python.is_symlink() else runtime
    command = ["bwrap", "--unshare-all", "--die-with-parent", "--new-session", "--cap-drop", "ALL", "--clearenv"]
    if network:
        command.append("--share-net")
    for path in dict.fromkeys([Path("/usr"), Path("/lib"), Path("/lib64"), runtime, runtime_alias, environment]):
        if path.exists():
            command.extend(["--ro-bind", str(path), str(path)])
    for path in ["/etc/ld.so.cache", "/etc/localtime", "/etc/fonts"]:
        if Path(path).exists():
            command.extend(["--ro-bind", path, path])
    command.extend(["--proc", "/proc", "--dev", "/dev", "--tmpfs", "/tmp",
                    "--bind", str(Path(workspace).absolute()), "/work", "--chdir", "/work"])
    variables = {
        "PATH": f"{environment}/bin:/usr/bin:/bin", "HOME": "/tmp", "LANG": "C.UTF-8",
        "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "2", "MPLCONFIGDIR": "/tmp/matplotlib", "XDG_CACHE_HOME": "/tmp/cache",
        "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy", "PYGAME_HIDE_SUPPORT_PROMPT": "1",
    }
    for key, value in variables.items():
        command.extend(["--setenv", key, value])
    return command


def run_isolated(python, script, workspace, timeout=30, arguments=()):
    command = base_command(python, workspace)
    command.extend(["--ro-bind", str(Path(script).absolute()), "/runner.py", str(Path(python).absolute()),
                    "-I", "/runner.py", *map(str, arguments)])
    command = ["prlimit", f"--as={6 * 1024 ** 3}", f"--fsize={32 * 1024 ** 2}",
               "--nofile=128", "--cpu=100:105", "--", *command]
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            raise TimeoutError(f"Evaluation exceeded {timeout} seconds") from None
        stdout.seek(0)
        stderr.seek(0)
        return subprocess.CompletedProcess(command, process.returncode, stdout.read(256000).decode(errors="replace"),
                                           stderr.read(256000).decode(errors="replace"))
