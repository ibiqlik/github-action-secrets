# Manage GitHub Actions secrets

- `listSecrets` - List all secrets (names only) from a repo
- `createSecret` - Create or update a secret in a repo
- `deleteSecret` - Delete a secret


Required Python3.6+

```
pip install -r requirements.txt
python3 run.py
```

## Docker

```
docker build -t ghsecrets .
docker run -it --rm ghsecrets <command> <args>
```
