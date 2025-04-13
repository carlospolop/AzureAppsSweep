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
    
    result = scopes_by_adu[aud_id]

    # Find apps that have the specified scope permission
    for app, scopes in result.items():
        print(f"- App: {app}")
        print(f"  - Scopes: {scopes}")
        print()
        print()
    
    print()
    print()
    print()
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    main()
