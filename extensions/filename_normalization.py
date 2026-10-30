"""Approved filename-metadata-only normalization; compiler content is invariant."""
import copy
import json
from pathlib import Path
import re


class NormalizationError(ValueError):pass


def assert_private_free(value):
    text=json.dumps(value,ensure_ascii=False)
    if re.search(r'(?i)sadiapeerzada|Sadia Peerzada|(?:/Users/|/home/|/private/var/|/private/tmp/)[^\s"\\]+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}',text):
        raise NormalizationError('Private path or identity outside permitted filename metadata; stop without editing compiler content')


def normalize_diagnostics(diagnostics,root):
    root=Path(root).resolve();result=copy.deepcopy(diagnostics or [])
    for before,after in zip(diagnostics or [],result):
        name=before.get('fileName')
        if name:
            path=Path(name)
            resolved=path.resolve() if path.is_absolute() else (root/path).resolve()
            try:after['fileName']=resolved.relative_to(root).as_posix()
            except ValueError:raise NormalizationError('Diagnostic filename is outside the repository; no consistent approved normalization') from None
        assert {k:v for k,v in before.items() if k!='fileName'}=={k:v for k,v in after.items() if k!='fileName'}
    assert_private_free(result)
    return result


def normalize_verification(value,root):
    result=copy.deepcopy(value)
    if value.get('diagnostics') is not None:result['diagnostics']=normalize_diagnostics(value['diagnostics'],root)
    stdout=value.get('compiler_stdout')
    if stdout:
        try:messages=[json.loads(line) for line in stdout.splitlines() if line.strip()]
        except json.JSONDecodeError:raise NormalizationError('Non-JSON compiler stdout cannot be normalized as filename metadata only') from None
        result['compiler_stdout']=''.join(json.dumps(d,ensure_ascii=False,separators=(',',':'))+'\n' for d in normalize_diagnostics(messages,root))
    unchanged=set(value)-{'diagnostics','compiler_stdout'}
    assert all(value[k]==result[k] for k in unchanged)
    assert_private_free(result)
    return result


def feedback(verification):
    if verification.get('diagnostic_state')!='available':return None
    ds=[d for d in verification.get('diagnostics') or [] if d.get('kind')!='hasSorry']
    return json.dumps({'diagnostic_state':'available','diagnostics':ds},ensure_ascii=False,indent=2) if ds else None
