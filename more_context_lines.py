import requests
import sys
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv("local.env")

def get_repo_details_from_pr_link(pr_link):
    parsed_url = urlparse(pr_link)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) < 4 or path_parts[2] != "pull":
        raise ValueError("Invalid PR link format. It should be in the format: https://github.com/owner/repo/pull/number")
    
    owner = path_parts[0]
    repo = path_parts[1]
    pr_number = path_parts[3]
    return owner, repo, pr_number

def fetch_pr_details(owner, repo, pr_number, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch PR details. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    return response.json()

def fetch_pr_diff(owner, repo, pr_number, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Accept": "application/vnd.github.v3.diff"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch PR diff. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    return response.text

def fetch_file_content(owner, repo, file_path, branch, github_token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}?ref={branch}"
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()["content"]
        # Decode the base64 content
        content_str = base64.b64decode(content).decode('utf-8', errors='ignore')
        return content_str
    else:
        print(f"Failed to fetch file content from {url}. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def apply_diff_to_file(diff, file_content, context_lines=5):
    diff_lines = diff.splitlines()
    file_lines = file_content.splitlines()
    output_lines = []

    i = 0
    while i < len(diff_lines):
        line = diff_lines[i]
        if line.startswith('@@'):
            output_lines.append(f"\n{line}\n")

            try:
                original_range = line.split(' ')[1]
                original_start = int(original_range.split(',')[0][1:]) - 1
            except (IndexError, ValueError):
                i += 1
                continue

            pre_context_start = max(0, original_start - context_lines)
            pre_context_end = original_start

            output_lines.extend(file_lines[pre_context_start:pre_context_end])

            i += 1
            chunk_lines = []
            original_lines_count = 0  # To count lines removed from the original content
            while i < len(diff_lines) and not diff_lines[i].startswith('@@'):
                diff_line = diff_lines[i]
                if diff_line.startswith('+'):
                    # chunk_lines.append(f"\033[92m{diff_line}\033[0m")
                    chunk_lines.append(f"{diff_line}")
                elif diff_line.startswith('-'):
                    # chunk_lines.append(f"\033[91m{diff_line}\033[0m")
                    chunk_lines.append(f"{diff_line}")
                    original_lines_count += 1
                else:
                    chunk_lines.append(diff_line)
                    original_lines_count += 1
                i += 1

            output_lines.extend(chunk_lines)

            # To Calculate the line number after the diff chunk in the original file
            original_end = original_start + original_lines_count

            post_context_start = original_end
            post_context_end = min(len(file_lines), post_context_start + context_lines)

            output_lines.extend(file_lines[post_context_start:post_context_end])

        else:
            i += 1

    return "\n".join(output_lines)

def highlight_changes_in_full_files(pr_link, github_token):
    try:
        owner, repo, pr_number = get_repo_details_from_pr_link(pr_link)
        pr_details = fetch_pr_details(owner, repo, pr_number, github_token)
        
        if not pr_details:
            print("PR details could not be fetched.")
            return

        branch = pr_details["base"]["ref"]  # Get the branch from PR details
        pr_diff = fetch_pr_diff(owner, repo, pr_number, github_token)
        
        if pr_diff:
            file_diffs = pr_diff.split("diff --git")
            for file_diff in file_diffs[1:]:
                file_info = file_diff.splitlines()[0]
                file_path = file_info.split(" ")[1][2:]  # Remove 'a/' or 'b/' prefix
                print(f"Fetching file: {file_path} from branch: {branch}")
                full_file_content = fetch_file_content(owner, repo, file_path, branch, github_token)
                
                if full_file_content:
                    print(f"Applying diff to file: {file_path}")
                    highlighted_content = apply_diff_to_file(file_diff, full_file_content, context_lines=5)
                    # print(highlighted_content)
                    print("\n" + "-"*30 + "\n")
                    return highlighted_content

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <PR_LINK>")
        sys.exit(1)

    pr_link = sys.argv[1]
    github_token = os.getenv("GITHUB_API_KEY")  
    
    highlight_changes_in_full_files(pr_link, github_token)