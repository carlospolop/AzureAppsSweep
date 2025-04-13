import json

def main():
    # Load dump_scopes_by_apps.json
    with open('dump_scopes_by_apps.json', 'r') as f:
        apps_by_scopes = json.load(f)
    
    # Get scope permission from user
    app_id = input("Enter the app to search for: ")

    if not app_id in apps_by_scopes:
        print(f"App {app_id} not found.")
        return
    
    result = apps_by_scopes[app_id]

    # Find apps that have the specified scope permission
    for req_scope, values in result.items():
        for aud, found_scopes in values.items():
            print(f"- Requesting: {req_scope}")
            print(f"  - Aud: {aud}")
            print(f"  - Found Scopes: {found_scopes}")
            print()
            print()
    
    print()
    print()
    print()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
