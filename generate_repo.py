import os
import subprocess
from typing import Iterator
import streamlit as st
from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.github import GithubTools
from phi.utils.pprint import pprint_run_response

load_dotenv()

ignored_patterns = set()
extract_path = "cloned_repo"
tree_structure = ""
ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}
MAX_FILE_SIZE = 5000  # Limit file content size in characters


def clone_repo(repo_url):
    """Clone the GitHub repository into a local directory."""
    if os.path.exists(extract_path):
        subprocess.run(["rm", "-rf", extract_path])
    os.makedirs(extract_path, exist_ok=True)

    try:
        subprocess.run(["git", "clone", repo_url, extract_path], check=True)
        st.success(f"Repository cloned successfully: `{repo_url}`")
    except subprocess.CalledProcessError:
        st.error("Failed to clone the repository. Please check the URL.")
        return None

    return extract_path


def load_gitignore(path):
    """Load patterns from the .gitignore file."""
    gitignore_path = os.path.join(path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)


def is_ignored(path):
    """Check if a file or folder should be ignored."""
    for pattern in ignored_patterns:
        if pattern in path:
            return True
    return False


def summarize_code(file_name, code_content):
    """Ask Groq to summarize the content of a file in a few words."""
    agent = Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        instructions=[
            f"Summarize the following code file in **one or two sentences**:\n\n"
            f"File: `{file_name}`\n"
            f"```\n{code_content}\n```"
        ],
        description="Summarizes code files briefly.",
    )

    response_stream: RunResponse = agent.run("Summarize this file")

    try:
        print(f"response stream {response_stream}")
        print(f"response stream {response_stream.content}")
        return response_stream.content
    except Exception as e:
        print(f"Error summarizing {file_name}: {e}")
        return "No summary available."


def list_files_and_summarize(startpath, indent=""):
    """List relevant files and summarize their contents."""
    global tree_structure
    summaries = {}

    for item in sorted(os.listdir(startpath)):
        fullpath = os.path.join(startpath, item)

        if is_ignored(item):
            continue

        if os.path.isdir(fullpath):
            tree_structure += f"{indent}📂 {item}/ \n"
            list_files_and_summarize(fullpath, indent + "   ")
        else:
            ext = item.split(".")[-1] if "." in item else ""
            if ext in ALLOWED_EXTENSIONS:
                with open(fullpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n... (truncated)"

                    # Summarize file content
                    summary = summarize_code(item, content)
                    summaries[item] = summary

                tree_structure += f"{indent} 📄 {item} \n"

    return tree_structure, summaries


# Get GitHub repository URL from user
repo_url = st.text_input("Enter the GitHub repository URL:")

if repo_url:
    repo_path = clone_repo(repo_url)
    if repo_path:
        load_gitignore(repo_path)
        dir_structure, file_summaries = list_files_and_summarize(repo_path)
        st.write(dir_structure)

# Set up API keys for GitHub and Groq
github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not set in the environment variables.")

github = GithubTools(access_token=github_access_token)

# Convert summaries into a readable format
summary_text = "\n".join(
    [f"**{file}**: {summary}" for file, summary in file_summaries.items()]
)

# Define the AI agent for README generation
agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),  # Use a smaller model
    instructions=[
        f"""
    You are an expert in software documentation. Generate a professional README.md file based on:

    **Project Directory Structure:**
    ```
    {tree_structure}
    ```

    **File Summaries:**
    {summary_text}

    Detect programming languages and use best documentation practices for each. Follow conventions for Python, JavaScript, TypeScript, C++, Java, or any other detected language.
    """
    ],
    description="Creates a README for a GitHub project.",
)

# Run the AI agent to generate the README
if repo_url:
    response_stream: Iterator[RunResponse] = agent.run(
        "Create a README file for this repository"
    )

    try:
        pprint_run_response(response_stream, markdown=True)
    except Exception as e:
        print(f"Error generating README: {e}")
        print(f"Error generating README: {e}")
        print(f"Error generating README: {e}")
