"""Behavior checks for the optional file helper; uses an isolated temporary directory."""
from pathlib import Path
import subprocess
import tempfile
import json
import os

script = Path(__file__).resolve().parents[1] / 'scripts/file_guard.py'
results = []


def run(*args, ok=True):
    p = subprocess.run(['python3', str(script), *map(str, args)], capture_output=True, text=True)
    assert (p.returncode == 0) == ok, (args, p.stdout, p.stderr)
    return p


with tempfile.TemporaryDirectory(prefix='skill-audit-test-') as tmp:
    # macOS /var is a system symlink; use its canonical path for ordinary-file tests.
    root = Path(tmp).resolve()
    src = root / '原文 with space.md'
    draft = root / '候选.md'
    original = '原文\r\n最后一行'.encode()
    changed = '优化稿\n新增条件\n'.encode()
    src.write_bytes(original)
    src.chmod(0o640)
    draft.write_bytes(changed)
    snap = Path(json.loads(run('stage', src, draft, root / 'backups').stdout)['snapshot'])
    assert src.read_bytes() == original
    results.append('stage 保留原文与 CRLF/无末尾换行')
    run('apply', snap)
    assert src.read_bytes() == changed and src.stat().st_mode & 0o777 == 0o640
    run('apply', snap)
    results.append('应用及重复应用、空格中文路径、权限保留')
    src.write_bytes(b'later edit')
    run('rollback', snap, ok=False)
    assert src.read_bytes() == b'later edit'
    results.append('拒绝回滚覆盖后续编辑')
    src.write_bytes(changed)
    run('rollback', snap)
    run('rollback', snap)
    assert src.read_bytes() == original
    results.append('字节级回滚及重复回滚')
    src.write_bytes(b'new source')
    run('apply', snap, ok=False)
    assert src.read_bytes() == b'new source'
    results.append('拒绝应用到已变化的源文件')
    src.write_bytes(original)
    src.chmod(0o600)
    run('apply', snap, ok=False)
    src.chmod(0o640)
    results.append('拒绝应用到权限已变化的源文件')
    (snap / 'candidate').write_bytes(b'tampered')
    run('apply', snap, ok=False)
    results.append('拒绝被修改的候选快照')
    link = root / 'link.md'
    link.symlink_to(src)
    run('stage', link, draft, root / 'backups', ok=False)
    parentlink = root / 'linked'
    parentlink.symlink_to(root, target_is_directory=True)
    run('stage', parentlink / src.name, draft, root / 'backups', ok=False)
    results.append('拒绝文件与父目录符号链接')
    hard = root / 'hard.md'
    os.link(src, hard)
    run('stage', src, draft, root / 'backups', ok=False)
    hard.unlink()
    results.append('拒绝硬链接')
    draft.write_bytes(b'\x00binary')
    run('stage', src, draft, root / 'backups', ok=False)
    draft.write_bytes(b'\xff')
    run('stage', src, draft, root / 'backups', ok=False)
    results.append('拒绝二进制和无效 UTF-8')
    draft.write_bytes(changed)
    p = subprocess.run(['bash', str(script.parent / 'backup.sh'), str(src), str(draft),
                        str(root / 'backups')], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    snap2 = Path(json.loads(p.stdout)['snapshot'])
    run('apply', snap2)
    p = subprocess.run(['bash', str(script.parent / 'rollback.sh'), str(snap2)],
                       capture_output=True, text=True)
    assert p.returncode == 0 and src.read_bytes() == original, p.stderr
    results.append('Bash 备份与回滚入口')
print('\n'.join('PASS ' + result for result in results))
