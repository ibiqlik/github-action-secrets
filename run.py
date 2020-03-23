'''
GitHub Actions secrets API

Reference: https://developer.github.com/v3/actions/secrets/
'''

import os
import sys
import argparse
import json
import requests
from nacl import encoding, public

BASEURL="https://api.github.com"


class githubSecrets(object):
    def __init__(self):
        parser = argparse.ArgumentParser(
            description="GitHub Actions Secrets management",
            usage='''<command> [args]

Available commands:
    listSecrets - List all secrets (names only) from a repo
    createSecret - Create or update a secret in a repo
    deleteSecret - Delete a secret
    
Arguments:
    --github_token - Access token with repo scope
    --owner - GitHub owner
    --repo - Git repository
    --secret - Name of the secret to retrieve or create/update
    --value - Secret value to create/update
            '''
        )
        parser.add_argument('command', help="Command to run")
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        getattr(self, args.command)()

    def listSecrets(self):
        parser = argparse.ArgumentParser(
            description="List secrets in repo(s)",
            usage='''listSecrets [args]

Available arguments:
    --github_token
    --owner
    --repo
            '''
        )
        parser.add_argument('--github_token', required=True)
        parser.add_argument('--owner', required=True)
        parser.add_argument('--repo', required=True)
        args = parser.parse_args(sys.argv[2:])
        # print(f'List secrets for {args.owner}/{args.repo}')
        global headers
        headers = {"Authorization": f"token {args.github_token}"}
        r = list_secrets(args.owner, args.repo)
        print(json.dumps(r, indent=4, sort_keys=True))

    def createSecret(self):
        parser = argparse.ArgumentParser(
            description="Create/Update secret",
            usage='''createSecret [args]

Available arguments:
    --github_token
    --owner
    --repo
    --secret
    --value
            '''
        )
        parser.add_argument('--github_token', required=True)
        parser.add_argument('--owner', required=True)
        parser.add_argument('--repo', required=True)
        parser.add_argument('--secret', required=True)
        parser.add_argument('--value', required=True)
        args = parser.parse_args(sys.argv[2:])
        # print(f'Create/Update {args.secret} secret in {args.owner}/{args.repo}')
        global headers
        headers = {"Authorization": f"token {args.github_token}"}
        r = create_secret(args.owner, args.repo, args.secret, args.value)
        print(json.dumps(r, indent=4, sort_keys=True))
        
    def deleteSecret(self):
        parser = argparse.ArgumentParser(
            description="Delete a secret",
            usage='''createSecret [args]

Available arguments:
    --github_token
    --owner
    --repo
    --secret
            '''
        )
        parser.add_argument('--github_token', required=True)
        parser.add_argument('--owner', required=True)
        parser.add_argument('--repo', required=True)
        parser.add_argument('--secret', required=True)
        args = parser.parse_args(sys.argv[2:])
        # print(f'Deleting {args.secret} secret in {args.owner}/{args.repo}')
        global headers
        headers = {"Authorization": f"token {args.github_token}"}
        r = delete_secret(args.owner, args.repo, args.secret)
        print(json.dumps(r, indent=4, sort_keys=True))


def encrypt(key: str, secret_value: str) -> str:
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(key, encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode(), encoding.Base64Encoder())
    return encrypted.decode("utf-8")


def get_pub_key(owner, repo):
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/public-key"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        sys.exit("Could not get public key")
    return json.loads(r.text)


def list_secrets(owner, repo):
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        sys.exit("Could not list secrets")
    return json.loads(r.text)


def get_secret(owner, repo, secret):
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/{secret}"
    r = requests.get(url, headers=headers)
    print(r.text)
    if r.status_code != 200:
        sys.exit("Could not get secret")
    return json.loads(r.text)


def create_secret(owner, repo, secret, value):
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/{secret}"
    pub_key = get_pub_key(owner, repo)
    encrypted_value = encrypt(pub_key["key"], value)
    data = {"encrypted_value": encrypted_value, "key_id": pub_key["key_id"]}
    r = requests.put(url, headers=headers, data=json.dumps(data))
    if r.status_code == 201:
        print(f"Secret {secret} created")
    elif r.status_code == 204:
        print(f"Secret {secret} updated")
    else:
        sys.exit(f"Could not create/update secret {secret}. Response:\n{r.text}")
    return r.ok


def delete_secret(owner, repo, secret):
    url = f"{BASEURL}/repos/{owner}/{repo}/actions/secrets/{secret}"
    r = requests.delete(url, headers=headers)
    if r.status_code != 204:
        sys.exit(f"Could not delete secret {secret}")
    return {
        "ok": r.ok, 
        "status_code": r.status_code, 
        "secret": secret, 
        "action": "delete"
    }


if __name__ == "__main__":
    githubSecrets()
