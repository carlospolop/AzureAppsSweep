import requests
from pprint import pprint
import argparse
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Rource URIs to authenticate against
RESOURCE_URIS = [
    'https://graph.windows.net/',
    'https://graph.microsoft.com/',
    'https://management.core.windows.net/',
    'https://management.azure.com/',
    'https://outlook.office.com/'
]

# List of Application (Client) IDs
"""
List of Application (Client) IDs from:
- https://github.com/secureworks/family-of-client-ids-research/blob/main/known-foci-clients.csv
- https://www.rickvanrousselt.com/blog/azure-default-service-principals-reference-table/
- https://github.com/dirkjanm/ROADtools/blob/master/roadtx/roadtools/roadtx/firstpartyscopes.json
- https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/governance/verify-first-party-apps-sign-in
"""

APPS = {
    "EnterpriseRoamingandBackup": [
        "60c8bde5-3167-4f92-8fdb-059f6176dc0f"
    ],
    "MicrosoftApprovalManagement": [
        "38049638-cc2c-4cde-abe4-4479d721ed44"
    ],
    "MicrosoftAuthenticationBroker": [
        "29d9ed98-a469-4536-ade2-f981bc1d605e"
    ],
    "MicrosoftAzureCLI": [
        "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    ],
    "MicrosoftAzurePowerShell": [
        "1950a258-227b-4e31-a9cf-717495945fc2"
    ],
    "MicrosoftBingSearch": [
        "cf36b471-5b44-428c-9ce7-313bf84528de"
    ],
    "MicrosoftBingSearchforMicrosoftEdge": [
        "2d7f3606-b07d-41d1-b9d2-0d0c9296a6e8"
    ],
    "MicrosoftDocs": [
        "18fbca16-2224-45f6-85b0-f7bf2b39b3f3"
    ],
    "MicrosoftExchangeRESTAPIBasedPowershell": [
        "fb78d390-0c51-40cd-8e17-fdbfab77341b"
    ],
    "MicrosoftExchangeWebServices": [
        "47629505-c2b6-4a80-adb1-9b3a3d233b7b"
    ],
    "MicrosoftIntuneWindowsAgent": [
        "fc0f3af4-6835-4174-b806-f7db311fd2f3"
    ],
    "MicrosoftOffice": [
        "d3590ed6-52b3-4102-aeff-aad2292ab01c"
    ],
    "MicrosoftPowerBI": [
        "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12"
    ],
    "MicrosoftTeams": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
    ],
    "Office365Management": [
        "00b41c95-dab0-4487-9791-b9d2c32c80f2"
    ],
    "Office365SharePointOnline": [
        "00000003-0000-0ff1-ce00-000000000000"
    ],
    "OneDriveSyncEngine": [
        "ab9b8c07-8f02-4f72-87fa-80105867a763"
    ],
    "OutlookMobile": [
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "SkypeforBusinessOnline": [
        "00000004-0000-0ff1-ce00-000000000000"
    ],
    "UniversalStoreNativeClient": [
        "268761a2-03f3-40df-8a8b-c3db24145b6b"
    ],
    "WindowsDefenderATPPortal": [
        "a3b79187-70b2-4139-83f9-6016c58cd27b"
    ],
    "WindowsSearch": [
        "26a7ee05-5602-4d76-a7ba-eae8b7b67941"
    ],
    "WindowsSpotlight": [
        "1b3c667f-cde3-4090-b60b-3d2abd0117f0"
    ],
    "MicrosoftGraphCommandLineTools": [
        "14d82eec-204b-4c2f-b7e8-296a70dab67e"
    ],
    "OutlookUserSettingsConsumer": [
        "7ae974c5-1af7-4923-af3a-fb1fd14dcb7e"
    ],
    "Vortex[wsfedenabled]": [
        "5572c4c0-d078-44ce-b81c-6cbf8d3ed39e"
    ],
    "OfficeUWPPWA": [
        "0ec893e0-5785-4de6-99da-4ed124e5296c"
    ],
    "WindowsShell": [
        "145fc680-eb72-4bcf-b4d5-8277021a1ce8"
    ],
    "SSOExtensionIntune": [
        "163b648b-025e-455b-9937-a7f39a65d171"
    ],
    "EditorBrowserExtension": [
        "1a20851a-696e-4c7e-96f4-c282dfe48872"
    ],
    "AzureActiveDirectoryPowerShell": [
        "1b730954-1685-4b74-9bfd-dac224a7b894"
    ],
    "MicrosoftTo-Doclient": [
        "22098786-6e16-43cc-a27d-191a01a1e3b5"
    ],
    "ModernWorkplaceCustomerAPINative": [
        "2e307cd5-5d2d-4499-b656-a97de9f52708"
    ],
    "PowerAutomateDesktopForWindows": [
        "386ce8c0-7421-48c9-a1df-2a532400339f"
    ],
    "EnterpriseDashboardProject": [
        "3a4d129e-7f50-4e0d-a7fd-033add0a29f4"
    ],
    "PowerApps-apps.powerapps.com": [
        "3e62f81e-590b-425b-9531-cad6683656cf"
    ],
    "UniversalPrintEnabledPrinter": [
        "417ae6eb-aac8-42c8-900c-0e50debba688"
    ],
    "MicrosoftAuthenticatorApp": [
        "4813382a-8fa7-425e-ab75-3b753aab3abb"
    ],
    "FXIrisClient": [
        "4b0964e4-58f1-47f4-a552-e2e1fc56dcd7"
    ],
    "PowerApps": [
        "4e291c71-d680-4d0e-9640-0a3358e31177"
    ],
    "SurfaceDashboard": [
        "507a7586-da5c-4e86-80f2-2bc2e55ae394"
    ],
    "GraphFilesManager": [
        "52c2e0b5-c7b6-4d11-a89c-21e42bcec444"
    ],
    "MicrosoftWhiteboardClient": [
        "57336123-6e14-4acc-8dcf-287b6088aa28"
    ],
    "SharePointOnlineClient": [
        "57fb890c-0dab-4253-a5e0-7188c88b2bb4"
    ],
    "MicrosoftFlowMobilePROD-GCCH-CN": [
        "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0"
    ],
    "MicrosoftOutlook": [
        "5d661950-3475-41cd-a2c3-d671a3162bc1"
    ],
    "WindowsUpdateforBusinessDeploymentService": [
        "61ae9cd9-7bca-458c-affc-861e2f24ba3b"
    ],
    "MicrosoftPlanner": [
        "66375f6b-983f-4c2c-9701-d680650f588f"
    ],
    "HoloLensCameraRollUpload": [
        "6b11041d-54a2-4c4f-96a2-6053efe46d8b"
    ],
    "WindowsUpdate-Service": [
        "6f0478d5-61a3-4897-a2f2-de09a5a90c7f"
    ],
    "MicrosoftApplicationCommandService": [
        "6f7e0f60-9401-4f5b-98e2-cf15bd5fd5e3"
    ],
    "ZTNADataAcquisition-PROD": [
        "7dd7250c-c317-4bc6-8528-8d27b02707ef"
    ],
    "PowerBIDesktop": [
        "7f67af8a-fedc-4b08-8b4e-37c4d127b6cf"
    ],
    "UniversalPrintConnector": [
        "80331ee5-4436-4815-883e-93bc833a9a15"
    ],
    "MicrosoftStreamMobileNative": [
        "844cca35-0656-46ce-b636-13f48b0eecbd"
    ],
    "OutlookWebAppWidgets": [
        "87223343-80b1-4097-be13-2332ffa1d666"
    ],
    "VisualStudio-Legacy": [
        "872cd9fa-d31f-45e0-9eab-6e460a02d1f1"
    ],
    "MicrosoftTeams-DeviceAdminAgent": [
        "87749df4-7ccf-48f8-aa87-704bad0e0e16"
    ],
    "MicrosoftIntuneCompanyPortal": [
        "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223"
    ],
    "Microsoft.MileIQ": [
        "a25dbca8-4e60-48e5-80a2-0664fdb5c9b6"
    ],
    "AccountsControlUI": [
        "a40d7d7d-59aa-447e-a655-679a4107e548"
    ],
    "YammeriPhone": [
        "a569458c-7f2b-45cb-bab9-b7dee514d112"
    ],
    "MicrosoftPowerQueryforExcel": [
        "a672d62c-fc7b-4e81-a576-e60dc46e951d"
    ],
    "AzureHDInsightonAKSClient": [
        "a6943a7f-5ba0-4a34-bf91-ab439efdda3f"
    ],
    "CommonJobProvider": [
        "a99783bc-5466-4cef-82eb-ebf285d77131"
    ],
    "UniversalPrintPSModule": [
        "aad98258-6bb0-44ed-a095-21506dfb68fe"
    ],
    "VisualStudioCode": [
        "aebc6443-996d-45c2-90f0-388ff96faa56"
    ],
    "OneDriveiOSApp": [
        "af124e86-4e96-495a-b70a-90f90ab96707"
    ],
    "OneDrive": [
        "b26aadf8-566f-4478-926f-589f601d9c74"
    ],
    "OutlookOnlineAdd-inApp": [
        "bc59ab01-8403-45c6-8796-ac3ef710b3e3"
    ],
    "M365ComplianceDriveClient": [
        "be1918be-3fe3-4be9-b32b-b542fc27f02e"
    ],
    "SharePointOnlineClientExtensibility": [
        "c58637bb-e2e1-4312-8a00-04b5ffcd3403"
    ],
    "MicrosoftDefenderPlatform": [
        "cab96880-db5b-4e15-90a7-f3f1d62ffe39"
    ],
    "MicrosoftAzureActiveDirectoryConnect": [
        "cb1056e2-e479-49de-ae31-7812af012ed8"
    ],
    "SharePoint": [
        "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0"
    ],
    "MicrosoftActivityFeedService": [
        "d32c68ad-72d2-4acb-a0c7-46bb2cf93873"
    ],
    "WindowsUpdateforBusinessCloudExtensionsPowerShell": [
        "d5097d05-956f-4ae2-b6a2-eff25f5689b3"
    ],
    "DynamicsRetailCloudPOS": [
        "d5527362-3bc8-4e63-b5b3-606dc14747e9"
    ],
    "MicrosoftEdgeEnterpriseNewTabPage": [
        "d7b530a4-7680-4c23-a8bf-c52c121d2e87"
    ],
    "UniversalPrintNativeClient": [
        "dae89220-69ba-4957-a77a-47b78695e883"
    ],
    "MicrosoftDefenderforMobile": [
        "dd47d17a-3194-4d86-bfd5-c6ae6f5651e3"
    ],
    "MicrosoftDeviceRegistrationClient": [
        "dd762716-544d-4aeb-a526-687b73838a22"
    ],
    "DeviceManagementClient": [
        "de50c81f-5f80-4771-b66b-cebd28ccdfc1"
    ],
    "ModernWorkplaceAppDiagnosticAuthenticator": [
        "e036f41b-7edf-47ee-b373-b4b374a2e33c"
    ],
    "OfficeBrowserExtension": [
        "e28ff72c-58a5-49ba-8125-42ec264d7cd0"
    ],
    "OutlookLite": [
        "e9b154d0-7658-433b-bb25-6b8e0a8a7c59"
    ],
    "MicrosoftEdge": [
        "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34"
    ],
    "MicrosoftTunnel": [
        "eb539595-3fe1-474e-9c1d-feb3625d1be5"
    ],
    "SharePointAndroid": [
        "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d"
    ],
    "IDS-PROD": [
        "f36c30df-d241-4c14-a0ee-752c71e4d3da"
    ],
    "MediaRecordingforDynamics365Sales": [
        "f448d7e5-e313-4f90-a3eb-5dbb3277e4b3"
    ],
    "MicrosoftRemoteAssist": [
        "fca5a20d-55aa-4395-9c2f-c6147f3c9ffa"
    ],
    "Teams Application Gateway": [
        "8a753eec-59bc-4c6a-be91-6bf7bfe0bcdf"
    ],
    "LinkedIn": [
        "f03e9017-17a2-4eea-b8d1-c27da31393d2"
    ],
    "Box": [
        "89220c47-d3bd-4942-a242-bda247a5bc5b"
    ],
    "ISV Portal": [
        "c6871074-3ded-4935-a5dc-b8f8d91d7d06"
    ],
    "BrowserStack": [
        "33261ead-27d2-41e8-97e5-24319826c2af"
    ],
    "Groupies Web Service": [
        "925eb0d0-da50-4604-a19f-bd8de9147958"
    ],
    "Azure ESTS Service": [
        "00000001-0000-0000-c000-000000000000"
    ],
    "MOD Demo Platform UnifiedApiConsumer": [
        "aff75787-e598-43f9-a0ea-7a0ca00ababc"
    ],
    "Kaizala Sync Service": [
        "d82073ec-4d7c-4851-9c5d-5d97a911d71d"
    ],
    "MicrosoftTeamsCortanaSkills": [
        "2bb78a2a-f8f1-4bc3-8ecf-c1e15a0726e6"
    ],
    "Salesforce": [
        "481732f5-fe5b-48c0-8445-d238ab230658"
    ],
    "Microsoft Dynamics CRM Learning Path": [
        "2db8cb1d-fb6c-450b-ab09-49b6ae35186b"
    ],
    "Azure Media Service": [
        "803ee9ca-3f7f-4824-bd6e-0b99d720c35c"
    ],
    "Cortana at Work Bing Services": [
        "22d7579f-06c2-4baa-89d2-e844486adb9d"
    ],
    "YammerOnOls": [
        "c26550d6-bc82-4484-82ca-ac1c75308ca3"
    ],
    "Microsoft Kaizala": [
        "dc3294af-4679-418f-a30c-76948e23fe1c"
    ],
    "Twitter": [
        "1683fa2e-8c1a-41e7-92f9-940cc8852759"
    ],
    "Office UWP PWA": [
        "0ec893e0-5785-4de6-99da-4ed124e5296c"
    ],
    "Microsoft Edge": [
        "e9c51622-460d-4d3d-952d-966a5b1da34c",
        "ecd6b820-32c2-49b6-98a6-444530e5a77a"
    ]
}

# Apps that are flagged as FOCI apps
FOCI_APPS = [
    "00b41c95-dab0-4487-9791-b9d2c32c80f2",
    "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    "1950a258-227b-4e31-a9cf-717495945fc2",
    "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
    "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
    "27922004-5251-4030-b22d-91ecd9a37ea4",
    "4813382a-8fa7-425e-ab75-3b753aab3abb",
    "ab9b8c07-8f02-4f72-87fa-80105867a763",
    "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "872cd9fa-d31f-45e0-9eab-6e460a02d1f1",
    "af124e86-4e96-495a-b70a-90f90ab96707",
    "2d7f3606-b07d-41d1-b9d2-0d0c9296a6e8",
    "844cca35-0656-46ce-b636-13f48b0eecbd",
    "87749df4-7ccf-48f8-aa87-704bad0e0e16",
    "cf36b471-5b44-428c-9ce7-313bf84528de",
    "0ec893e0-5785-4de6-99da-4ed124e5296c",
    "22098786-6e16-43cc-a27d-191a01a1e3b5",
    "4e291c71-d680-4d0e-9640-0a3358e31177",
    "57336123-6e14-4acc-8dcf-287b6088aa28",
    "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0",
    "66375f6b-983f-4c2c-9701-d680650f588f",
    "9ba1a5c7-f17a-4de9-a1f1-6178c8d51223",
    "a40d7d7d-59aa-447e-a655-679a4107e548",
    "a569458c-7f2b-45cb-bab9-b7dee514d112",
    "b26aadf8-566f-4478-926f-589f601d9c74",
    "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
    "d326c1ce-6cc6-4de2-bebc-4591e5e13ef0",
    "e9c51622-460d-4d3d-952d-966a5b1da34c",
    "eb539595-3fe1-474e-9c1d-feb3625d1be5",
    "ecd6b820-32c2-49b6-98a6-444530e5a77a",
    "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d",
    "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34",
    "be1918be-3fe3-4be9-b32b-b542fc27f02e",
    "cab96880-db5b-4e15-90a7-f3f1d62ffe39",
    "d7b530a4-7680-4c23-a8bf-c52c121d2e87",
    "dd47d17a-3194-4d86-bfd5-c6ae6f5651e3",
    "e9b154d0-7658-433b-bb25-6b8e0a8a7c59",
]


INVALID_APPS = {}
VALID_APPS = {}

def authenticate_username_password_native(username, password, client_id, resource_uri):
    """
    Authenticate using username and password with the native app (public client).
    Tries to obtain an access token for the given resource URI.

    Parameters:
    - client_id: The client ID of the application.
    - resource_uri: The resource URI you are trying to access.

    Returns:
    - A dictionary containing the token information if successful.
    - A dictionary with error information if authentication fails.
    """

    data = {
        "client_id": client_id,
        "grant_type": "password",
        "resource": resource_uri,
        "username": username,
        "password": password
    }
    
    tenant = username.split("@")[1]
    authority_url = f'https://login.microsoftonline.com/{tenant}'
    res = requests.post(f"{authority_url}/oauth2/token", data=data)

    is_valid = True
    
    if res.status_code != 200:
        error_msg = res.json().get("error_description")
        error_code = res.json().get("error_codes")[0]
        
        # Map error codes to summaries
        error_summary = ""
        if error_code == 65001:
            error_summary = "Not consented"
        elif error_code == 65002:
            error_summary = "Not consented by resource"
        elif error_code == 7000112:
            error_summary = "Disabled"
        elif error_code == 700016:
            error_summary = "Not installed"
        elif error_code == 50076:
            error_summary = "MFA required"
        elif error_code == 53003:
            error_summary = "Conditional Access Policy"
        elif error_code == 7000218:
            error_summary = "Need client_secret"
            is_valid = False
        else:
            error_summary = "Unknown error"
            #print(error_code)
    
        return {"error_description": error_msg, "error_summary": error_summary, "login_error": True}, is_valid
    
    token_info = res.json()
    token_info["is_foci"] = client_id in FOCI_APPS
    return token_info, is_valid


def main():
    """
    Main function to authenticate with different apps and resource URIs.
    Iterates over all apps and client IDs, attempting to authenticate with each resource URI.
    """

    global INVALID_APPS, VALID_APPS

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Authenticate to apps and resources.')
    parser.add_argument('--username', required=True, type=str, help='Username to login')
    parser.add_argument('--password', required=True, type=str, help='Password to login')
    parser.add_argument('--print-errors', action='store_true', help='Print the whole error description.')
    args = parser.parse_args()

    username = args.username
    password = args.password 

    for name, client_ids in APPS.items():
        for client_id in client_ids:
            print(f"{Fore.CYAN}Logging into app {name} ({client_id}){Style.RESET_ALL}")
            success = False
            
            for res_uri in RESOURCE_URIS:
                token, is_valid = authenticate_username_password_native(username, password, client_id, res_uri)
                
                """ This functionality is here in case we need to test more app IDs
                if is_valid:
                    VALID_APPS[name] = client_ids
                else:
                    INVALID_APPS[name] = client_ids
                """
                
                if token.get("login_error"):
                    if res_uri == RESOURCE_URIS[-1]:
                        error_summary = token.get("error_summary", "Unknown error")
                        print(f"{Fore.RED}{error_summary}{Style.RESET_ALL}")
                        if args.print_errors:
                            print(f"{Fore.YELLOW}{token.get('error_description')}{Style.RESET_ALL}")
                    continue
                
                else:
                    success = True
                    print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
                    if token.get("is_foci"):
                        print(f"{Fore.YELLOW}FOCI token{Style.RESET_ALL}")
                    pprint(token)
                    break  # Stop after first successful authentication
            
            if not success:
                continue
        
        print(f"{Fore.MAGENTA}=============================={Style.RESET_ALL}")
    
    """ This functionality is here in case we need to test more app IDs
    import json
    print(f"{Fore.RED}Invalid apps:{Style.RESET_ALL}")
    print(json.dumps(INVALID_APPS, indent=4))

    print(f"{Fore.GREEN}Valid apps:{Style.RESET_ALL}")
    print(json.dumps(VALID_APPS, indent=4))
    """


if __name__ == "__main__":
    main()


# Well known apps that require client_secret so they are useless for this
"""
{
    "ACOM Azure Website": [
        "23523755-3a2b-41ca-9315-f81f3f566a95"
    ],
    "ADIbizaUX": [
        "74658136-14ec-4630-ad9b-26e160ff0fc6"
    ],
    "AEM-DualAuth": [
        "69893ee3-dd10-4b1c-832d-4870354be3d8"
    ],
    "App Service": [
        "7ab7862c-4c57-491e-8a45-d52a7e023983"
    ],
    "ASM Campaign Servicing": [
        "0cb7b9ec-5336-483b-bc31-b15b5788de71"
    ],
    "Azure Advanced Threat Protection": [
        "7b7531ad-5926-4f2d-8a1d-38495ad33e17"
    ],
    "Azure Data Lake": [
        "e9f49c6b-5ce5-44c8-925d-015017e9f7ad"
    ],
    "Azure Lab Services Portal": [
        "835b2a73-6e10-4aa5-a979-21dfda45231c"
    ],
    "Azure Portal": [
        "c44b4083-3bb0-49c1-b47d-974e53cbdf3c"
    ],
    "Azure SQL Database": [
        "022907d3-0f1b-48f7-badc-1ba6abab6d66"
    ],
    "AzureSupportCenter": [
        "37182072-3c9c-4f6a-a4b3-b3f91cacffce"
    ],
    "Bing": [
        "9ea1ad79-fdb6-4f9a-8bc3-2b70f96e34c7"
    ],
    "ContactsInferencingEmailProcessor": [
        "20a11fe0-faa8-4df5-baf2-f965f8f9972e"
    ],
    "CPIM Service": [
        "bb2a2e3a-c5e7-4f0a-88e0-8e01fd3fc1f4"
    ],
    "CRM Power BI Integration": [
        "e64aa8bc-8eb4-40e2-898b-cf261a25954f"
    ],
    "Dataverse": [
        "00000007-0000-0000-c000-000000000000"
    ],
    "Exchange Admin Center": [
        "497effe9-df71-4043-a8bb-14cf78c4b63b"
    ],
    "FindTime": [
        "f5eaa862-7f08-448c-9c4e-f4047d4d4521"
    ],
    "Focused Inbox": [
        "b669c6ea-1adf-453f-b8bc-6d526592b419"
    ],
    "GroupsRemoteApiRestClient": [
        "c35cb2ba-f88b-4d15-aa9d-37bd443522e1"
    ],
    "HxService": [
        "d9b8ec3a-1e4e-4e08-b3c2-5baf00c0fcb0"
    ],
    "IAM Supportability": [
        "a57aca87-cbc0-4f3c-8b9e-dc095fdc8978"
    ],
    "IrisSelectionFrontDoor": [
        "16aeb910-ce68-41d1-9ac3-9e1673ac9575"
    ],
    "MCAPI Authorization Prod": [
        "d73f4b35-55c9-48c7-8b10-651f6f2acb2e"
    ],
    "Media Analysis and Transformation Service": [
        "944f0bd1-117b-4b1c-af26-804ed95e767e",
        "0cd196ee-71bf-4fd6-a57c-b491ffd4fb1e"
    ],
    "Microsoft 365 Security and Compliance Center": [
        "80ccca67-54bd-44ab-8625-4b79c4dc7775"
    ],
    "Microsoft 365 Support Service": [
        "ee272b19-4411-433f-8f28-5c13cb6fd407"
    ],
    "Microsoft App Access Panel": [
        "0000000c-0000-0000-c000-000000000000"
    ],
    "Microsoft Approval Management": [
        "65d91a3d-ab74-42e6-8a2f-0add61688c74"
    ],
    "MicrosoftAzureActiveAuthn": [
        "0000001a-0000-0000-c000-000000000000"
    ],
    "Microsoft Bing Default Search Engine": [
        "1786c5ed-9644-47b2-8aa0-7201292175b6"
    ],
    "Microsoft Defender for Cloud Apps": [
        "3090ab82-f1c1-4cdf-af2c-5d7a6f3e2cc7"
    ],
    "Microsoft Defender for Identity (formerly Radius Aad Syncer)": [
        "60ca1954-583c-4d1f-86de-39d835f3e452"
    ],
    "Microsoft Dynamics ERP": [
        "00000015-0000-0000-c000-000000000000"
    ],
    "Microsoft Edge Insider Addons Prod": [
        "6253bca8-faf2-4587-8f2f-b056d80998a7"
    ],
    "Microsoft Exchange ForwardSync": [
        "99b904fd-a1fe-455c-b86c-2f9fb1da7687"
    ],
    "Microsoft Exchange Online Protection": [
        "00000007-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Exchange ProtectedServiceHost": [
        "51be292c-a17e-4f17-9a7e-4b661fb16dd2"
    ],
    "Microsoft Forms": [
        "c9a559d2-7aab-4f13-a6ed-e7e9c52aec87"
    ],
    "Microsoft Graph": [
        "00000003-0000-0000-c000-000000000000"
    ],
    "Microsoft Intune Web Company Portal": [
        "74bcdadc-2fdc-4bb3-8459-76d06952a0e9"
    ],
    "Microsoft Office 365 Portal": [
        "00000006-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Office Web Apps Service": [
        "67e3df25-268a-4324-a550-0de1c7f97287"
    ],
    "Microsoft Online Syndication Partner Portal": [
        "d176f6e7-38e5-40c9-8a78-3998aab820e7"
    ],
    "Microsoft password reset service": [
        "93625bc8-bfe2-437a-97e0-3d0060024faa"
    ],
    "Microsoft Storefronts": [
        "28b567f6-162c-4f54-99a0-6887f387bbcc"
    ],
    "Microsoft Stream Portal": [
        "cf53fce8-def6-4aeb-8d30-b158e7b1cf83"
    ],
    "Microsoft Substrate Management": [
        "98db8bd6-0cc0-4e67-9de5-f187f1cd1b41"
    ],
    "Microsoft Support": [
        "fdf9885b-dd37-42bf-82e5-c3129ef5a302"
    ],
    "Microsoft Teams Services": [
        "cc15fd57-2c6c-4117-a88c-83b1d56b4bbe"
    ],
    "Microsoft Teams Web Client": [
        "5e3ce6c0-2b1f-4285-8d4b-75ee78787346"
    ],
    "Microsoft Whiteboard Services": [
        "95de633a-083e-42f5-b444-a4295d8e9314"
    ],
    "O365 SkypeSpaces Ingestion Service": [
        "dfe74da8-9279-44ec-8fb2-2aed9e1c73d0"
    ],
    "O365 Suite UX": [
        "4345a7b9-9a63-4910-a426-35363201d503"
    ],
    "Office 365 Exchange Online": [
        "00000002-0000-0ff1-ce00-000000000000"
    ],
    "Office 365 Search Service": [
        "66a88757-258c-4c72-893c-3e8bed4d6899"
    ],
    "Office Delve": [
        "94c63fef-13a3-47bc-8074-75af8c65887a"
    ],
    "Office Online Add-in SSO": [
        "93d53678-613d-4013-afc1-62e9e444a0a5"
    ],
    "Office Online Client Microsoft Entra ID- Augmentation Loop": [
        "2abdc806-e091-4495-9b10-b04d93c3f040"
    ],
    "Office Online Client Microsoft Entra ID- Loki": [
        "b23dd4db-9142-4734-867f-3577f640ad0c"
    ],
    "Office Online Client Microsoft Entra ID- Maker": [
        "17d5e35f-655b-4fb0-8ae6-86356e9a49f5"
    ],
    "Office Online Client MSA- Loki": [
        "b6e69c34-5f1f-4c34-8cdf-7fea120b8670"
    ],
    "Office Online Core SSO": [
        "243c63a3-247d-41c5-9d83-7788c43f1c43"
    ],
    "Office Online Search": [
        "a9b49b65-0a12-430b-9540-c80b3332c127"
    ],
    "Office.com": [
        "4b233688-031c-404b-9a80-a4f3f2351f90"
    ],
    "Office365 Shell WCSS-Client": [
        "89bee1f7-5e6e-4d8a-9f3d-ecd601259da7"
    ],
    "OfficeClientService": [
        "0f698dd4-f011-4d23-a33e-b36416dcb1e6"
    ],
    "OfficeHome": [
        "4765445b-32c6-49b0-83e6-1d93765276ca"
    ],
    "OfficeShredderWacClient": [
        "4d5c2d63-cf83-4365-853c-925fd1a64357"
    ],
    "OMSOctopiPROD": [
        "62256cef-54c0-4cb4-bcac-4c67989bdc40"
    ],
    "OneNote": [
        "2d4d3d8e-2be3-4bef-9f87-7875a61c29de"
    ],
    "Partner Customer Delegated Admin Offline Processor": [
        "a3475900-ccec-4a69-98f5-a65cd5dc5306"
    ],
    "Password Breach Authenticator": [
        "bdd48c81-3a58-4ea9-849c-ebea7f6b6360"
    ],
    "PeoplePredictions": [
        "35d54a08-36c9-4847-9018-93934c62740c"
    ],
    "Power BI Service": [
        "00000009-0000-0000-c000-000000000000"
    ],
    "Scheduling": [
        "ae8e128e-080f-4086-b0e3-4c19301ada69"
    ],
    "SharedWithMe": [
        "ffcb16e8-f789-467c-8ce9-f826a080d987"
    ],
    "SharePoint Online Web Client Extensibility": [
        "08e18876-6177-487e-b8b5-cf950c1e598c"
    ],
    "Signup": [
        "b4bddae8-ab25-483e-8670-df09b9f1d0ea"
    ],
    "SpoolsProvisioning": [
        "61109738-7d2b-4a0b-9fe3-660b1ff83505"
    ],
    "Sticky Notes API": [
        "91ca2ca5-3b3e-41dd-ab65-809fa3dffffa"
    ],
    "Substrate Context Service": [
        "13937bba-652e-4c46-b222-3003f4d1ff97"
    ],
    "SubstrateDirectoryEventProcessor": [
        "26abc9a8-24f0-4b11-8234-e86ede698878"
    ],
    "Substrate Search Settings Management Service": [
        "a970bac6-63fe-4ec5-8884-8536862c42d4"
    ],
    "Sway": [
        "905fcf26-4eb7-48a0-9ff0-8dcc7194b5ba"
    ],
    "Transcript Ingestion": [
        "97cb1f73-50df-47d1-8fb0-0271f2728514"
    ],
    "Viva Engage (formerly Yammer)": [
        "00000005-0000-0ff1-ce00-000000000000"
    ],
    "WeveEngine": [
        "3c896ded-22c5-450f-91f6-3d1ef0848f6e"
    ],
    "Windows Azure Active Directory": [
        "00000002-0000-0000-c000-000000000000"
    ],
    "Windows Azure Security Resource Provider": [
        "8edd93e1-2103-40b4-bd70-6e34e586362d"
    ],
    "Windows Azure Service Management API": [
        "797f4846-ba00-4fd7-ba43-dac1f8f63013"
    ],
    "Windows Store for Business": [
        "45a330b1-b1ec-4cc1-9161-9f03992aa49f"
    ],
    "Yammer Web": [
        "c1c74fed-04c9-4704-80dc-9f79a2e515cb"
    ],
    "Yammer Web Embed": [
        "e1ef36fd-b883-4dbf-97f0-9ece4b576fc6"
    ],
    "Graph Explorer": [
        "de8bc8b5-d9f9-48b1-a8ad-b748da725064"
    ],
    "Microsoft App Access Panel": [
        "0000000c-0000-0000-c000-000000000000"
    ],
    "Microsoft Teams Retail Service": [
        "75efb5bc-18a1-4e7b-8a66-2ad2503d79c6"
    ],
    "Power BI Premium": [
        "cb4dc29f-0bf4-402a-8b30-7511498ed654"
    ],
    "Office Scripts Service": [
        "62fd1447-0ef3-4ab7-a956-7dd05232ecc1"
    ],
    "Intune DeviceActionService": [
        "18a4ad1e-427c-4cad-8416-ef674e801d32"
    ],
    "Dynamics 365 Business Central": [
        "996def3d-b36c-4153-8607-a6fd3c01b89f"
    ],
    "Skype For Business Powershell Server Application": [
        "39624784-6cbe-4a60-afbe-9f46d10fdb27"
    ],
    "Microsoft.MileIQ.Dashboard": [
        "f7069a8d-9edc-4300-b365-ae53c9627fc4"
    ],
    "Power Query Online GCC-L2": [
        "939fe80f-2eef-464f-b0cf-705d254a2cf2"
    ],
    "O365 UAP Processor": [
        "df09ff61-2178-45d8-888c-4210c1c7b0b2"
    ],
    "Microsoft To-Do": [
        "c830ddb0-63e6-4f22-bd71-2ad47198a23e"
    ],
    "MCAPI Authorization Prod": [
        "d73f4b35-55c9-48c7-8b10-651f6f2acb2e"
    ],
    "O365 Secure Score": [
        "8b3391f4-af01-4ee8-b4ea-9871b2499735"
    ],
    "Microsoft Teams AuditService": [
        "978877ea-b2d6-458b-80c7-05df932f3723"
    ],
    "Demeter.WorkerRole": [
        "3c31d730-a768-4286-a972-43e9b83601cd"
    ],
    "Microsoft Mobile Application Management": [
        "0a5f63c0-b750-4f38-a71c-4fc0d58b89e2"
    ],
    "IDML Graph Resolver Service and CAD": [
        "d88a361a-d488-4271-a13f-a83df7dd99c2"
    ],
    "Permission Service O365": [
        "6d32b7f8-782e-43e0-ac47-aaad9f4eb839"
    ],
    "Skype for Business Management Reporting and Analytics \u2013 Legacy": [
        "de17788e-c765-4d31-aba4-fb837cfff174"
    ],
    "Microsoft Azure Workflow": [
        "00000005-0000-0000-c000-000000000000"
    ],
    "Microsoft Intune API": [
        "c161e42e-d4df-4a3d-9b42-e7a3c31f59d4"
    ],
    "Substrate Instant Revocation Pipeline": [
        "eace8149-b661-472f-b40d-939f89085bd4"
    ],
    "Yggdrasil": [
        "78e7bc61-0fab-4d35-8387-09a8d2f5a59d"
    ],
    "Microsoft Teams User Profile Search Service": [
        "a47591ab-e23e-4ffa-9e1b-809b9067e726"
    ],
    "SalesInsightsWebApp": [
        "b20d0d3a-dc90-485b-ad11-6031e769e221"
    ],
    "Microsoft Parature Dynamics CRM": [
        "8909aac3-be91-470c-8a0b-ff09d669af91"
    ],
    "Application Insights Configuration Service": [
        "6a0a243c-0886-468a-a4c2-eff52c7445da"
    ],
    "Directory and Policy Cache": [
        "7b58f833-4438-494c-a724-234928795a67"
    ],
    "ConnectionsService": [
        "b7912db9-aa33-4820-9d4f-709830fdd78f"
    ],
    "Dynamics CRM Online Administration": [
        "637fcc9f-4a9b-4aaa-8713-a2a3cfda1505"
    ],
    "Microsoft Teams AadSync": [
        "62b732f7-fc71-40bc-b27d-35efcb0509de"
    ],
    "Microsoft Teams Web Client": [
        "e1829006-9cf1-4d05-8b48-2e665cb48e6a"
    ],
    "Microsoft Office Licensing Service vNext": [
        "db55028d-e5ba-420f-816a-d18c861aefdf"
    ],
    "Microsoft Teams Partner Tenant Administration": [
        "0c708d37-30b2-4f22-8168-5d0cba6f37be"
    ],
    "Azns AAD Webhook": [
        "461e8683-5575-4561-ac7f-899cc907d62a"
    ],
    "Export to data lake": [
        "7f15f9d9-cad0-44f1-bbba-d36650e07765"
    ],
    "Windows Store for Business": [
        "45a330b1-b1ec-4cc1-9161-9f03992aa49f"
    ],
    "Microsoft Cognitive Services": [
        "7d312290-28c8-473c-a0ed-8e53749b6d6d"
    ],
    "MicrosoftAzureActiveDirectoryIntegratedApp": [
        "af47b99c-8954-4b45-ab68-8121157418ef"
    ],
    "Microsoft Office Web Apps Service": [
        "67e3df25-268a-4324-a550-0de1c7f97287"
    ],
    "Cortana Experience with O365": [
        "0a0a29f9-0a25-49c7-94bf-c53c3f8fa69d"
    ],
    "Call Recorder": [
        "4580fd1d-e5a3-4f56-9ad1-aab0e3bf8f76"
    ],
    "Microsoft Graph": [
        "00000003-0000-0000-c000-000000000000"
    ],
    "ProjectWorkManagement": [
        "09abbdfd-ed23-44ee-a2d9-a627aa1c90f3"
    ],
    "Office 365 Reports": [
        "507bc9da-c4e2-40cb-96a7-ac90df92685c"
    ],
    "Windows Azure Security Resource Provider": [
        "8edd93e1-2103-40b4-bd70-6e34e586362d"
    ],
    "Bing": [
        "9ea1ad79-fdb6-4f9a-8bc3-2b70f96e34c7"
    ],
    "Common Data Service License Management": [
        "1c2909a7-6432-4263-a70d-929a3c1f9ee5"
    ],
    "Bot Framework Dev Portal": [
        "f3723d34-6ff5-4ceb-a148-d99dcd2511fc"
    ],
    "Dynamics Provision": [
        "39e6ea5b-4aa4-4df2-808b-b6b5fb8ada6f"
    ],
    "Exchange Office Graph Client for AAD \u2013 Noninteractive": [
        "765fe668-04e7-42ba-aec0-2c96f1d8b652"
    ],
    "Microsoft Exchange Online Protection": [
        "00000007-0000-0ff1-ce00-000000000000"
    ],
    "Azure Portal": [
        "c44b4083-3bb0-49c1-b47d-974e53cbdf3c"
    ],
    "Microsoft Stream Service": [
        "2634dd23-5e5a-431c-81ca-11710d9079f4"
    ],
    "DWEngineV2": [
        "441509e5-a165-4363-8ee7-bcf0b7d26739"
    ],
    "Dynamic Alerts": [
        "707be275-6b9d-4ee7-88f9-c0c2bd646e0f"
    ],
    "Microsoft AppPlat EMA": [
        "dee7ba80-6a55-4f3b-a86c-746a9231ae49"
    ],
    "Common Data Service": [
        "00000007-0000-0000-c000-000000000000"
    ],
    "Azure AD Identity Governance": [
        "bf26f092-3426-4a99-abfb-97dad74e661a"
    ],
    "KaizalaActionsPlatform": [
        "9bb724a5-4639-438c-969b-e184b2b1e264"
    ],
    "O365 LinkedIn Connection": [
        "f569b9c7-be15-4e87-86f7-87d30d02090b"
    ],
    "M365 Admin Services": [
        "6b91db1b-f05b-405a-a0b2-e3f60b28d645"
    ],
    "SharePoint Notification Service": [
        "88884730-8181-4d82-9ce2-7d5a7cc7b81e"
    ],
    "Intune CMDeviceService": [
        "14452459-6fa6-4ec0-bc50-1528a1a06bf0"
    ],
    "IC3 Long Running Operations Service": [
        "21a8a852-89f4-4947-a374-b26b2db3d365"
    ],
    "Connectors": [
        "48af08dc-f6d2-435f-b2a7-069abd99c086"
    ],
    "Azure AD Identity Protection": [
        "fc68d9e5-1f76-45ef-99aa-214805418498"
    ],
    "Azure AD Identity Governance Insights": [
        "58c746b0-a0b0-4647-a8f6-12dde5981638"
    ],
    "OfficeClientService": [
        "0f698dd4-f011-4d23-a33e-b36416dcb1e6"
    ],
    "Microsoft.Azure.SyncFabric": [
        "00000014-0000-0000-c000-000000000000"
    ],
    "Signup": [
        "b4bddae8-ab25-483e-8670-df09b9f1d0ea"
    ],
    "M365 License Manager": [
        "aeb86249-8ea3-49e2-900b-54cc8e308f85"
    ],
    "Office 365 Search Service": [
        "66a88757-258c-4c72-893c-3e8bed4d6899"
    ],
    "Teams User Engagement Profile Service": [
        "0f54b75d-4d29-4a92-80ae-106a60cd8f5d"
    ],
    "Microsoft Customer Engagement Portal": [
        "71234da4-b92f-429d-b8ec-6e62652e50d7"
    ],
    "Cortana at Work Service": [
        "2a486b53-dbd2-49c0-a2bc-278bdfc30833"
    ],
    "AAD Terms Of Use": [
        "d52792f4-ba38-424d-8140-ada5b883f293"
    ],
    "Skype for Business": [
        "7557eb47-c689-4224-abcf-aef9bd7573df"
    ],
    "OfficeFeedProcessors": [
        "98c8388a-4e86-424f-a176-d1288462816f"
    ],
    "WindowsDefenderATP": [
        "fc780465-2017-40d4-a0c5-307022471b92"
    ],
    "Log Analytics API": [
        "ca7f3f0b-7d91-482c-8e09-c5d840d0eac5"
    ],
    "Azure AD Notification": [
        "fc03f97a-9db0-4627-a216-ec98ce54e018"
    ],
    "DeploymentScheduler": [
        "8bbf8725-b3ca-4468-a217-7c8da873186e"
    ],
    "Microsoft Flow CDS Integration Service": [
        "0eda3b13-ddc9-4c25-b7dd-2f6ea073d6b7"
    ],
    "OneDrive Web": [
        "33be1cef-03fb-444b-8fd3-08ca1b4d803f"
    ],
    "Yammer": [
        "00000005-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Office 365 Portal": [
        "00000006-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Intune Service Discovery": [
        "9cb77803-d937-493e-9a3b-4b49de3f5a74"
    ],
    "AAD App Management": [
        "f0ae4899-d877-4d3c-ae25-679e38eea492"
    ],
    "Skype Team Substrate connector": [
        "1c0ae35a-e2ec-4592-8e08-c40884656fa5"
    ],
    "Skype for Business Name Dictionary Service": [
        "e95d8bee-4725-4f59-910d-94d415da51b9"
    ],
    "Microsoft.ExtensibleRealUserMonitoring": [
        "e3583ad2-c781-4224-9b91-ad15a8179ba0"
    ],
    "Office 365 Import Service": [
        "3eb95cef-b10f-46fe-94e0-969a3d4c9292"
    ],
    "Azure Storage": [
        "e406a681-f3d4-42a8-90b6-c2b029497af1"
    ],
    "Microsoft Information Protection API": [
        "40775b29-2688-46b6-a3b5-b256bd04df9f"
    ],
    "Azure Notification Service": [
        "b503eb83-1222-4dcc-b116-b98ed5216e05"
    ],
    "Microsoft Discovery Service": [
        "6f82282e-0070-4e78-bc23-e6320c5fa7de"
    ],
    "Windows Azure Active Directory": [
        "00000002-0000-0000-c000-000000000000"
    ],
    "AIGraphClient": [
        "0f6edad5-48f2-4585-a609-d252b1c52770"
    ],
    "Microsoft Teams Mailhook": [
        "51133ff5-8e0d-4078-bcca-84fb7f905b64"
    ],
    "IPSubstrate": [
        "4c8f074c-e32b-4ba7-b072-0f39d71daf51"
    ],
    "Microsoft Intune AndroidSync": [
        "d8877f27-09c0-43aa-8113-40151dae8b14"
    ],
    "Power BI Service": [
        "00000009-0000-0000-c000-000000000000"
    ],
    "Azure Information Protection": [
        "5b20c633-9a48-4a5f-95f6-dae91879051f"
    ],
    "Microsoft SharePoint Online \u2013 SharePoint Home": [
        "dcad865d-9257-4521-ad4d-bae3e137b345"
    ],
    "Microsoft Approval Management": [
        "65d91a3d-ab74-42e6-8a2f-0add61688c74"
    ],
    "Office Change Management": [
        "601d4e27-7bb3-4dee-8199-90d47d527e1c"
    ],
    "Microsoft Exact Data Match Service": [
        "273404b8-7ebc-4360-9f90-b40417f77b53"
    ],
    "Azure Resource Graph": [
        "509e4652-da8d-478d-a730-e9d4a1996ca4"
    ],
    "IAM Supportability": [
        "a57aca87-cbc0-4f3c-8b9e-dc095fdc8978"
    ],
    "O365 Demeter": [
        "982bda36-4632-4165-a46a-9863b1bbcf7d"
    ],
    "Azure Analysis Services": [
        "4ac7d521-0382-477b-b0f8-7e1d95f85ca2"
    ],
    "Microsoft 365 Security and Compliance Center": [
        "80ccca67-54bd-44ab-8625-4b79c4dc7775"
    ],
    "Microsoft Seller Dashboard": [
        "0000000b-0000-0000-c000-000000000000"
    ],
    "Microsoft Cloud App Security": [
        "25a6a87d-1e19-4c71-9cb0-16e88ff608f1"
    ],
    "Microsoft Intune": [
        "0000000a-0000-0000-c000-000000000000"
    ],
    "Microsoft Power BI Information Service": [
        "0000001b-0000-0000-c000-000000000000"
    ],
    "OfficeGraph": [
        "ba23cd2a-306c-48f2-9d62-d3ecd372dfe4"
    ],
    "Service Encryption": [
        "dbc36ae1-c097-4df9-8d94-343c3d091a76"
    ],
    "Microsoft Office Licensing Service Agents": [
        "d7097cd1-c779-44d0-8c71-ab1f8386a97e"
    ],
    "MS Teams Griffin Assistant": [
        "c9224372-5534-42cb-a48b-8db4f4a3892e"
    ],
    "Microsoft.OfficeModernCalendar": [
        "ab27a73e-a3ba-4e43-8360-8bcc717114d8"
    ],
    "Azure Multi-Factor Auth Connector": [
        "1f5530b3-261a-47a9-b357-ded261e17918"
    ],
    "Cortana Runtime Service": [
        "81473081-50b9-469a-b9d8-303109583ecb"
    ],
    "OneNote": [
        "2d4d3d8e-2be3-4bef-9f87-7875a61c29de"
    ],
    "PushChannel": [
        "4747d38e-36c5-4bc3-979b-b0ef74df54d1"
    ],
    "Storage Resource Provider": [
        "a6aa9161-5291-40bb-8c5c-923b567bee3b"
    ],
    "Graph Connector Service": [
        "56c1da01-2129-48f7-9355-af6d59d42766"
    ],
    "Microsoft Teams Graph Service": [
        "ab3be6b7-f5df-413d-ac2d-abf1e3fd9c0b"
    ],
    "Azure Multi-Factor Auth Client": [
        "981f26a1-7f43-403b-a875-f8b09b8cd720"
    ],
    "Centralized Deployment": [
        "257601fd-462f-4a21-b623-7f719f0f90f4"
    ],
    "Skype Business Voice Directory": [
        "27b24f1f-688b-4661-9594-0fdfde972edc"
    ],
    "Office Shredding Service": [
        "b97b6bd4-a49f-4a0c-af18-af507d1da76c"
    ],
    "MileIQ Admin Center": [
        "de096ee1-dae7-4ee1-8dd5-d88ccc473815"
    ],
    "MicrosoftAzureADFulfillment": [
        "f09d1391-098c-47d7-ac7e-6ed2afc5016b"
    ],
    "PowerApps Service": [
        "475226c6-020e-4fb2-8a90-7a972cbfc1d4"
    ],
    "Automated Call Distribution": [
        "11cd3e2e-fccb-42ad-ad00-878b93575e07"
    ],
    "Exchange Office Graph Client for AAD \u2013 Interactive": [
        "6da466b6-1d13-4a2c-97bd-51a99e8d4d74"
    ],
    "Discovery Service": [
        "d29a4c00-4966-492a-84dd-47e779578fb7"
    ],
    "O365 Customer Monitoring": [
        "3aa5c166-136f-40eb-9066-33ac63099211"
    ],
    "Microsoft Azure Policy Insights": [
        "1d78a85d-813d-46f0-b496-dd72f50a3ec0"
    ],
    "Azure Monitor Restricted": [
        "035f9e1d-4f00-4419-bf50-bf2d87eb4878"
    ],
    "Policy Administration Service": [
        "0469d4cd-df37-4d93-8a61-f8c75b809164"
    ],
    "Application Insights API": [
        "f5c26e74-f226-4ae8-85f0-b4af0080ac9e"
    ],
    "Microsoft Exact Data Match Upload Agent": [
        "b51a99a9-ccaa-4687-aa2c-44d1558295f4"
    ],
    "App Studio for Microsoft Teams": [
        "e1979c22-8b73-4aed-a4da-572cc4d0b832"
    ],
    "Targeted Messaging Service": [
        "4c4f550b-42b2-4a16-93f9-fdb9e01bb6ed"
    ],
    "Microsoft Social Engagement": [
        "e8ab36af-d4be-4833-a38b-4d6cf1cfd525"
    ],
    "Microsoft Teams VSTS": [
        "a855a166-fd92-4c76-b60d-a791e0762432"
    ],
    "Microsoft Service Trust": [
        "d6fdaa33-e821-4211-83d0-cf74736489e1"
    ],
    "Azure Advisor": [
        "c39c9bac-9d1f-4dfb-aa29-27f6365e5cb7"
    ],
    "Microsoft Teams Settings Store": [
        "cf6c77f8-914f-4078-baef-e39a5181158b"
    ],
    "Office 365 Client Admin": [
        "3cf6df92-2745-4f6f-bbcf-19b59bcdb62a"
    ],
    "Microsoft Teams ADL": [
        "30e31aeb-977f-4f4f-a483-b61e8377b302"
    ],
    "Azure Smart Alerts": [
        "3af5a1e8-2459-45cb-8683-bcd6cccbcc13"
    ],
    "Microsoft Teams Services": [
        "cc15fd57-2c6c-4117-a88c-83b1d56b4bbe"
    ],
    "Power Query Online": [
        "f3b07414-6bf4-46e6-b63f-56941f3f4128"
    ],
    "Microsoft Dynamics 365 Apps Integration": [
        "44a02aaa-7145-4925-9dcd-79e6e1b94eff"
    ],
    "Microsoft Teams AuthSvc": [
        "a164aee5-7d0a-46bb-9404-37421d58bdf7"
    ],
    "ReportReplica": [
        "f25a7567-8ec5-4582-8a65-bfd66b0530cc"
    ],
    "Office Enterprise Protection Service": [
        "55441455-2f54-42b5-bc99-93e21cd4ae28"
    ],
    "Office 365 Exchange Online": [
        "00000002-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Intune Enrollment": [
        "d4ebce55-015a-49b5-a083-c84d1797ae8c"
    ],
    "Microsoft Invoicing": [
        "b6b84568-6c01-4981-a80f-09da9a20bbed"
    ],
    "AzureLockbox": [
        "a0551534-cfc9-4e1f-9a7a-65093b32bb38"
    ],
    "DevilFish": [
        "eaf8a961-f56e-47eb-9ffd-936e22a554ef"
    ],
    "Skype Teams Calling API Service": [
        "26a18ebc-cdf7-4a6a-91cb-beb352805e81"
    ],
    "Reply-At-Mention": [
        "18f36947-75b0-49fb-8d1c-29584a55cac5"
    ],
    "Microsoft Teams Chat Aggregator": [
        "b1379a75-ce5e-4fa3-80c6-89bb39bf646c"
    ],
    "Microsoft Rights Management Services": [
        "00000012-0000-0000-c000-000000000000"
    ],
    "Microsoft Stream Portal": [
        "cf53fce8-def6-4aeb-8d30-b158e7b1cf83"
    ],
    "Microsoft Teams \u2013 Teams And Channels Service": [
        "b55b276d-2b09-4ad2-8de5-f09cf24ffba9"
    ],
    "Request Approvals Read Platform": [
        "d8c767ef-3e9a-48c4-aef9-562696539b39"
    ],
    "Windows Azure Application Insights": [
        "11c174dc-1945-4a9a-a36b-c79a0f246b9b"
    ],
    "Microsoft Device Directory Service": [
        "8f41dc7c-542c-4bdd-8eb3-e60543f607ca"
    ],
    "Azure Advanced Threat Protection": [
        "7b7531ad-5926-4f2d-8a1d-38495ad33e17"
    ],
    "Skype for Business Application Configuration Service": [
        "00f82732-f451-4a01-918c-0e9896e784f9"
    ],
    "Device Registration Service": [
        "01cb2876-7ebd-4aa4-9cc9-d28bd4d359a9"
    ],
    "AAD Request Verification Service \u2013 PROD": [
        "c728155f-7b2a-4502-a08b-b8af9b269319"
    ],
    "Microsoft.MileIQ.RESTService": [
        "b692184e-b47f-4706-b352-84b288d2d9ee"
    ],
    "Azure AD Identity Governance \u2013 User Management": [
        "ec245c98-4a90-40c2-955a-88b727d97151"
    ],
    "Microsoft People Cards Service": [
        "394866fc-eedb-4f01-8536-3ff84b16be2a"
    ],
    "Microsoft Flow Portal": [
        "6204c1d1-4712-4c46-a7d9-3ed63d992682"
    ],
    "Microsoft Information Protection Sync Service": [
        "870c4f2e-85b6-4d43-bdda-6ed9a579b725"
    ],
    "AzureSupportCenter": [
        "37182072-3c9c-4f6a-a4b3-b3f91cacffce"
    ],
    "Microsoft Office Licensing Service": [
        "8d3a7d3c-c034-4f19-a2ef-8412952a9671"
    ],
    "Data Classification Service": [
        "7c99d979-3b9c-4342-97dd-3239678fb300"
    ],
    "Microsoft Fluid Framework Preview": [
        "660d4be7-2665-497f-9611-a42c2668dbce"
    ],
    "Office 365 Management APIs": [
        "c5393580-f805-4401-95e8-94b7a6ef2fc2"
    ],
    "Sway": [
        "905fcf26-4eb7-48a0-9ff0-8dcc7194b5ba"
    ],
    "Microsoft Intune Checkin": [
        "26a4ae64-5862-427f-a9b0-044e62572a4f"
    ],
    "Microsoft Azure AD Identity Protection": [
        "a3dfc3c6-2c7d-4f42-aeec-b2877f9bce97"
    ],
    "Microsoft Mobile Application Management Backend": [
        "354b5b6d-abd6-4736-9f51-1be80049b91f"
    ],
    "OneProfile Service": [
        "b2cc270f-563e-4d8a-af47-f00963a71dcd"
    ],
    "Microsoft.DynamicsMarketing": [
        "9b06ebd4-9068-486b-bdd2-dac26b8a5a7a"
    ],
    "OCPS Checkin Service": [
        "23c898c1-f7e8-41da-9501-f16571f8d097"
    ],
    "Microsoft Flow CDS Integration Service TIP1": [
        "eacba838-453c-4d3e-8c6a-eb815d3469a3"
    ],
    "Microsoft Teams Shifts": [
        "aa580612-c342-4ace-9055-8edee43ccb89"
    ],
    "IAMTenantCrawler": [
        "66244124-575c-4284-92bc-fdd00e669cea"
    ],
    "AADPremiumService": [
        "bf4fa6bf-d24c-4d1c-8cfd-12063dd646b2"
    ],
    "Windows Azure Service Management API": [
        "797f4846-ba00-4fd7-ba43-dac1f8f63013"
    ],
    "Microsoft Whiteboard Services": [
        "95de633a-083e-42f5-b444-a4295d8e9314"
    ],
    "Microsoft Flow Service": [
        "7df0a125-d3be-4c96-aa54-591f83ff541c"
    ],
    "Azure AD Identity Governance \u2013 SPO Management": [
        "396e7f4b-41ea-4851-b04d-65de6cf1b4a3"
    ],
    "Microsoft Intune Advanced Threat Protection Integration": [
        "794ded15-70c6-4bcd-a0bb-9b7ad530a01a"
    ],
    "Microsoft Policy Insights Provider Data Plane": [
        "8cae6e77-e04e-42ce-b5cb-50d82bce26b1"
    ],
    "Microsoft.Azure.DataMarket": [
        "00000008-0000-0000-c000-000000000000"
    ],
    "Azure AD Identity Governance \u2013 Entitlement Management": [
        "810dcf14-1858-4bf2-8134-4c369fa3235b"
    ],
    "O365SBRM Service": [
        "9d06afd9-66c9-49a6-b385-ea7509332b0b"
    ],
    "Microsoft password reset service": [
        "93625bc8-bfe2-437a-97e0-3d0060024faa"
    ],
    "Skype Presence Service": [
        "1e70cd27-4707-4589-8ec5-9bd20c472a46"
    ],
    "Geneva Alert RP": [
        "6bccf540-eb86-4037-af03-7fa058c2db75"
    ],
    "Microsoft Teams UIS": [
        "1996141e-2b07-4491-927a-5a024b335c78"
    ],
    "Microsoft Teams Task Service": [
        "d0597157-f0ae-4e23-b06c-9e65de434c4f"
    ],
    "Dynamics Data Integration": [
        "2e49aa60-1bd3-43b6-8ab6-03ada3d9f08b"
    ],
    "Microsoft Teams Bots": [
        "64f79cb9-9c82-4199-b85b-77e35b7dcbcb"
    ],
    "ComplianceWorkbenchApp": [
        "92876b03-76a3-4da8-ad6a-0511ffdf8647"
    ],
    "AI Builder Authorization Service": [
        "ad40333e-9910-4b61-b281-e3aeeb8c3ef3"
    ],
    "Microsoft Forms": [
        "c9a559d2-7aab-4f13-a6ed-e7e9c52aec87"
    ],
    "Microsoft.SMIT": [
        "8fca0a66-c008-4564-a876-ab3ae0fd5cff"
    ],
    "Federated Profile Service": [
        "7e468355-e4db-46a9-8289-8d414c89c43c"
    ],
    "Data Export Service for Microsoft Dynamics 365": [
        "b861dbcc-a7ef-4219-a005-0e4de4ea7dcf"
    ],
    "Skype Teams Firehose": [
        "cdccd920-384b-4a25-897d-75161a4b74c1"
    ],
    "Media Analysis and Transformation Service": [
        "0cd196ee-71bf-4fd6-a57c-b491ffd4fb1e"
    ],
    "PowerAI": [
        "8b62382d-110e-4db8-83a6-c7e8ee84296a"
    ],
    "Dynamics Lifecycle services": [
        "913c6de4-2a4a-4a61-a9ce-945d2b2ce2e0"
    ],
    "O365Account": [
        "1cda9b54-9852-4a5a-96d4-c2ab174f9edf"
    ],
    "Microsoft Teams RetentionHook Service": [
        "f5aeb603-2a64-4f37-b9a8-b544f3542865"
    ],
    "Skype and Teams Tenant Admin API": [
        "48ac35b8-9aa8-4d74-927d-1f4a14a0b239"
    ],
    "Microsoft Teams Wiki Images Migration": [
        "823dfde0-1b9a-415a-a35a-1ad34e16dd44"
    ],
    "OCaaS Client Interaction Service": [
        "c2ada927-a9e2-4564-aae2-70775a2fa0af"
    ],
    "Microsoft Substrate Management": [
        "98db8bd6-0cc0-4e67-9de5-f187f1cd1b41"
    ],
    "OCPS Admin Service": [
        "f416c5fc-9ac4-4f66-a8e5-cb203139cbe4"
    ],
    "Office 365 Configure": [
        "aa9ecb1e-fd53-4aaa-a8fe-7a54de2c1334"
    ],
    "Office365 Zoom": [
        "0d38933a-0bbd-41ca-9ebd-28c4b5ba7cb7"
    ],
    "Teams ACL management service": [
        "6208afad-753e-4995-bbe1-1dfd204b3030"
    ],
    "PowerAppsService": [
        "331cc017-5973-4173-b270-f0042fddfd75"
    ],
    "StreamToSubstrateRepl": [
        "607e1f95-b519-4bac-8a15-6196f40e8977"
    ],
    "PowerApps-Advisor": [
        "c9299480-c13a-49db-a7ae-cdfe54fe0313"
    ]
}
"""
