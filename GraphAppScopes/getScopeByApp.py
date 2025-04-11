import json

def main():
    # Load dump_scopes_by_apps.json
    with open('dump_scopes_by_apps.json', 'r') as f:
        scopes_by_apps = json.load(f)
    
    # Get scope permission from user
    scope_permission = input("Enter the scope permission to search for: ")

    # Find apps that have the specified scope permission
    found = False
    for app_id, scope_dict in scopes_by_apps.items():
        if found:
            break
        for req_scope, found_scopes in scope_dict.items():
            if any(s for s in found_scopes if scope_permission in s):
                print(f"- App ID: {app_id}\n  - Requesting: {req_scope}\n  - Found Scopes: {found_scopes}")
                print()
                break
    
if __name__ == "__main__":
    main()
