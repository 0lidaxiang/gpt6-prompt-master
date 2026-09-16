#!/usr/bin/env python3
"""Single-file snapshot, guarded apply and guarded restore. Python 3, stdlib only."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import tempfile


def regular(path):
    path = Path(os.path.abspath(path))
    for part in (path, *path.parents):
        if part.is_symlink():
            raise ValueError(f"Refusing symbolic link: {part}")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f"Expected regular file with one link: {path}")
    return path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_checked(path, expected, replacement, mode):
    path = regular(path)
    if path.read_bytes() != expected or stat.S_IMODE(path.stat().st_mode) != mode:
        raise ValueError("Source content or permissions changed; review and stage again.")
    fd, temporary = tempfile.mkstemp(prefix=".skill-audit-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(replacement)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        regular(path)
        if path.read_bytes() != expected or stat.S_IMODE(path.stat().st_mode) != mode:
            raise ValueError("Source changed during operation; no replacement performed.")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def stage(source, candidate, output):
    source, candidate = regular(source), regular(candidate)
    if source == candidate:
        raise ValueError("Source and candidate must be different files.")
    before, after = source.read_bytes(), candidate.read_bytes()
    # Binary or non-UTF-8 input must not be silently rewritten.
    old, new = before.decode("utf-8"), after.decode("utf-8")
    if "\x00" in old or "\x00" in new:
        raise ValueError("NUL bytes are not supported.")
    output = Path(output).absolute()
    for part in (output, *output.parents):
        if part.is_symlink():
            raise ValueError(f"Refusing symbolic link output: {part}")
    output.mkdir(parents=True, exist_ok=True)
    snapshot = Path(tempfile.mkdtemp(prefix="audit-", dir=output))
    (snapshot / "original").write_bytes(before)
    (snapshot / "candidate").write_bytes(after)
    lines = difflib.unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                fromfile="a/" + source.name, tofile="b/" + source.name)
    diff = "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                   for line in lines)
    (snapshot / "changes.diff").write_text(diff, encoding="utf-8")
    save_json(snapshot / "manifest.json", {
        "version": 1, "source": str(source), "mode": stat.S_IMODE(source.stat().st_mode),
        "original_sha256": digest(before), "candidate_sha256": digest(after),
    })
    command = f"python3 {shlex.quote(str(Path(__file__).resolve()))}"
    print(json.dumps({"status": "staged; source unchanged", "snapshot": str(snapshot),
                      "apply": f"{command} apply {shlex.quote(str(snapshot))}",
                      "rollback": f"{command} rollback {shlex.quote(str(snapshot))}"},
                     ensure_ascii=False, indent=2))


def change(snapshot, action):
    snapshot = Path(snapshot).absolute()
    manifest = json.loads(regular(snapshot / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("version") != 1:
        raise ValueError("Unknown manifest version.")
    before = regular(snapshot / "original").read_bytes()
    after = regular(snapshot / "candidate").read_bytes()
    if digest(before) != manifest["original_sha256"] or digest(after) != manifest["candidate_sha256"]:
        raise ValueError("Snapshot changed; refusing operation.")
    source = regular(manifest["source"])
    current = source.read_bytes()
    expected, replacement = (before, after) if action == "apply" else (after, before)
    if current == replacement and stat.S_IMODE(source.stat().st_mode) == manifest["mode"]:
        print("Already at requested version; no write performed.")
        return
    replace_checked(source, expected, replacement, manifest["mode"])
    print(json.dumps({"status": action + " completed", "source": str(source),
                      "sha256": digest(replacement)}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    create = sub.add_parser("stage")
    create.add_argument("source")
    create.add_argument("candidate")
    create.add_argument("output")
    for action in ("apply", "rollback"):
        child = sub.add_parser(action)
        child.add_argument("snapshot")
    args = parser.parse_args()
    try:
        if args.action == "stage":
            stage(args.source, args.candidate, args.output)
        else:
            change(args.snapshot, args.action)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
