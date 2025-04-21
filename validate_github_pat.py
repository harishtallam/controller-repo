import requests
import os

def validate_pat(token, label="PAT"):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get("https://api.github.com/user", headers=headers)
    
    if response.status_code == 200:
        scopes = response.headers.get("X-OAuth-Scopes", "Not available")
        user = response.json().get("login", "unknown")
        print(f"✅ {label} is valid. User: {user}")
        print(f"🔑 Scopes: {scopes}")
    else:
        print(f"❌ {label} is INVALID. Status: {response.status_code}")
        print(response.json())

# Example usage
if __name__ == "__main__":
    # You can hardcode, read from environment or prompt the user
    # python validate_pat.py
    # SRC_PAT=ghp_abc...123 TGT_PAT_USERB=ghp_def...456 python validate_pat.py

    src_pat = os.environ.get("SRC_PAT") or input("Enter SRC_PAT: ")
    tgt_pat = os.environ.get("TGT_PAT_USERB") or input("Enter TGT_PAT_USERB: ")
    
    validate_pat(src_pat, label="SRC_PAT")
    validate_pat(tgt_pat, label="TGT_PAT_USERB")
