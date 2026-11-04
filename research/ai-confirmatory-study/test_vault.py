"""Encrypted test payload and source-enforced role/resource checks, not filename secrecy."""
import os
from ai_common import HERE,read,save,canonical
from resource_gate import authorize

def seal(records):
    from cryptography.fernet import Fernet
    private=HERE/'.private';private.mkdir(mode=0o700,exist_ok=True);key_path=private/'test_seal.key'
    if key_path.exists():raise ValueError('Refuse to replace a test seal/key')
    key=Fernet.generate_key();fd=os.open(key_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    with os.fdopen(fd,'wb') as f:f.write(key)
    ciphertext=Fernet(key).encrypt(canonical(records)).decode()
    save(HERE/'runs/test_sealed.json',dict(status='SEALED_TEST_PAYLOAD',ciphertext=ciphertext,count=len(records),access='test_vault.load_test requires test role and separate explicit test authorization'),exclusive=True)

def load_test(role):
    if role!='test':raise ValueError('Calibration/development code cannot open the sealed test payload')
    authorize('test')  # Before reading key or ciphertext.
    from cryptography.fernet import Fernet
    import json
    key=(HERE/'.private/test_seal.key').read_bytes()
    return json.loads(Fernet(key).decrypt(read(HERE/'runs/test_sealed.json')['ciphertext']))
