import requests
import os
import logging
import sys
from dotenv import load_dotenv
import nbformat
from nbconvert import PythonExporter
from openai import OpenAI
from urllib.parse import urlparse, parse_qs
import tiktoken
from more_context_lines import highlight_changes_in_full_files

logging.basicConfig(level=logging.INFO)

load_dotenv("local.env")

def review_code_with_gpt4(code_diff, openai_api_key):
    """
    Sends the code diff to GPT-4 and receives feedback.
    """
    client = OpenAI(api_key=openai_api_key)

    prompt = (
        "You are an AI code reviewer. Please review the following GitHub PR code changes.\n"
        "Your response should follow this structure:\n"
            "1. Summary: \nProvide a brief summary of the changes.\n"
            "2. Issues Found: \nList any issues or potential problems with the code. Use the format:\n "
                "Issue ID <Number>: Description\n"
                "Location: File and line\n"
                "Severity: High/Medium/Low\n"
            "3. Suggested Improvements: \nSuggest specific improvements for the code. Use the format:\n "
                "Improvement ID <Number>: Description\n"
                "Original Code: Code before change\n"
                "Suggested Code: Code after change\n"
                "Benefit: Description\n"
            "4. Conclusion: \nSummarize your overall feedback.\n\n"
            "Additionally, ensure your review covers the following aspects:\n"
                "1) Correct naming conventions (like camel case and snake case)\n"
                "2) Adherence to DRY (Don't Repeat Yourself) principles\n"
                "3) Proper error handling\n"
                "4) Overall maintainability\n"
            f"Code changes:\n{code_diff}\n\n"
            "Provide detailed constructive feedback in the given format."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "Failed to get feedback from GPT-4."

def convert_ipynb_to_py(notebook_content):
    """
    Converts Jupyter notebook content to Python script.
    """
    notebook_node = nbformat.reads(notebook_content, as_version=4)
    exporter = PythonExporter()
    script, _ = exporter.from_notebook_node(notebook_node)
    return script

def filter_diff_based_on_extensions(diff, exclude_extensions, include_extensions):
    """
    Filters out diffs from files with specified extensions.
    """
    filtered_diff = []
    skip_chunk = False
    include_ipynb = False
    ipynb_diff = ""

    for line in diff.split("\n"):
        if line.startswith('diff --git'):
            skip_chunk = any(ext in line for ext in exclude_extensions)
            include_ipynb = any(ext in line for ext in include_extensions)
        if not skip_chunk:
            filtered_diff.append(line)
        elif include_ipynb:
            ipynb_diff += line + "\n"
        elif line == "":
            skip_chunk = False

    return "\n".join(filtered_diff), ipynb_diff

def split_diff_and_review(code_diff, openai_api_key, max_tokens=4335):
    """
    Splits the diff into chunks for review.
    """
    feedbacks = []
    chunk = ""

    for line in code_diff.split("\n"):
        if num_tokens_from_string(chunk, "gpt-4o") + num_tokens_from_string(line, "gpt-4o") + 1 > max_tokens:

            feedback = review_code_with_gpt4(chunk, openai_api_key)
            feedbacks.append(feedback)
            chunk = line
        else:
            chunk += f"\n{line}"

    if chunk:
        feedback = review_code_with_gpt4(chunk, openai_api_key)
        feedbacks.append(feedback)

    return " ".join(feedbacks)

def num_tokens_from_string(string: str, model_name: str) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        
        encoding = tiktoken.get_encoding("cl100k_base")  
    num_tokens = len(encoding.encode(string))
    return num_tokens

def main(pr_link):
    """
    Main function to process the PR link and print feedback.
    """
    parsed_url = urlparse(pr_link)
    path_parts = parsed_url.path.strip("/").split("/")
    if len(path_parts) < 4 or path_parts[2] != "pull":
        logging.error("Invalid PR link format.")
        return

    owner, repo, _, pr_number = path_parts[:4]
    github_token = os.getenv("GITHUB_API_KEY")
    openai_api_key = os.getenv("OPEN_AI_API_KEY")

    logging.info(f"Fetching PR #{pr_number} diff from {owner}/{repo}...")
    
    pr_diff = highlight_changes_in_full_files(pr_link, github_token)
    
    if pr_diff:
        logging.info("Processing diff code...")
        exclude_extensions = [".md", ".lock"]  
        include_extensions = [".ipynb"]
        pr_diff_filtered, ipynb_diff = filter_diff_based_on_extensions(pr_diff, exclude_extensions, include_extensions)
        print(ipynb_diff)

        if ipynb_diff:
            logging.info("Converting .ipynb file changes to Python code...")
            ipynb_script = convert_ipynb_to_py(ipynb_diff)
            pr_diff_filtered += "\n" + ipynb_script

        logging.info("Reviewing code diff...")
        feedback = split_diff_and_review(pr_diff_filtered, openai_api_key)
        print(feedback)
        print("-----------------")
        print(f'Tokens Used: {num_tokens_from_string(feedback, "gpt-4o")}')

if __name__ == "__main__":

    if len(sys.argv) != 2:
        logging.error("Usage: python pr_review.py <PR_LINK>")
        sys.exit(1)
    main(sys.argv[1])