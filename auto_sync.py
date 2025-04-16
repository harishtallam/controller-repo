import os
import subprocess
import shutil
import yaml
import json
import random
import argparse
from datetime import datetime

def run(cmd, check=True):
    print("RUNNING:", " ".join(cmd))
    subprocess.run(cmd, check=check)

parser = argparse.ArgumentParser()
parser.add_argument("--target-user", help="Target GitHub username (lowercase)")
args = parser.parse_args()
target_user = args.target_user.lower() if args.target_user else None

with open("repos.yaml") as f:
    config = yaml.safe_load(f)

state_file = "progress.json"
if os.path.exists(state_file):
    with open(state_file, "r") as f:
        state = json.load(f)
else:
    state = {}

for repo in config["repos"]:
    src = repo["source"]
    tgt = repo["target"]
    branch = repo.get("branch", "main")
    base_path = repo.get("base_path", "days")
    messages = repo.get("messages", ["Daily Commit"])

    if target_user and target_user != tgt.split("/")[0].lower():
        continue

    key = f"{src}->{tgt}"
    last_index = state.get(key, 0)

    if random.random() > 0.7:
        print(f"🎲 Skipping sync for {key} today.")
        continue

    num_to_commit = random.randint(1, 3)
    print(f"➡️ Will commit {num_to_commit} folder(s) for {key}")

    src_repo = src.split("/")[-1]
    tgt_repo = tgt.split("/")[-1]
    src_pat = os.environ["SRC_PAT"]
    tgt_pat_var = f"TGT_PAT_{tgt.split('/')[0].upper()}"
    tgt_pat = os.environ.get(tgt_pat_var)

    if not tgt_pat:
        print(f"❌ Missing PAT for target user {tgt_pat_var}")
        continue

    src_url = f"https://x-access-token:{src_pat}@github.com/{src}.git"
    tgt_url = f"https://x-access-token:{tgt_pat}@github.com/{tgt}.git"

    run(["git", "clone", src_url, src_repo])
    run(["git", "clone", "-b", branch, tgt_url, tgt_repo])

    for i in range(1, num_to_commit + 1):
        folder_index = last_index + i
        folder_to_copy = f"day{folder_index:03d}"
        src_folder = os.path.join(src_repo, base_path, folder_to_copy)
        dst_folder = os.path.join(tgt_repo, folder_to_copy)

        if not os.path.exists(src_folder):
            print(f"⚠️ Folder {folder_to_copy} not found in source repo.")
            continue

        shutil.copytree(src_folder, dst_folder, dirs_exist_ok=True)

        os.chdir(tgt_repo)
        run(["git", "add", folder_to_copy])
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        dynamic_msg = random.choice(messages)
        #commit_msg = f"{dynamic_msg} — {folder_to_copy} at {timestamp}"
        commit_msg = f"{dynamic_msg} — {folder_to_copy}"
        result = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if result.returncode != 0:
            run(["git", "commit", "-m", commit_msg])
            run(["git", "push", "origin", branch])
        else:
            print(f"✅ No changes to commit for {folder_to_copy}.")
        os.chdir("..")

    shutil.rmtree(src_repo)
    shutil.rmtree(tgt_repo)

    state[key] = last_index + num_to_commit

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)