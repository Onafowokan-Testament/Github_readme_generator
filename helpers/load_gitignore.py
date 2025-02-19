import os

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
    return ignored_patterns
