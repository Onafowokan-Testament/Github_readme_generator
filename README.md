# Professional README Generator
=====================================

## Project Title
---------------

Professional README Generator is a web application built using Streamlit, designed to create a well-structured and professional README file for a GitHub repository. The application clones a GitHub repository, summarizes the code files in the repository using the Groq API, and generates a professional README file.

## Description
---------------

The application takes a GitHub repository URL and a Groq API key as input from the user, utilizing the Streamlit library to create a user-friendly interface. The Groq API is used to summarize the code files in the repository, providing a comprehensive overview of the project. The generated README file includes essential information such as project title, description, installation instructions, usage guide, features, and example code snippets.

## Installation Instructions
---------------------------

To run the application, follow these steps:

1. **Clone the repository**: Clone the Professional README Generator repository using Git.
2. **Install dependencies**: Install the required libraries by running `pip install -r requirements.txt`.
3. **Set up Groq API**: Obtain a Groq API key and set it as an environment variable (`GROQ_API_KEY`).
4. **Run the application**: Run the application using `streamlit run generate_repo.py`.

## Usage Guide
--------------

1. **Open the application**: Open the application in your web browser.
2. **Enter repository URL**: Enter the GitHub repository URL you want to generate a README for.
3. **Enter Groq API key**: Enter your Groq API key.
4. **Generate README**: Click the "Generate README" button to create the README file.

## Features
------------

* **Repository cloning**: Clones a GitHub repository using the provided URL.
* **Code summary**: Summarizes the code files in the repository using the Groq API.
* **README generation**: Generates a professional README file based on the summary.
* **User-friendly interface**: Streamlit-based interface for easy user interaction.

## Example Code Snippets
-------------------------

### Generating a README file
```python
import streamlit as st
from generate_repo import generate_readme

# Get repository URL and Groq API key from user
repo_url = st.text_input("Enter repository URL:")
groq_api_key = st.text_input("Enter Groq API key:")

# Generate README file
if st.button("Generate README"):
    readme_content = generate_readme(repo_url, groq_api_key)
    st.code(readme_content)
```

## License
-------

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contributing
------------

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please submit a pull request or issue on GitHub.

## Acknowledgments
---------------

* **Streamlit**: For providing a user-friendly interface for the application.
* **Groq API**: For providing a powerful API for summarizing code files.
* **PyGithub**: For providing a Python library for interacting with GitHub repositories.
