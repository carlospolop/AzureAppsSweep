import json

def main():
    # Load dump_auds_by_apps.json
    with open('dump_auds_by_apps.json', 'r') as f:
        scopes_by_adu = json.load(f)
    
    # Get scope permission from user
    aud_id = input("Enter the aud to search for: ")

    if not aud_id in scopes_by_adu:
        print(f"Aud {aud_id} not found.")
        return
    
    # Get scope permission from user
    scope_permission = input("Enter the scope permission to search for: ")
    
    temp_result = scopes_by_adu[aud_id]
    result = []

    # Find apps that have the specified scope permission
    for app, scopes in temp_result.items():
        if not any(s for s in scopes if scope_permission.lower() in s.lower()):
            continue
    
        if not app in result:
            result.append(app)
        
        print(f"- {app}")
    
    print()
    print()
    print()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
