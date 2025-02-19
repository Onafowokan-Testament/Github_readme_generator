import io
import os
import zipfile
from typing import Iterator

import streamlit as st
from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.github import GithubTools
from phi.utils.pprint import pprint_run_response

load_dotenv()


ignored_patterns = set()
extract_path = "unzipped_folder"
contents = []
tree_structure = ""
ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}


def load_gitignore(path):
    global ignored_patterns
    gitignore_path = os.path.join(path, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored_patterns.add(line)
    else:
        print(
            ".gitignore files do not exist. Please make sure a gitignore file exist in your root folder"
        )
    return ignored_patterns


def is_ignored(path):
    for pattern in ignored_patterns:
        if pattern in path:
            return True
    return False


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
            ext = item.split(".")[1] if len(item.split(".")) > 1 else ""

            if ext in ALLOWED_EXTENSIONS:
                with open(fullpath, "r", encoding="utf-8") as f:
                    contents.append(f.read())
                tree_structure += f"{indent} 📄 {item} \n"

    return tree_structure, contents


uploaded_zip = st.file_uploader(
    label="upload a ZIP file",
    type=["zip", "rar"],
    help="You can download ziprar to zip your code folder",
)
if uploaded_zip:
    name = uploaded_zip.name.split(".")[0]
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read()), "r") as zip_ref:
        zip_ref.extractall(extract_path)

    st.success(f"Extracted files to `{extract_path}`")

    load_gitignore(f"{extract_path}/{name}")

dir_structure, contents = list_files_with_extensions(extract_path)

print(ignored_patterns)
print(dir_structure)
st.write(dir_structure)
print(contents)


github_access_token = os.getenv("GITHUB_ACCESS_TOKEN")
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError(
        "GROQ_API_KEY environment variable is not set. Please set it in the .env file."
    )

os.environ["GROQ_API_KEY"] = groq_api_key

github = GithubTools(access_token=github_access_token)


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    instructions=[
        f"""
       Final Prompt (For Any Language)
You are an expert in software documentation. I will provide you with:

The cleaned directory structure of a project (only relevant files and folders).
The main source code files in one or more programming languages.
Your task is to:

Detect the programming language(s) used in the project.
Use best practices for documentation in each detected language.
Generate a structured and professional README.md file.

Copy code
{tree_structure}
Main Source Code Files:

csharp
Copy code
{contents}
⚠️ Note: The directory structure has already been cleaned—unnecessary files and folders have been removed. Please focus only on relevant parts.

Now, generate a professional README.md file based on this information, using proper documentation conventions for each detected programming language.

Would you like me to generate a README for a specific project using this approach? 🚀,""",
    ],
    description="You are a professional developer that creates a README for a GitHub project.",
)

# Run the agent to generate the README
response_stream: Iterator[RunResponse] = agent.run(
    "create a readme file for this repository"
)

# Print the response in Markdown format
try:
    pprint_run_response(response_stream, markdown=True)
except Exception as e:
    print(f"An error occurred while trying to create the README file: {e}")
