"""Restore exact prior typesetting assets; no experimental record is modified."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import ssl
import tarfile
import urllib.request
import zipfile
import certifi
from .common import OUT,write_json

ENGINE_URL='https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-aarch64-apple-darwin.tar.gz'
TEMPLATE_URL='https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/26361882/data/v8'
PINS={'tectonic':'b52b5a730e2b0b33087304f7720f649603953f270a6b1c88bb031e1ae01f7f9c',
      'llncs.cls':'04ec99046ad9867f6cd54ffd1ef8c47c767b327d1baec77536db0528cd492fa2',
      'splncs04.bst':'f36c3a17e5304a692706359aafa9de709395a085e579eb47c027095aeaa35174'}


def main():
    tls=ssl.create_default_context(cafile=certifi.where())
    engine=Path('/tmp/nl2lean-tectonic-0.17.0/tectonic');template=Path('/tmp/nl2lean-springer-template')
    template.mkdir(exist_ok=True)
    if not all((template/n).exists() and hashlib.sha256((template/n).read_bytes()).hexdigest()==PINS[n] for n in ['llncs.cls','splncs04.bst']):
        archive=Path('/tmp/nl2lean-springer-current.zip')
        if not archive.exists():
            with urllib.request.urlopen(TEMPLATE_URL,context=tls,timeout=60) as response:archive.write_bytes(response.read())
        with zipfile.ZipFile(archive) as z:
            for name in ['llncs.cls','splncs04.bst']:
                data=z.read(next(n for n in z.namelist() if n.endswith(name)))
                assert hashlib.sha256(data).hexdigest()==PINS[name]
                (template/name).write_bytes(data)
    if not engine.exists():
        release_path=Path('/tmp/nl2lean-tectonic-release.json')
        if not release_path.exists():
            with urllib.request.urlopen('https://api.github.com/repos/tectonic-typesetting/tectonic/releases/tags/tectonic%400.17.0',context=tls,timeout=60) as response:
                release_path.write_bytes(response.read())
        release=json.loads(release_path.read_text())
        asset=next(a for a in release['assets'] if a['browser_download_url']==ENGINE_URL);size=asset['size'];parts=8
        folder=Path('/tmp/nl2lean-tectonic-pinned-parts');folder.mkdir(exist_ok=True)
        def fetch(index):
            start=size*index//parts;end=size*(index+1)//parts-1;path=folder/str(index)
            for attempt in range(4):
                have=path.stat().st_size if path.exists() else 0
                assert have<=end-start+1
                if have==end-start+1:return path
                offset=start+have
                request=urllib.request.Request(ENGINE_URL+f'?verified-part={index}',headers={'Range':f'bytes={offset}-{end}','User-Agent':'publication-build-asset-restore'})
                try:
                    with urllib.request.urlopen(request,context=tls,timeout=90) as response:
                        assert response.status==206 and response.headers['Content-Range']==f'bytes {offset}-{end}/{size}'
                        with path.open('ab') as stream:
                            while chunk:=response.read(65536):stream.write(chunk)
                    break
                except TimeoutError:
                    if attempt==3:raise
            assert path.stat().st_size==end-start+1
            print('Pinned engine download part complete:',index+1,'/',parts,flush=True)
            return path
        with ThreadPoolExecutor(max_workers=parts) as pool:paths=list(pool.map(fetch,range(parts)))
        archive=folder/'complete.tar.gz'
        with archive.open('wb') as stream:
            for path in paths:stream.write(path.read_bytes())
        with tarfile.open(archive) as tar:
            member=next(m for m in tar.getmembers() if Path(m.name).name=='tectonic' and m.isfile())
            data=tar.extractfile(member).read()
        assert hashlib.sha256(data).hexdigest()==PINS['tectonic']
        engine.parent.mkdir(exist_ok=True);engine.write_bytes(data);engine.chmod(0o755)
    assert hashlib.sha256(engine.read_bytes()).hexdigest()==PINS['tectonic']
    record={'post_hoc':True,'all_match_prior_recorded_hashes':True,'sha256':PINS,
        'official_engine_URL':ENGINE_URL,'official_template_URL':TEMPLATE_URL,'not_redistributed':True,
        'scope':'Exact executable/class/bibliography-style bytes restored; original build manifests and experimental records remain unchanged.'}
    previous=OUT/'post_hoc_build_asset_restore.json'
    if previous.exists():assert json.loads(previous.read_text())==record
    else:write_json(previous,record)
    print('Exact pinned engine, Springer class and bibliography style restored.')


if __name__=='__main__':main()
