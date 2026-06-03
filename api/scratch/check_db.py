import os
import hvac

vault_addr = "http://127.0.0.1:8200"
vault_token = "hvs.6ddxqsuJlRSyuRzOIsXIL9n6"

try:
    client = hvac.Client(url=vault_addr, token=vault_token)
    if client.is_authenticated():
        print("Connected to Vault!")
        try:
            read_response = client.secrets.kv.v2.read_secret_version(path='casmarts/security', mount_point='secret')
            secrets = read_response['data']['data']
            print(f"Vault 'casmarts/security' secret keys: {list(secrets.keys())}")
        except Exception as e:
            print(f"Could not read 'casmarts/security': {e}")
            
        try:
            # Let's list other secrets
            res = client.secrets.kv.v2.list_secrets(path='', mount_point='secret')
            print(f"Vault root secret keys: {res.get('data', {}).get('keys', [])}")
        except Exception as e:
            print(f"Could not list root: {e}")
except Exception as e:
    print(f"Vault connection failed: {e}")
