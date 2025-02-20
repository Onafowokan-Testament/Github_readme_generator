import os
import shutil
import stat
import subprocess
from typing import Iterator

import streamlit as st
from dotenv import load_dotenv
from phi.agent import Agent, RunResponse
from phi.model.groq import Groq

load_dotenv()

# Allow user to enter their Groq API key
user_groq_api_key = st.text_input("Enter your Groq API Key:", type="password")
if user_groq_api_key:
    os.environ["GROQ_API_KEY"] = user_groq_api_key
total_file_count = 0

# Initialize per-session state instead of globals
if "ignored_patterns" not in st.session_state:
    st.session_state.ignored_patterns = set()
if "tree_structure" not in st.session_state:
    st.session_state.tree_structure = ""

if "current_file_index" not in st.session_state:
    st.session_state.current_file_index = 0

extract_path = "cloned_repo"
ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}
MAX_FILE_SIZE = 5000


def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


# Then, to remove the cloned repository:


def clone_repo(repo_url):
    with st.status("🔄 Cloning repository..."):
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path, onerror=remove_readonly)
        os.makedirs(extract_path, exist_ok=True)

        try:
            subprocess.run(["git", "clone", repo_url, extract_path], check=True)
            st.success(f"✅ Repository cloned successfully: `{repo_url}`")
        except subprocess.CalledProcessError:
            st.error("❌ Failed to clone the repository. Please check the URL.")
            return None
    return extract_path


def count_allowed_files(startpath):
    count = 0
    for root, dirs, files in os.walk(startpath):
        for file in files:
            ext = file.split(".")[-1] if "." in file else ""
            if ext in ALLOWED_EXTENSIONS:
                count += 1
    return count


def summarize_code(file_name, code_content, progress_message=None):
    if progress_message is None:
        progress_message = f"📄 Summarizing `{file_name}`..."
    with st.status(progress_message):
        agent = Agent(
            model=Groq(id="llama-3.3-70b-versatile", api_key=user_groq_api_key),
            instructions=[
                f"Summarize the following code file in **one or two short sentences taking note of library used and what it is doing**:\n\n"
                f"File: `{file_name}`\n"
                f"```\n{code_content}\n```"
            ],
            description="Summarizes code files briefly.",
        )
        response_stream: RunResponse = agent.run("Summarize this file")
        summary = (
            response_stream.content if response_stream else "No summary available."
        )
        st.success(f"✅ `{file_name}` summarized successfully!")
        return summary


def list_files_and_summarize(startpath, indent=""):
    summaries = {}
    for item in sorted(os.listdir(startpath)):
        fullpath = os.path.join(startpath, item)
        if os.path.isdir(fullpath):
            st.session_state.tree_structure += f"{indent}📂 {item}/ \n"
            list_files_and_summarize(fullpath, indent + "   ")
        else:
            ext = item.split(".")[-1] if "." in item else ""
            if ext in ALLOWED_EXTENSIONS:
                with open(fullpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    if len(content) > MAX_FILE_SIZE:
                        content = content[:MAX_FILE_SIZE] + "\n... (truncated)"
                    st.session_state.current_file_index += 1
                    progress_message = f"📄 Summarizing `{item}`... ({st.session_state.current_file_index}/{total_file_count})"
                    summaries[item] = summarize_code(
                        item, content, progress_message=progress_message
                    )
                st.session_state.tree_structure += f"{indent} 📄 {item} \n"
    return st.session_state.tree_structure, summaries


repo_url = st.text_input("Enter the GitHub repository URL:")

if repo_url:
    repo_path = clone_repo(repo_url)
    if repo_path:
        total_file_count = count_allowed_files(repo_path)
        st.write("### 📂 Project Structure:")
        dir_structure, file_summaries = list_files_and_summarize(repo_path)
        st.code(dir_structure, language="markdown")

        st.write("### 📝 Summarizing all files...")
        summary_text = "\n".join(
            [f"**{file}**: {summary}" for file, summary in file_summaries.items()]
        )
        st.success("✅ All files summarized successfully!")

        # Define AI Agent for README Generation
        agent = Agent(
            model=Groq(id="llama-3.3-70b-versatile"),
            instructions=[
                f"""
                # Professional README Generator
                
                You are an **expert in software documentation**. Generate a well-structured and professional `README.md` file for a GitHub repository.
                
                ## Provided Information:
                - **Project Directory Structure:**  
                ```
                {st.session_state.tree_structure}
                ```
                - **Summarized File Contents:**  
                {summary_text}
                
                ## Your Objectives:
                1. **Identify the Programming Language(s).**
                2. **Create a Well-Structured README including:**
                   - Project Title
                   - Description
                   - Installation Instructions
                   - Usage Guide
                   - Features
                   - Example Code Snippets
                   - License (if applicable)
                
                Ensure clarity, proper Markdown formatting, and best practices for open-source projects.
                """
            ],
            description="Creates a README for a GitHub project.",
        )

        # Generate README
        with st.status("🛠️ Generating README..."):
            response_stream: Iterator[RunResponse] = agent.run(
                "Create a README file for this repository"
            )
            readme_content = (
                response_stream.content
                if response_stream
                else "Error generating README."
            )
            st.success("✅ README.md generated successfully!")

        # Display README
        st.write("### 📜 Generated README.md:")
        st.code(readme_content, language="markdown")
