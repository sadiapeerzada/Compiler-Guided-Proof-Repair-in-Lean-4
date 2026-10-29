"""Check extracted final PDF text against actual result counts and author metadata."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'data/final_study/v1'


def read(path):
    return json.loads(path.read_text())


def main():
    build = read(BASE / 'paper_build_manifest.json')
    path = ROOT / build['pdf']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != build['pdf_sha256'] or build['exit_code'] != 0:
        raise ValueError('PDF differs from the successful build artifact')
    reader = PdfReader(path)
    pages = [page.extract_text() or '' for page in reader.pages]
    text = '\n'.join(pages)
    normalized = re.sub(r'\s+', '', text)
    results = read(BASE / 'analysis/results.json')
    required = []
    for condition in ['A', 'B', 'C']:
        row = results['conditions'][condition]
        required.append(f"{condition}:{row['successes']}/60({100*row['success_rate']:.1f}%)")
    author = read(BASE / 'author_metadata.json')
    required.extend(re.sub(r'\s+', '', author[key]) for key in ['author_name', 'corresponding_email'])
    missing = [fragment for fragment in required if fragment not in normalized]
    if missing or '@@' in text or '??' in text or not pages:
        raise ValueError('Compiled PDF content check failed: ' + json.dumps({
            'missing_fragments': missing, 'unexpanded_placeholder': '@@' in text,
            'unresolved_reference_marker': '??' in text, 'page_count': len(pages),
        }))
    text_path = BASE / 'compiled_final_manuscript_extracted.txt'
    text_path.write_text(text)
    record = {
        'valid': True, 'pdf_sha256': digest, 'page_count': len(pages),
        'checked_result_fragments': required,
        'extracted_text_sha256': hashlib.sha256(text_path.read_bytes()).hexdigest(),
        'scope': 'Actual compiled A/B/C counts/rates and supplied author identity; placeholder/reference marker check. Source-to-artifact hashes and full numerical evidence are checked separately. This is not venue acceptance or human editorial approval.',
    }
    (BASE / 'final_pdf_validation.json').write_text(json.dumps(record, indent=2) + '\n')
    print('Actual PDF text validated:', len(pages), 'pages; A/B/C counts and author metadata match recorded artifacts.')


if __name__ == '__main__':
    main()
