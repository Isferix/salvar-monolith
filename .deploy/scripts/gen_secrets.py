import secrets
import subprocess
import json
from pathlib import Path

PROJECT = "zen"
SUFFIX_LEN = 2  # 2 bytes = 4 hex chars

SECRETS = {
    "api_key": lambda: secrets.token_urlsafe(32),
    "encryption_key": lambda: secrets.token_hex(32),
    "jwt_key": lambda: secrets.token_urlsafe(64),
}

STATE_FILE = Path(".deploy/generated_secrets.json")


def run(cmd: list[str], input_data: str | None = None):
    return subprocess.run(
        cmd,
        input=input_data,
        text=True,
        capture_output=True,
        check=False,
    )


def secret_exists(name: str) -> bool:
    r = run(["docker", "secret", "ls", "--format", "{{.Name}}"])
    return name in r.stdout.splitlines()


def create_secret(name: str, value: str):
    r = run(["docker", "secret", "create", name, "-"], input_data=value)
    if r.returncode != 0:
        raise RuntimeError(f"Failed creating secret {name}: {r.stderr}")


def generate_suffix() -> str:
    return secrets.token_hex(SUFFIX_LEN)


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def main():
    state = load_state()

    for key, generator in SECRETS.items():
        if key in state:
            name = state[key]
            if secret_exists(name):
                print(f"✓ secret exists: {name}")
                continue

        suffix = generate_suffix()
        name = f"{PROJECT}_{key}_{suffix}"

        value = generator()
        print(f"Creating secret: {name}")

        create_secret(name, value)
        state[key] = name

    save_state(state)
    print("Secrets state saved.")


if __name__ == "__main__":
    main()
