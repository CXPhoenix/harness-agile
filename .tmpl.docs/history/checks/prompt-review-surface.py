import json
import subprocess
import tempfile
from pathlib import Path

source = Path(__file__).resolve().parents[3]
results = {}
with tempfile.TemporaryDirectory(prefix='prompt-wip-') as directory:
    repo = Path(directory) / 'repo'
    subprocess.run(['git', 'clone', '--quiet', '--shared', str(source), str(repo)], check=True)
    def git(*args):
        return subprocess.check_output(['git', '-C', str(repo), *args])
    head = git('rev-parse', 'HEAD').decode().strip()
    assert not git('status', '--porcelain=v1', '-uall')
    results['empty_scope'] = True
    readme = repo / 'README.md'
    original = readme.read_bytes()
    readme.write_bytes(original + b'\nStaged fixture\n')
    git('add', '--', 'README.md')
    rules = repo / 'AGENTS.md'
    rules.write_bytes(rules.read_bytes() + b'\nUnstaged fixture\n')
    new = repo / 'new file\nfixture.txt'
    new.write_text('Untracked fixture\n')
    assert not git('diff', f'{head}...{head}', '--')
    assert b'Staged fixture' in git('diff', '--cached', head, '--')
    assert b'Unstaged fixture' in git('diff', '--', 'AGENTS.md')
    names = git('ls-files', '--others', '--exclude-standard', '-z').split(b'\0')
    assert b'new file\nfixture.txt' in names
    assert new.read_text() == 'Untracked fixture\n'
    results['empty_committed_with_all_wip_layers'] = True
    readme.write_bytes(original)
    assert not git('diff', head, '--', 'README.md')
    assert git('diff', '--cached', head, '--', 'README.md')
    assert git('diff', '--', 'README.md')
    results['staged_change_cancelled_in_worktree'] = True
    assert b'AGENTS.md' not in git('diff', head, '--', 'README.md')
    results['path_filter'] = True
    invalid = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--verify', 'missing-fixture-ref^{commit}'], capture_output=True)
    assert invalid.returncode != 0
    results['invalid_ref_rejected'] = True
print(json.dumps(results, indent=2))
