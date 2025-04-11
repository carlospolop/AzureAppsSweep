import requests
from bs4 import BeautifulSoup
import msal
import jwt
import concurrent.futures
from tqdm import tqdm
from colorama import init, Fore, Style
import json
import tempfile
import threading
import time


lock = threading.Lock()

FOCI_APPS = [
    "04b07795-8ddb-461a-bbee-02f9e1bf7b46", # Azure CLI keep first
    "1950a258-227b-4e31-a9cf-717495945fc2",
    "cf36b471-5b44-428c-9ce7-313bf84528de",
    "2d7f3606-b07d-41d1-b9d2-0d0c9296a6e8",
    "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
    "00b41c95-dab0-4487-9791-b9d2c32c80f2",
    "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    "ab9b8c07-8f02-4f72-87fa-80105867a763",
    "27922004-5251-4030-b22d-91ecd9a37ea4",
    "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
    "0ec893e0-5785-4de6-99da-4ed124e5296c",
    "22098786-6e16-43cc-a27d-191a01a1e3b5",
    "4813382a-8fa7-425e-ab75-3b753aab3abb",
    "4e291c71-d680-4d0e-9640-0a3358e31177",
    "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
    "57336123-6e14-4acc-8dcf-287b6088aa28",
    "66375f6b-983f-4c2c-9701-d680650f588f",
    "844cca35-0656-46ce-b636-13f48b0eecbd",
    "872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
    "87749df4-7ccf-48f8-aa87-704bad0e0e16",
    "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
    "a569458c-7f2b-45cb-bab9-b7dee514d112",
    "af124e86-4e96-495a-b70a-90f90ab96707",
    "b26aadf8-566f-4478-926f-589f601d9c74",
    "be1918be-3fe3-4be9-b32b-b542fc27f02e",
    "cab96880-db5b-4e15-90a7-f3f1d62ffe39",
    "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0",
    "d7b530a4-7680-4c23-a8bf-c52c121d2e87",
    "dd47d17a-3194-4d86-bfd5-c6ae6f5651e3",
    "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
    "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34",
    "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d",
    "0ec893e0-5785-4de6-99da-4ed124e5296c",
    "ecd6b820-32c2-49b6-98a6-444530e5a77a",
    "e9c51622-460d-4d3d-952d-966a5b1da34c",
    "c1c74fed-04c9-4704-80dc-9f79a2e515cb",
    "eb20f3e3-3dce-4d2c-b721-ebb8d4414067"
]

FOUND_SCOPES_BY_APPS = {}
FOUND_APPS_BY_SCOPES = {}

def get_accesstoken_from_foci(client_id, scopes, foci_refresh_token, tenant_id):
    """
    Get access token from FOCI refresh token using MSAL.
    """
    app = msal.PublicClientApplication(
        client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}"
    )
    try:
        tokens = app.acquire_token_by_refresh_token(foci_refresh_token, scopes=scopes)
    except Exception as e:
        if "Connection aborted." in str(e) or "Read timed out" in str(e):
            time.sleep(15)
            return get_accesstoken_from_foci(client_id, scopes, foci_refresh_token, tenant_id)
        if not "API does not accept frozenset" in str(e):
            print(f"{Fore.RED}Error acquiring token: {e}{Style.RESET_ALL}")
        tokens = {}

    return tokens

def get_tokens_from_foci(scope, foci_refresh_token, tenant_id):
    """
    Get a token using FOCI apps for the required resource/scopes.
    """
    global FOUND_SCOPES_BY_APPS
    global FOUND_APPS_BY_SCOPES

    for app_id in FOCI_APPS:
        resp = get_accesstoken_from_foci(
            app_id,
            [scope],
            foci_refresh_token,
            tenant_id
        )
        
        token = resp.get("access_token")
        if token:
            decoded = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
            scopes_str = decoded.get('scp')
            if scopes_str:
                scopes_list = [s.strip() for s in scopes_str.split(",")]
                add_scopes(app_id, scope, scopes_list)
        else:
            if 65002 in resp.get("error_codes", []):
                pass
            else:
                _ = 1

def add_scopes(app_id, req_scope, scopes):
    """
    Add scopes to the global dictionaries with thread-safe locking.
    """
    global FOUND_SCOPES_BY_APPS
    global FOUND_APPS_BY_SCOPES

    with lock:
        # Add to FOUND_SCOPES_BY_APPS
        if app_id not in FOUND_SCOPES_BY_APPS:
            FOUND_SCOPES_BY_APPS[app_id] = {}
        FOUND_SCOPES_BY_APPS[app_id][req_scope] = scopes

        # Add to FOUND_APPS_BY_SCOPES
        if req_scope not in FOUND_APPS_BY_SCOPES:
            FOUND_APPS_BY_SCOPES[req_scope] = {}
        if app_id not in FOUND_APPS_BY_SCOPES[req_scope]:
            FOUND_APPS_BY_SCOPES[req_scope][app_id] = []
        FOUND_APPS_BY_SCOPES[req_scope][app_id] = scopes


def down_graph_scopes():
    """
    Download Microsoft Graph scopes from the permissions reference page.
    """
    url = "https://learn.microsoft.com/en-us/graph/permissions-reference"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    all_scopes_h2 = soup.find('h2', id='all-permissions')
    if not all_scopes_h2:
        raise Exception("The h2 tag with id 'all-permissions' was not found.")

    scopes = []
    for sibling in all_scopes_h2.find_next_siblings():
        if sibling.name == 'h2':
            break
        if sibling.name == 'h3':
            permission = sibling.get_text(strip=True)
            scopes.append(permission)

    print(f"{Fore.GREEN}Extracted {len(scopes)} scopes{Style.RESET_ALL}")
    return scopes

def main():
    # Initialize Colorama for colored outputs
    init(autoreset=True)

    foci_refresh_token = input(f"{Fore.CYAN}Enter the FOCI refresh token: {Style.RESET_ALL}")
    tenant_id = input(f"{Fore.CYAN}Enter the tenant ID: {Style.RESET_ALL}")

    scopes = down_graph_scopes()

    # Process each scope in parallel using a ThreadPoolExecutor with a progress bar
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        list(tqdm(
            executor.map(lambda s: get_tokens_from_foci(s, foci_refresh_token, tenant_id), scopes),
            total=len(scopes),
            desc=f"{Fore.YELLOW}Processing scopes{Style.RESET_ALL}"
        ))

    # Print the found scopes by apps with colored output
    print(f"\n{Fore.GREEN}Found scopes by apps:{Style.RESET_ALL}")
    for app_id, scope_dict in FOUND_SCOPES_BY_APPS.items():
        print(f"{Fore.BLUE}App ID: {app_id}{Style.RESET_ALL}")
        for req_scope, found_scopes in scope_dict.items():
            print(f"  {Fore.MAGENTA}Scope: {req_scope}{Style.RESET_ALL}, Found Scopes: {Fore.YELLOW}{found_scopes}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}Found apps by scopes:{Style.RESET_ALL}")
    for scope, apps in FOUND_APPS_BY_SCOPES.items():
        print(f"{Fore.BLUE}Scope: {scope}{Style.RESET_ALL}")
        for app_id, found_scopes in apps.items():
            print(f"  {Fore.MAGENTA}App ID: {app_id}{Style.RESET_ALL}, Found Scopes: {Fore.YELLOW}{found_scopes}{Style.RESET_ALL}")

    # Dump the global variables to a temporary files
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", prefix="dump_scopes_by_apps_") as temp_file:
        json.dump(FOUND_SCOPES_BY_APPS, temp_file, indent=4)
        temp_filename = temp_file.name
        print(f"\n{Fore.CYAN}Scopes by apps info dumped in JSON dumped to file: {temp_filename}{Style.RESET_ALL}")
    
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json", prefix="dump_apps_by_scopes_") as temp_file:
        json.dump(FOUND_APPS_BY_SCOPES, temp_file, indent=4)
        temp_filename = temp_file.name
        print(f"\n{Fore.CYAN}Apps by scopes info dumped in JSON dumped to file: {temp_filename}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
