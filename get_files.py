import os
import subprocess
import tempfile
from typing import Iterator

from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.github import GithubTools
from phi.utils.pprint import pprint_run_response
from helpers import load_gitignore

# Load environment variables
load_dotenv()

github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in the .env file.")

os.environ["GROQ_API_KEY"] = groq_api_key

github = GithubTools(access_token=github_access_token)

# Get the GitHub repository URL from the user
repo_url = input("Enter the GitHub repository URL: ").strip()
if not repo_url:
    raise ValueError("Repository URL cannot be empty.")

# Clone the repository into a temporary directory
temp_dir = tempfile.mkdtemp()
repo_name = repo_url.split("/")[-1].replace(".git", "")
repo_path = os.path.join(temp_dir, repo_name)

print(f"Cloning repository into {repo_path}...")

try:
    subprocess.run(["git", "clone", repo_url, repo_path], check=True)
except subprocess.CalledProcessError as e:
    raise RuntimeError(f"Failed to clone the repository: {e}")

print("Repository cloned successfully.")

# Load ignored files from .gitignore
ignored_patterns = load_gitignore.load_gitignore(repo_path)

ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}
tree_structure = ""
contents = []

def is_ignored(path):
    return any(pattern in path for pattern in ignored_patterns)

def list_files_with_extensions(startpath, indent=""):
    global tree_structure, contents
    for item in sorted(os.listdir(startpath)):
        fullpath = os.path.join(startpath, item)

        if is_ignored(item):
            continue

        if os.path.isdir(fullpath):
            tree_structure += f"{indent}📂 {item}/ \n"
            list_files_with_extensions(fullpath, indent + "   ")
        else:
            ext = item.split(".")[-1]
            if ext in ALLOWED_EXTENSIONS:
                with open(fullpath, "r", encoding="utf-8") as f:
                    contents.append(f.read())
                tree_structure += f"{indent} 📄 {item} \n"

    return tree_structure, contents

dir_structure, contents = list_files_with_extensions(repo_path)

agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    show_tool_calls=True,
    instructions=[
        f"""
        You are an expert in software documentation. I will provide you with:

        1. The cleaned directory structure of a project (only relevant files and folders).
        2. The main source code files in one or more programming languages.

        Your task is to:
        - Detect the programming language(s) used in the project.
        - Use best practices for documentation in each detected language.
        - Generate a structured and professional README.md file.

        The README should include:
        - Title: A short, descriptive title of the project.
        - Description: A brief overview of what the project does.
        - Installation: Steps to install dependencies (if applicable).
        - Usage: Instructions on how to use the project.
        - Directory Structure: A formatted view of the cleaned project structure, with explanations.
        - Features: A list of key functionalities.
        - Example Output: A sample output from the program.
        - Customization: How users can modify or extend the project.
        - Language-Specific Documentation:
          - Python → Include docstrings and module descriptions.
          - JavaScript/TypeScript → Include JSDoc comments.
          - C/C++ → Include Doxygen-style documentation.
          - Java → Include Javadoc-style documentation.
          - Other languages → Use best practices.
        - License: If applicable, include a license section.

        Cleaned Project Directory Structure (Only Relevant Files & Folders):
        ```
        {tree_structure}
        ```

        Main Source Code Files:
        ```
        {contents}
        ```

        Now, generate a professional README.md file using proper documentation conventions.
        """
    ],
    description="You are a professional developer that creates a README for a GitHub project.",
)

# Run the agent to generate the README
response_stream: Iterator[RunResponse] = agent.run("Create a README file for this repository")

# Print the response in Markdown format
try:
    pprint_run_response(response_stream, markdown=True)
except Exception as e:
    print(f"An error occurred while trying to create the README file: {e}")
