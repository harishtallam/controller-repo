import os
import shutil
from github import Github
import yaml
import json
from git import Repo

# Helper function to get the next folder
def get_next_day_folder(current):
    if not current:
        return 'day001'
    n = int(current.replace('day', ''))
    if n >= 100:
        return None
    return f"day{n+1:03}"

# Check if folder exists in source repo
def folder_exists_in_source(source_path, folder):
    return os.path.exists(os.path.join(source_path, 'days', folder))

# Clone and commit to the target repo
def sync_repos():
    # Load configuration from the YAML file
    with open("repo_config.yaml", 'r') as file:
        config = yaml.safe_load(file)
    
    # Initialize progress tracking
    if not os.path.exists("progress.json"):
        with open("progress.json", 'w') as progress_file:
            json.dump({}, progress_file)
    
    with open("progress.json", 'r') as progress_file:
        progress = json.load(progress_file)

    for user, mappings in config.items():
        for mapping in mappings['mappings']:
            source_repo = mapping['source']['repo']
            target_repo = mapping['target']['repo']
            source_username = mapping['source']['username']
            target_username = mapping['target']['username']
            target_private = mapping['target'].get('private', False)
            
            # Get the next folder to commit
            key = f"{user}/{source_repo}->{target_repo}"
            current_folder = progress.get(key, None)
            next_folder = get_next_day_folder(current_folder)
            
            if next_folder:
                print(f"Syncing {next_folder} from {source_repo} to {target_repo}")
                
                # Clone source repo (public or private with token)
                g = Github(os.getenv(f"TOKEN_{user.upper()}"))
                source_repo_instance = g.get_repo(f"{source_username}/{source_repo}")
                
                # Local clone
                source_local_path = f"/tmp/{source_repo}"
                if os.path.exists(source_local_path):
                    shutil.rmtree(source_local_path)
                
                os.makedirs(source_local_path)
                Repo.clone_from(source_repo_instance.clone_url, source_local_path, branch='main')
                
                # Check if the folder exists in source repo
                if not folder_exists_in_source(source_local_path, next_folder):
                    print(f"Folder {next_folder} does not exist in the source repo")
                    continue

                # Clone target repo
                target_local_path = f"/tmp/{target_repo}"
                target_repo_instance = g.get_repo(f"{target_username}/{target_repo}")
                
                # Local clone
                if os.path.exists(target_local_path):
                    shutil.rmtree(target_local_path)
                
                os.makedirs(target_local_path)
                Repo.clone_from(target_repo_instance.clone_url, target_local_path, branch='main')

                # Copy the folder to target repo
                source_folder_path = os.path.join(source_local_path, 'days', next_folder)
                target_folder_path = os.path.join(target_local_path, next_folder)

                shutil.copytree(source_folder_path, target_folder_path)
                
                # Commit and push the change
                repo = Repo(target_local_path)
                repo.git.add(A=True)
                repo.index.commit(f"Add {next_folder} from source repo {source_repo}")
                origin = repo.remote(name='origin')
                origin.push()

                # Update progress file
                progress[key] = next_folder
                with open("progress.json", 'w') as progress_file:
                    json.dump(progress, progress_file)

                # Check if all folders are committed (optional)
                if not os.path.exists(os.path.join(source_local_path, 'days', f"day{int(next_folder[3:])+1:03}")):
                    print(f"All folders from {source_repo} have been synced to {target_repo}. Disabling workflow.")
                    with open(".done", "w") as done_file:
                        done_file.write(f"All folders from {source_repo} synced.")

                break  # Once a folder is committed, stop for now

if __name__ == "__main__":
    sync_repos()
