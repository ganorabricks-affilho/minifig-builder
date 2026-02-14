#!/usr/bin/env python3
"""
BrickStore Database Downloader

This script downloads the latest BrickStore database files from the
rgriebl/brickstore-database GitHub repository releases.

Files downloaded include:
- database-v*.lzma (multiple versions)
- downloads.zip
- regenerate.log
"""

import os
import sys
import requests
from pathlib import Path
from typing import List, Dict
import json
import zipfile
import shutil


# Configuration
GITHUB_REPO = "rgriebl/brickstore-database"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
DATA_FOLDER = "brickstore-data"


def clear_data_folder(folder_path: Path) -> None:
    """Clear all files in the data folder."""
    if folder_path.exists():
        print(f"🗑️  Clearing existing files in {folder_path}...")
        for item in folder_path.iterdir():
            if item.is_file():
                item.unlink()
                print(f"   Deleted: {item.name}")
            elif item.is_dir():
                shutil.rmtree(item)
                print(f"   Deleted: {item.name}/")


def create_data_folder(folder_path: Path) -> None:
    """Create the data folder if it doesn't exist."""
    folder_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Using data folder: {folder_path.absolute()}")


def get_latest_release() -> Dict:
    """Fetch the latest release information from GitHub API."""
    print(f"🔍 Fetching latest release from {GITHUB_REPO}...")
    
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    try:
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"❌ Error fetching release information: {e}")
        sys.exit(1)


def download_file(url: str, filepath: Path) -> bool:
    """Download a file from URL to the specified filepath."""
    filename = filepath.name
    print(f"⬇️  Downloading {filename}...", end=" ", flush=True)
    
    try:
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
        
        # Format file size
        size_mb = downloaded / (1024 * 1024)
        print(f"✅ ({size_mb:.2f} MB)")
        return True
        
    except requests.RequestException as e:
        print(f"❌ Failed: {e}")
        return False


def download_assets(assets: List[Dict], data_folder: Path) -> Path:
    """Download only the downloads.zip file from the release."""
    if not assets:
        print("⚠️  No assets found in the latest release.")
        return None
    
    # Find downloads.zip in assets
    downloads_zip = None
    for asset in assets:
        if asset['name'] == 'downloads.zip':
            downloads_zip = asset
            break
    
    if not downloads_zip:
        print("❌ downloads.zip not found in the latest release.")
        return None
    
    print(f"\n📦 Found downloads.zip file\n")
    
    filename = downloads_zip['name']
    download_url = downloads_zip['browser_download_url']
    filepath = data_folder / filename
    
    if download_file(download_url, filepath):
        return filepath
    else:
        return None


def extract_csv_from_zip(zip_filepath: Path, data_folder: Path) -> bool:
    """Extract M.csv and categories.xml from downloads.zip."""
    print(f"\n📦 Extracting M.csv and categories.xml from {zip_filepath.name}...")
    
    try:
        with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
            target_csv = 'items/M.csv'
            target_categories = 'categories.xml'

            missing_files = [
                name for name in (target_csv, target_categories)
                if name not in zip_ref.namelist()
            ]
            if missing_files:
                print(f"❌ Missing files in zip: {', '.join(missing_files)}")
                return False

            csv_data = zip_ref.read(target_csv)
            csv_filepath = data_folder / 'M.csv'
            with open(csv_filepath, 'wb') as f:
                f.write(csv_data)
            size_kb = len(csv_data) / 1024
            print(f"✅ Extracted M.csv ({size_kb:.2f} KB)")

            categories_data = zip_ref.read(target_categories)
            categories_filepath = data_folder / 'categories.xml'
            with open(categories_filepath, 'wb') as f:
                f.write(categories_data)
            categories_kb = len(categories_data) / 1024
            print(f"✅ Extracted categories.xml ({categories_kb:.2f} KB)")
            return True
            
    except zipfile.BadZipFile as e:
        print(f"❌ Invalid zip file: {e}")
        return False
    except Exception as e:
        print(f"❌ Error extracting file: {e}")
        return False


def list_downloaded_files(data_folder: Path) -> None:
    """List all files in the data folder."""
    files = sorted(data_folder.iterdir())
    if files:
        print(f"\n📋 Files in {data_folder}:")
        for file in files:
            if file.is_file():
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"   - {file.name} ({size_mb:.2f} MB)")


def main():
    """Main execution function."""
    print("=" * 50)
    print("🧱 BrickStore Database Downloader")
    print("=" * 50)
    
    # Setup data folder
    script_dir = Path(__file__).parent
    data_folder = script_dir.parent / DATA_FOLDER
    
    # Clear existing files
    clear_data_folder(data_folder)
    
    # Create data folder
    create_data_folder(data_folder)
    
    # Get latest release information
    release_info = get_latest_release()
    
    release_name = release_info.get('name', 'Unknown')
    release_tag = release_info.get('tag_name', 'Unknown')
    published_at = release_info.get('published_at', 'Unknown')
    
    print(f"✅ Latest release: {release_name}")
    print(f"   Tag: {release_tag}")
    print(f"   Published: {published_at}")
    
    # Download downloads.zip only
    assets = release_info.get('assets', [])
    zip_filepath = download_assets(assets, data_folder)
    
    if not zip_filepath:
        print("❌ Failed to download downloads.zip")
        sys.exit(1)
    
    # Extract M.csv from the zip
    if not extract_csv_from_zip(zip_filepath, data_folder):
        print("❌ Failed to extract M.csv from zip")
        sys.exit(1)
    
    # List downloaded files
    list_downloaded_files(data_folder)
    
    print(f"\n✨ All done! M.csv is ready in: {data_folder.absolute()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Download cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
