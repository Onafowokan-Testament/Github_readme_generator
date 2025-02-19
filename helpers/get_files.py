import os
from typing import Iterator

from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq
from phi.tools.github import GithubTools
from phi.utils.pprint import pprint_run_response

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
print(github.list_repositories())


name_of_repo = input("Enter the exact name of the repository: ")


agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    tools=[github],
    show_tool_calls=True,
    instructions=[
        f"""
        You are a professional developer tasked with creating a high-quality `README.md` file for the GitHub repository: {name_of_repo}. 
        Your goal is to analyze the content of every file in the repository, understand the purpose of the project, its functionality, and its structure, and then generate a detailed and well-organized README file.

        Follow these steps:

        1. **Analyze the Repository**:
           - Go through every file in the repository.
           - Read and understand the code, comments, and any documentation present in the files.
           - Identify the purpose of the project, its main features, and its overall structure.
           - Pay attention to any configuration files (e.g., `package.json`, `requirements.txt`, `Dockerfile`, etc.) to understand dependencies, setup instructions, and runtime requirements.

        2. **Extract Key Information**:
           - Identify the programming languages, frameworks, and tools used in the project.
           - Extract any important instructions for setting up, configuring, and running the project.
           - Note any examples, usage patterns, or commands provided in the code or documentation.
           - Identify any contributors, licenses, or acknowledgments mentioned in the files.

        3. **Generate the README**:
           - Write a clear and concise title for the project at the top of the README.
           - Provide a brief description of the project, its purpose, and its main features.
           - Include a **Table of Contents** for easy navigation.
           - Add sections for:
             - **Installation**: Step-by-step instructions for setting up the project locally.
             - **Usage**: How to use the project, including examples and commands.
             - **Configuration**: Any configuration options or environment variables required.
             - **Contributing**: Guidelines for contributing to the project.
             - **License**: Information about the project's license.
             - **Acknowledgments**: Credits or acknowledgments, if applicable.
           - Use proper Markdown formatting, including headings, code blocks, lists, and links.

        4. **Ensure Clarity and Completeness**:
           - Make sure the README is easy to read and understand.
           - Include all necessary information for someone new to the project to get started.
           - Avoid unnecessary technical jargon unless it is clearly explained.

        5. **Output the README**:
           - Output the final `README.md` file in Markdown format.
           - Ensure the file is ready to be used in the repository.
        """,
        "Do not create any issues or pull requests unless explicitly asked to do so.",
        f"Just focus on just this particular file and no longer: {name_of_repo}",
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

#just for javascript, typescript and python
# read through the whole directory
# i want to escape common files
# just read common file structure
# read though all tsx, ts, py, js, jsx file,ipynb
#also provide the structure of the the wholse folder

