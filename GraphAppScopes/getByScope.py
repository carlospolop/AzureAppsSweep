import json

def main():
    # Load dump_scopes_by_apps.json
    with open('dump_scopes_by_apps.json', 'r') as f:
        scopes_by_apps = json.load(f)
    
    # Get scope permission from user
    scope_permission = input("Enter the scope permission to search for: ")

    result = {}

    # Find apps that have the specified scope permission
    for app_id, scope_dict in scopes_by_apps.items():
        for req_scope, values in scope_dict.items():
            for aud, found_scopes in values.items():
                if any(s for s in found_scopes if scope_permission in s):
                    print(f"- App ID: {app_id}\n  - Requesting: {req_scope}\n  - Found Scopes: {found_scopes}")
                    print()
                    print()
                    if not req_scope in result:
                        result[req_scope] = []
                    if not app_id in result[req_scope]:
                        result[req_scope].append(app_id)
    
    print()
    print()
    print()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
