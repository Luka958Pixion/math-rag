import os
import subprocess
import sys


def poetry_install(dir: str):
    pyproject_path = os.path.join(dir, 'pyproject.toml')

    if not os.path.isfile(pyproject_path):
        print(
            f'Root does not contain pyproject.toml',
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = ['poetry', 'install']

    try:
        subprocess.run(cmd, cwd=dir, check=True)

    except subprocess.CalledProcessError:
        print(f'poetry install failed', file=sys.stderr)
        sys.exit(1)


def pre_commit_install(dir: str):
    cmd = ['poetry', 'run', 'pre-commit', 'install']

    try:
        subprocess.run(cmd, cwd=dir, check=True)

    except subprocess.CalledProcessError:
        print(f'pre-commit install failed', file=sys.stderr)
        sys.exit(1)


def ipykernel_install(dir: str):
    cmd = [
        'poetry',
        'run',
        'python',
        '-m',
        'ipykernel',
        'install',
        '--user',
        '--name=math_rag',
        '--display-name',
        '"Python (math_rag)"',
    ]

    try:
        subprocess.run(cmd, cwd=dir, check=True)

    except subprocess.CalledProcessError:
        print(f'ipykernel install failed', file=sys.stderr)
        sys.exit(1)


def main():
    root_dir = os.path.dirname(os.path.realpath(__file__))

    poetry_install(root_dir)
    pre_commit_install(root_dir)
    ipykernel_install(root_dir)


if __name__ == '__main__':
    main()
