import os, time, sys, requests, getpass
from urllib.parse import urlparse, unquote
from bs4 import BeautifulSoup
from tqdm import tqdm

# Defines
def make_error_file(error=""):
    with open("ERROR.log", "a") as f:
        f.write(error + "\n")

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.path
    filename = os.path.basename(path)
    return unquote(filename) if filename else "downloaded_file"

def list_github_files_from_html(url): 
    if not url.startswith("https://github.com"): 
        raise ValueError("URL must start with https://github.com") 
    if "/tree/" not in url: 
        raise ValueError("URL must point to a folder in a GitHub repo (contains /tree/)") 
    
    response = requests.get(url) 
    if response.status_code != 200: 
        raise ValueError(f"Failed to access URL: {response.status_code}") 
    
    soup = BeautifulSoup(response.text, "html.parser") 
    files = []

    for item in soup.select("div[role='row'] a[data-turbo-frame]"): 
        href = item.get("href")
        if not href:
            continue
        href = str(href)
        if "/blob/" not in href: 
            continue
        parts = href.split("/blob/")
        raw_url = f"https://raw.githubusercontent.com/{parts[0].strip('/')}/{parts[1]}" 
        files.append(raw_url)

    return files

def download_file(url, save_path, mode):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))

        with open(save_path, "wb") as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=get_filename_from_url(url)
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

        if mode == "def":
            print(f"\nDownloaded: {save_path}")
        elif mode == "SI":
            print(f"\nDownloaded: {get_filename_from_url(url)}")

    except requests.RequestException as e:
        make_error_file(f"Download failed: {url} | {e}")
        raise

def download_github_file(url, folder=".", mode="def"):
    filename = get_filename_from_url(url)
    save_path = os.path.join(folder, filename)
    download_file(url, save_path, mode)
    return save_path

LONG_MODE_REPOS = [
    "https://github.com/thompog/bot-thingy",
    "https://github.com/thompog/LPM",
    "https://github.com/thompog/moter",
    "https://github.com/thompog/list",
    "https://github.com/thompog/idc",
    "https://github.com/thompog/funny-thing-to-play-with",
    "https://github.com/thompog/auto-downloads-all-my-older-programs",
    "https://github.com/thompog/my-installer-files"
]

def list_all_files_from_repo(repo_url, branch="main"):
    """
    Gets raw URLs for all files in the root folder of a repo.
    """
    if repo_url.endswith("/"):
        repo_url = repo_url[:-1]
    tree_url = f"{repo_url}/tree/{branch}/"
    try:
        return list_github_files_from_html(tree_url)
    except Exception as e:
        make_error_file(f"Failed to list files in {repo_url}: {e}")
        return []

# Variables
VALID_MODES = ["def", "short", "long", "forse"]
VALID_DOWNLOAD_MODES = ["def", "SI"]
mode = None
timeout = 12
start_time = time.time()
try:
    username = getpass.getuser()
except OSError as ERROR:
    make_error_file(f"USERNAME is not set: {ERROR}")
    raise OSError("Windows variable 'USERNAME' is not set")
print("def: full path printed")
print("SI: filename only")
download_mode = input("What mode does the prints of downloading be? ").strip()
if download_mode not in VALID_DOWNLOAD_MODES:
    make_error_file("download mode has to be in VALID_DOWNLOAD_MODES: def, SI")
    raise ValueError("Invalid download mode")

cls()

# Function
while mode is None:
    if time.time() - start_time > timeout:
        sys.exit(1)
    try:
        if os.path.exists("mode_A.txt"):
            with open("mode_A.txt", "r") as f:
                content = f.read().strip()
            if content in VALID_MODES:
                mode = content
                break
            else:
                os.remove("mode_A.txt")
        time.sleep(1)
    except OSError as ERROR:
        make_error_file(f"OSError: {ERROR}")
        raise

URLS = {
    "def": [
        "https://github.com/thompog/LPM/releases/download/main_installer/LPM.installer.msi",
        "https://github.com/thompog/idc/blob/main/set-up.bat",
        "https://github.com/thompog/moter/blob/main/page_loader.py",
        "https://github.com/thompog/moter/blob/main/decoder.py"
    ],
    "short": [
        "https://github.com/thompog/LPM/releases/download/main_installer/LPM.installer.msi",
        "https://github.com/thompog/idc/blob/main/set-up.bat"
    ],
    "forse": [
        "https://github.com/thompog/LPM/releases/download/main_installer/LPM.installer.msi",
        "https://github.com/thompog/idc/blob/main/set-up.bat",
        "https://github.com/thompog/moter/blob/main/page_loader.py",
        "https://github.com/thompog/moter/blob/main/decoder.py"
    ]
}

if mode == "long":
    long_mode_urls = []
    for repo in LONG_MODE_REPOS:
        files = list_all_files_from_repo(repo)
        long_mode_urls.extend(files)
    urls = long_mode_urls
else:
    urls = URLS.get(mode, [])

meny_url = len(urls)

while meny_url > 0:
    url = urls[-meny_url]
    success = False
    retries = 0
    file_path = None

    while not success:
        try:
            file_path = download_github_file(url, folder=f"C:\\Users\\{username}\\Downloads", mode=download_mode)
            success = True
        except Exception as e:
            if mode != "forse":
                make_error_file(f"Failed to download {url}: {e}")
                break
            retries += 1
            make_error_file(f"Retrying {url} | Attempt {retries}")
            time.sleep(2)

    if mode in ["def", "forse"] and success and file_path:
        try:
            os.startfile(file_path)
        except Exception as e:
            make_error_file(f"Failed to open {file_path}: {e}")

    meny_url -= 1

print("All downloads finished!")
input("Press Enter to exit...")
