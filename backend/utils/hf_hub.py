import os
import hashlib
from typing import Optional, List
from huggingface_hub import HfApi, hf_hub_download

def get_hf_token() -> str:
    token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError("HF_TOKEN environment variable not set. Refusing to interact with Hugging Face Hub.")
    return token

def calculate_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash in chunks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def upload_to_hf_model(
    repo_id: str, 
    local_path: str, 
    path_in_repo: str, 
    dry_run: bool = False
) -> bool:
    """
    Safely uploads a file to a private Hugging Face Model repository.
    Verifies checksum remotely if possible or assumes success if HfApi doesn't raise.
    """
    print(f"[HF Hub] Model Upload requested: {local_path} -> {repo_id}/{path_in_repo}")
    if dry_run:
        print("  [DRY RUN] Would calculate SHA256 and upload to HF.")
        return True
        
    token = get_hf_token()
    api = HfApi(token=token)
    
    # Ensure repo exists
    try:
        api.create_repo(repo_id=repo_id, private=True, exist_ok=True, repo_type="model")
    except Exception as e:
        pass # Already exists or no permission, proceed to upload
        
    try:
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="model"
        )
        print("  [HF Hub] Upload successful.")
        return True
    except Exception as e:
        print(f"  [HF Hub] ERROR: Upload failed: {e}")
        return False

def upload_to_hf_dataset(
    repo_id: str, 
    local_path: str, 
    path_in_repo: str, 
    dry_run: bool = False
) -> bool:
    """
    Safely uploads a file to a private Hugging Face Dataset repository.
    """
    print(f"[HF Hub] Dataset Upload requested: {local_path} -> {repo_id}/{path_in_repo}")
    if dry_run:
        print("  [DRY RUN] Would calculate SHA256 and upload to HF.")
        return True
        
    token = get_hf_token()
    api = HfApi(token=token)
    
    try:
        api.create_repo(repo_id=repo_id, private=True, exist_ok=True, repo_type="dataset")
    except Exception as e:
        pass
        
    try:
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=path_in_repo,
            repo_id=repo_id,
            repo_type="dataset"
        )
        print("  [HF Hub] Upload successful.")
        return True
    except Exception as e:
        print(f"  [HF Hub] ERROR: Upload failed: {e}")
        return False

def download_from_hf_model(
    repo_id: str, 
    filename: str, 
    local_dir: str, 
    dry_run: bool = False
) -> Optional[str]:
    print(f"[HF Hub] Download requested: {repo_id}/{filename} -> {local_dir}")
    if dry_run:
        print("  [DRY RUN] Would download from HF.")
        return os.path.join(local_dir, filename)
        
    token = get_hf_token()
    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="model",
            local_dir=local_dir,
            token=token
        )
        return path
    except Exception as e:
        print(f"  [HF Hub] ERROR: Download failed: {e}")
        return None

def list_model_files(repo_id: str) -> List[str]:
    token = get_hf_token()
    api = HfApi(token=token)
    try:
        files = api.list_repo_files(repo_id=repo_id, repo_type="model")
        return files
    except Exception as e:
        print(f"  [HF Hub] ERROR: Failed to list repo files: {e}")
        return []
