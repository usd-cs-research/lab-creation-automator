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
                    'last_name': row['last name'],
                    'first_name': row['first name'],
                    'username': row['username'],
                    'gh_username': row['github username'],
                    'section_number': row['section number']
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
    return parser.parse_args()



def create_gh_repo(repo_dir: str, repo_name: str, gh_username: str, owner: Optional[str] = None):
    full_repo_name = f'{owner}/{repo_name}' if owner is not None else repo_name

    command: list[str] = ['gh', 'repo', 'create', full_repo_name, '--private',
                          f'--source={repo_dir}']

    add_collab_command = ['gh', 'api', '--method', 'PUT',
                          f'repos/{full_repo_name}/collaborators/{gh_username}',
                          '-f', "permission='push'"]

    try:
        print(' '.join(command))
        print(' '.join(add_collab_command))

        # Run the command and capture its output
        """
        result: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            check=True,  # Raise an error for non-zero exit codes
            capture_output=True,
            text=True
        )
        print(f"Success for {repo_name}: {result.stdout.strip()}")
        """

    except subprocess.CalledProcessError as e:
        print(f"Command failed for {repo_name}. Stderr: {e.stderr.strip()}")
    except FileNotFoundError:
        print(f"Error: External program not found.")


def main():
    args = setup_arg_parser()
    user_data = read_user_data(args.csv_file)

    for user in user_data:
        repo_name = f"comp110-{args.semester}-s{user['section_number'].zfill(2)}-{user['username']}"
        create_gh_repo('lab12', repo_name, user['gh_username'], args.owner)


if __name__ == "__main__":
    main()
