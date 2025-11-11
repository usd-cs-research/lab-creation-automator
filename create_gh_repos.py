import csv
from typing import Any, Optional
import argparse
import subprocess

def read_user_data(file_path: str) -> list[dict[str, str]]:
    """Reads user data from a CSV file."""
    # Type hint for the variable uses the standard list[dict[str, str]] syntax
    users: list[dict[str, str]] = []
    try:
        with open(file_path, mode='r', newline='') as file:
            # Use DictReader for easy column access by name
            reader = csv.DictReader(file) 
            for row in reader:
                # Store the relevant columns for processing
                users.append({
                    'last_name': row['last name'].strip(),
                    'first_name': row['first name'].strip(),
                    'username': row['username'].strip(),
                    'gh_username': row['github username'].strip(),
                    'section_number': row['section number'].strip()
                })
        return users
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return []

def setup_arg_parser() -> argparse.Namespace:
    """Sets up and parses command line arguments."""
    parser = argparse.ArgumentParser(
        description="Automatically create GitHub repositories based on user data."
    )
    # Required positional argument
    parser.add_argument(
        'semester',
        type=str,
        help='The semester code (e.g., fa24, sp25).'
    )
    # Optional argument
    parser.add_argument(
        '--owner',
        type=str,
        default=None,
        help='The organization or user that will own the repository.'
    )
    # Add an argument for the CSV file path
    parser.add_argument(
        '--csv_file',
        type=str,
        required=True,
        help='Path to the CSV file containing user data.'
    )
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Path to the directory containing the starter git repo.'
    )
    return parser.parse_args()



def run_command(command: str) -> bool:
    print(' '.join(command))
    try:
        # Run the command and capture its output
        result: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            check=True,  # Raise an error for non-zero exit codes
            capture_output=True,
            text=True
        )
        print(f"Success: {result.stdout.strip()}")
        return True

    except Exception as e:
        print(f"Failed: {e.stderr.strip()}")
        return False



def create_gh_repo(source_dir: str, full_repo_name: str, usd_username: str, gh_username: str):

    command: list[str] = ['gh', 'repo', 'create', full_repo_name, '--private',
                          f'--source={source_dir}', '--push',
                          f'--remote=gh_{usd_username}']

    ok = run_command(command)

    if ok:
        add_collab_command = ['gh', 'api', '--method', 'PUT',
                              f'repos/{full_repo_name}/collaborators/{gh_username}',
                              '-f', "permission=push"]

        run_command(add_collab_command)


def main():
    args = setup_arg_parser()
    user_data = read_user_data(args.csv_file)

    for user in user_data:
        repo_name = f"comp110-{args.semester}-s{user['section_number'].zfill(2)}-{user['username']}"
        full_repo_name = f'{args.owner}/{repo_name}' if args.owner is not None else repo_name

        create_gh_repo(args.source, full_repo_name, user['username'], user['gh_username'])


if __name__ == "__main__":
    main()
