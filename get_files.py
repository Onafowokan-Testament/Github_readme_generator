import os
from typing import Iterator

from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.github import GithubTools
from phi.utils.pprint import pprint_run_response

from generate_repo import get_content


tree_structure, contents = get_content()
print(tree_structure)
print(contents)
load_dotenv()

# Fetch GitHub and Groq API keys from environment variables
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
    show_tool_calls=True,
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
The README should include:

Title: A short, descriptive title of the project.
Description: A brief overview of what the project does.
Installation: Steps to install dependencies (if applicable).
Usage: Instructions on how to use the project, including input and expected output.
Directory Structure: A formatted view of the cleaned project structure, with explanations of key files.
Features: A list of key functionalities.
Example Output: A sample output from the program.
Customization: How users can modify or extend the project.
Language-Specific Documentation:
If it's Python → Include docstrings and module descriptions.
If it's JavaScript/TypeScript → Include JSDoc comments.
If it's C/C++ → Include Doxygen-style documentation.
If it's Java → Include Javadoc-style documentation.
If it's another language → Use best practices for that language.
License: If applicable, include a license section.
Cleaned Project Directory Structure (Only Relevant Files & Folders):

csharp
Copy code
{tree_structure}
Main Source Code Files:

csharp
Copy code
{contents}
⚠️ Note: The directory structure has already been cleaned—unnecessary files and folders have been removed. Please focus only on relevant parts.

Now, generate a professional README.md file based on this information, using proper documentation conventions for each detected programming language.

Why This Works Well:
✅ Auto-detects languages and applies the right documentation style.
✅ Works for any project, whether Python, JavaScript, C++, Java, Go, Rust, etc.
✅ Ensures best practices are used for each language.

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
