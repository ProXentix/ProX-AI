import os
import glob
import argparse
from typing import List
from backend.utils.hf_hub import upload_to_hf_dataset

def upload_corpus(repo_id: str, corpus_dir: str, dry_run: bool = False):
    print(f"Starting resumable upload of corpus in {corpus_dir} to {repo_id}")
    
    # We will upload train shards, val shards, deduplicated, and manifests
    upload_dirs = ["train", "validation", "manifests", "reports"]
    
    # Try to list remote files to skip existing (a true resumable upload)
    # The Hugging Face API (upload_file) already handles deduplication natively
    # based on SHA256 (it skips if the file exists and hash matches).
    # We will just iterate over all files and call upload_to_hf_dataset.
    
    files_to_upload = []
    for d in upload_dirs:
        path = os.path.join(corpus_dir, d)
        if os.path.exists(path):
            for root, _, files in os.walk(path):
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, corpus_dir)
                    files_to_upload.append((full_path, rel_path))
                    
    total = len(files_to_upload)
    print(f"Found {total} files to upload.")
    
    success_count = 0
    for i, (local_path, remote_path) in enumerate(files_to_upload):
        print(f"[{i+1}/{total}] Uploading {remote_path}...")
        success = upload_to_hf_dataset(
            repo_id=repo_id,
            local_path=local_path,
            path_in_repo=remote_path,
            dry_run=dry_run
        )
        if success:
            success_count += 1
            
    if success_count == total:
        print("\nAll files uploaded successfully.")
        if not dry_run:
            print("You may now safely delete the local corpus directory to save space.")
    else:
        print(f"\nUploaded {success_count}/{total} files. Please rerun to resume.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo_id", type=str, required=True, help="HF Dataset Repo ID")
    parser.add_argument("--corpus_dir", type=str, default="prox_training_corpus", help="Path to corpus")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    
    upload_corpus(args.repo_id, args.corpus_dir, args.dry_run)
