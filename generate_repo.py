import io
import os
import zipfile

import streamlit as st

from helpers import load_gitignore

extract_path = "unzipped_folder"
contents = []


uploaded_zip = st.file_uploader(
    label="upload a ZIP file",
    type=["zip", "rar"],
    help="You can dowload  ziprar to zip your cold folder ",
)


if uploaded_zip:
    name = uploaded_zip.name.split(".")[0]
    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(io.BytesIO(uploaded_zip.read()), "r") as zip_ref:
        zip_ref.extractall(extract_path)

    st.success(f"Extracted files to `{extract_path}`")

    ignored_patterns = load_gitignore.load_gitignore(f"{extract_path}/{name}")
    print(f"{extract_path}/{name}")

ALLOWED_EXTENSIONS = {"py", "tsx", "jsx", "ts", "js", "txt"}
tree_structure = ""


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
            ext = item.split(".")[1]
            if ext in ALLOWED_EXTENSIONS:
                if os.path.exists(fullpath):
                    with open(fullpath, "r", encoding="utf-8") as f:
                        contents.append(f.readlines())
                else:
                    print(f"no path like this{fullpath}")

                tree_structure += f"{indent} 📄 {item} \n"

    return tree_structure, contents


dir_structure = list_files_with_extensions(extract_path)


print(ignored_patterns)
print(dir_structure)
st.write(dir_structure)
print(contents)
