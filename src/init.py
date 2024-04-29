if __name__ == "__main__":

    import json
    from pathlib import Path

    users_folder = Path("users")

    if not users_folder.exists():
        users_folder.mkdir()

    users_file = Path("users/users.json")

    if not users_file.exists():
        with users_file.open(encoding="utf-8", mode="w") as f:
            json.dump({}, f)

