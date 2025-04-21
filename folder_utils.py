import os

def get_next_day_folder(current):
    if not current:
        return 'day001'
    n = int(current.replace('day', ''))
    if n >= 100:
        return None
    return f"day{n+1:03}"

def folder_exists_in_source(source_path, folder):
    return os.path.exists(os.path.join(source_path, 'days', folder))
