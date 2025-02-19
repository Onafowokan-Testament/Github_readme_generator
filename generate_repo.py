import io
import os
import zipfile

import streamlit as st

uploaded_zip = st.file_uploader(
    label="upload a ZIP file",
    type=["zip", "rar"],
    help="You can dowload  ziprar to zip your cold folder ",
)
extract_path = "unzipped_folder"
ignored_patterns = set()


def load_gitignore(path):
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
    print(f"ignored patterns {ignored_patterns}")


if uploaded_zip:
    name = uploaded_zip.name.split(".")[0]
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read()), "r") as zip_ref:
        zip_ref.extractall(extract_path)

    st.success(f"Extracted files to `{extract_path}`")

    load_gitignore(f"{extract_path}/{name}")
    print(f"{extract_path}/{name}")

ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}
tree_structure = ""


def is_ignored(path):
    for pattern in ignored_patterns:
        if pattern in path:
            return True
    return False


def list_files_with_extensions(startpath, indent=""):
    global tree_structure
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
                tree_structure += f"{indent} 📄 {item} \n"
    return tree_structure


dir_structure = list_files_with_extensions(extract_path)


print(ignored_patterns)
st.write(dir_structure)
