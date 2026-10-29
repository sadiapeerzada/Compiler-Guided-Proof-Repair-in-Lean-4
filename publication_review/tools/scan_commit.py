"""Read-only tracked-blob publication scan; never writes detected secret values."""
import collections
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[2]
COMMIT = '3b4909a20ed24cafd36cbe029a81f8946bc96d69'
OUT = ROOT / 'publication_review/local'
PATTERNS = {
    'credential_token': r'(?<![A-Za-z0-9])(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gsk_[A-Za-z0-9]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{15,}|AIza[0-9A-Za-z_-]{30,})',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'credential_assignment': r'(?i)(?:api[_-]?key|access[_-]?token|password|secret[_-]?key|authorization)\s*[\"\x27]?\s*[:=]\s*[\"\x27]([^\"\x27\r\n]{8,})',
    'credential_url': r'(?i)https?://[^\s/:@]+:[^\s/@]+@[^\s/]+',
    'email': r'[A-Za-z0-9.!#$%&\x27*+/=?^_`{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',
    'private_local_path': r'(?:/Users/|/home/|[A-Z]:\\Users\\)[^\s\"\x27<>]+',
    'temporary_local_path': r'(?:/private/(?:tmp|var/folders)/|/tmp/)[^\s\"\x27<>]+',
    'personal_owner_identifier': r'(?i)\bsadiapeerzada(?:2006)?\b|\bSadia Peerzada\b',
    'confidentiality_marker': r'(?i)\b(?:confidential|not for distribution|internal only|proprietary|all rights reserved)\b',
    'license_marker': r'(?i)\b(?:Apache[- ]2\.0|CC BY[- ]SA[- ]4\.0|Creative Commons|copyright|redistribution|license|licence)\b',
    'ip_address': r'(?<![0-9])(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?![0-9])',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries = subprocess.check_output(['git', 'ls-tree', '-rz', COMMIT], cwd=ROOT).split(b'\0')
    inventory = []
    with subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        for entry in entries:
            if not entry:
                continue
            meta, path = entry.split(b'\t', 1)
            mode, kind, oid = meta.split()
            if kind != b'blob':
                raise ValueError('Non-blob entry requires manual review')
            proc.stdin.write(oid + b'\n'); proc.stdin.flush()
            header = proc.stdout.readline().split(); data = proc.stdout.read(int(header[2])); assert proc.stdout.read(1) == b'\n'
            rel = path.decode(); suffix = Path(rel).suffix.lower(); extracted = ''
            scan_kind = 'utf8_text'
            try:
                extracted = data.decode('utf-8')
            except UnicodeDecodeError:
                if suffix == '.pdf':
                    from pypdf import PdfReader
                    reader = PdfReader(io.BytesIO(data))
                    extracted = '\n'.join(page.extract_text() or '' for page in reader.pages) + '\n' + str(reader.metadata)
                    scan_kind = 'pdf_extracted_text_and_metadata'
                elif suffix == '.png':
                    from PIL import Image
                    im = Image.open(io.BytesIO(data)); extracted = json.dumps(im.info, default=str) + str(im.getexif())
                    scan_kind = 'png_metadata_only_pixels_not_OCRed'
                else:
                    extracted = data.decode('latin1'); scan_kind = 'binary_byte_text_fallback'
            hits = []
            for category, pattern in PATTERNS.items():
                matches = list(re.finditer(pattern, extracted))
                if matches:
                    hits.append({'category': category, 'count': len(matches), 'locations': [
                        {'line': extracted.count('\n', 0, m.start())+1,
                         'value_sha256': hashlib.sha256(m.group().encode()).hexdigest()}
                        for m in matches]})
            inventory.append({'path': rel, 'git_blob': oid.decode(), 'sha256': hashlib.sha256(data).hexdigest(),
                              'bytes': len(data), 'scan_kind': scan_kind, 'findings': hits})
        proc.stdin.close(); proc.wait()
    summary = {'target_commit': COMMIT, 'tracked_files': len(inventory), 'tracked_bytes': sum(x['bytes'] for x in inventory),
               'file_counts_by_finding': dict(collections.Counter(h['category'] for x in inventory for h in x['findings'])),
               'coverage': dict(collections.Counter(x['scan_kind'] for x in inventory)),
               'limitations': ['Heuristic triage, not proof of absence of secrets or legal clearance.',
                              'PNG pixel contents require visual review; embedded PDF text/metadata extracted, no OCR.',
                              'Commit tree only; excluded git ancestry must not be attached to a public release.',
                              'No detected values are recorded; hashes/line locations allow local review without duplicating secrets.']}
    (OUT/'tracked_file_scan.json').write_text(json.dumps({'summary': summary, 'files': inventory}, indent=2)+'\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
