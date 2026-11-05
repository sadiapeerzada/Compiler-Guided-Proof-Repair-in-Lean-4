"""Recreate ignored data-only views from existing approved cached bytes; no download."""
from study_common import *

def main():
    for manifest_path in (HERE/'model_views').glob('*.json'):
        m=read(manifest_path);model=next(v for v in protocol()['models'].values() if v['id']==m['model_id'] and v['revision']==m['revision'])
        source=Path.home()/'.cache/huggingface/hub'/model['cache_name']/'snapshots'/model['revision'];target=HERE/m['view_path'];target.mkdir(parents=True,exist_ok=True)
        for name,expected in m['included_files'].items():
            ensure(not name.endswith('.py'),'Executable snapshot file forbidden')
            path=source/name;ensure(path.is_file() and sha(path)==expected['sha256'],'Approved cached file unavailable or changed: '+name)
            dest=target/name
            if dest.exists():ensure(sha(dest)==expected['sha256'],'Existing model view changed')
            else:dest.symlink_to(path.resolve())
        ensure(not list(target.glob('*.py')),'Python code in model view')
        from local_llm_client import snapshot_inventory
        inventory=snapshot_inventory(target);ensure(inventory['snapshot_revision']==m['revision'],'Revision mismatch')
        print('Verified data-only view:',m['model_id'],m['revision'])

if __name__=='__main__':main()
