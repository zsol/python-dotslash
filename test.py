import json
from pathlib import Path
import shutil
import sys
import subprocess
import traceback


def check_path(dotslash: str, path: Path) -> None:
    contents = path.read_text()
    _header, _, descriptor_text = contents.partition("\n")
    descriptor = json.loads(descriptor_text)
    assert isinstance(descriptor, dict)
    name = descriptor["name"]
    assert isinstance(name, str)
    version = name.removeprefix("cpython-")
    proc = subprocess.run(
        [dotslash, path, "-c", "import sys; print(sys.version)"],
        text=True,
        capture_output=True,
        check=True,
    )
    if not proc.stdout.startswith(version):
        raise AssertionError(f"{version=} not found in {proc.stdout=}")


def main() -> None:
    dotslash = shutil.which("dotslash")
    if dotslash is None:
        print("Dotslash binary cannot be found, failing test.", file=sys.stderr)
        sys.exit(-1)
    descriptor_paths = sys.argv[1:]
    failure = False
    for path in descriptor_paths:
        try:
            check_path(dotslash, Path(path))
        except Exception:
            failure = True
            traceback.print_exc()
    if failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
