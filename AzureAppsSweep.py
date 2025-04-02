import argparse
import json
import threading
import concurrent.futures
from pprint import pprint
from colorama import Fore, Style, init
import requests
import msal
from tqdm import tqdm


# Initialize colorama for colored output
init()

# Rource URIs to authenticate against
RESOURCE_URIS = [
    'https://graph.windows.net/',
    'https://graph.microsoft.com/',
    'https://management.core.windows.net/',
    'https://management.azure.com/',
    'https://outlook.office.com/',
    'https://vault.azure.net/',
    'https://storage.azure.com/'
]

REQUIRE_SECRET_RESOURCE_URIS = [
    'https://graph.windows.net/',
    'https://graph.microsoft.com/',
    'https://management.core.windows.net/',
    'https://management.azure.com/'
]


# List of Application (Client) IDs
"""
List of Application (Client) IDs from:
- https://github.com/secureworks/family-of-client-ids-research/blob/main/known-foci-clients.csv
- https://www.rickvanrousselt.com/blog/azure-default-service-principals-reference-table/
- https://github.com/dirkjanm/ROADtools/blob/master/roadtx/roadtools/roadtx/firstpartyscopes.json
- https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/governance/verify-first-party-apps-sign-in
- https://learn.microsoft.com/en-us/power-platform/admin/apps-to-allow
- https://raw.githubusercontent.com/emilyvanputten/Microsoft-Owned-Enterprise-Applications/refs/heads/main/Microsoft%20Owned%20Enterprise%20Applications%20Overview.md
- https://raw.githubusercontent.com/SlimKQL/Hunting-Queries-Detection-Rules/refs/heads/main/IOC/GraphPreConsent.csv
- https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/governance/verify-first-party-apps-sign-in
- https://malwaremaloney.blogspot.com/2022/12/azure-app-ids.html
- https://www.powershellgallery.com/packages/AADInternals/0.8.2/Content/AccessToken_utils.ps1
- https://raw.githubusercontent.com/dmb2168/o365-appids/refs/heads/master/ids.md
- https://github.com/maciejporebski/azure-ad-first-party-apps-permissions
"""

APPS = {
    "FindTime": [
        "9758a0e2-7861-440f-b467-1823144e5b65"
    ],
    "Office Delve": [
        "94c63fef-13a3-47bc-8074-75af8c65887a"
    ],
    "SpoolsProvisioning": [
        "61109738-7d2b-4a0b-9fe3-660b1ff83505"
    ],
    "Windows Azure Service Management API": [
        "84070985-06ea-473d-82fe-eb82b4011c9d"
    ],
    "Graph Explorer": [
        "d3ce4cf8-6810-442d-b42e-375e14710095"
    ],
    "Intune DeviceActionService": [
        "18a4ad1e-427c-4cad-8416-ef674e801d32"
    ],
    "Cortana Experience with O365": [
        "0a0a29f9-0a25-49c7-94bf-c53c3f8fa69d"
    ],
    "O365 LinkedIn Connection": [
        "e06b767e-6342-4a04-a421-f801693feb8d"
    ],
    "Teams User Engagement Profile Service": [
        "0f54b75d-4d29-4a92-80ae-106a60cd8f5d"
    ],
    "OfficeGraph": [
        "ba23cd2a-306c-48f2-9d62-d3ecd372dfe4"
    ],
    "DevilFish": [
        "eaf8a961-f56e-47eb-9ffd-936e22a554ef"
    ],
    "Microsoft Fluid Framework Preview": [
        "660d4be7-2665-497f-9611-a42c2668dbce"
    ],
    "EnterpriseRoamingandBackup": [
        "60c8bde5-3167-4f92-8fdb-059f6176dc0f"
    ],
    "MicrosoftApprovalManagement": [
        "38049638-cc2c-4cde-abe4-4479d721ed44"
    ],
    "MicrosoftAzurePowerShell": [
        "1950a258-227b-4e31-a9cf-717495945fc2"
    ],
    "MicrosoftAzureCLI": [
        "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
    ],
    "MicrosoftAuthenticationBroker": [
        "29d9ed98-a469-4536-ade2-f981bc1d605e"
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
    "Office365Management": [
        "00b41c95-dab0-4487-9791-b9d2c32c80f2"
    ],
    "MicrosoftTeams": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
    ],
    "Office365SharePointOnline": [
        "00000003-0000-0ff1-ce00-000000000000"
    ],
    "OutlookMobile": [
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "OneDriveSyncEngine": [
        "ab9b8c07-8f02-4f72-87fa-80105867a763"
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
    "WindowsSpotlight": [
        "1b3c667f-cde3-4090-b60b-3d2abd0117f0"
    ],
    "WindowsSearch": [
        "26a7ee05-5602-4d76-a7ba-eae8b7b67941"
    ],
    "Vortex[wsfedenabled]": [
        "5572c4c0-d078-44ce-b81c-6cbf8d3ed39e"
    ],
    "MicrosoftGraphCommandLineTools": [
        "14d82eec-204b-4c2f-b7e8-296a70dab67e"
    ],
    "OutlookUserSettingsConsumer": [
        "7ae974c5-1af7-4923-af3a-fb1fd14dcb7e"
    ],
    "OfficeUWPPWA": [
        "0ec893e0-5785-4de6-99da-4ed124e5296c"
    ],
    "WindowsShell": [
        "145fc680-eb72-4bcf-b4d5-8277021a1ce8"
    ],
    "EditorBrowserExtension": [
        "1a20851a-696e-4c7e-96f4-c282dfe48872"
    ],
    "SSOExtensionIntune": [
        "163b648b-025e-455b-9937-a7f39a65d171"
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
    "PowerApps-apps.powerapps.com": [
        "3e62f81e-590b-425b-9531-cad6683656cf"
    ],
    "EnterpriseDashboardProject": [
        "3a4d129e-7f50-4e0d-a7fd-033add0a29f4"
    ],
    "UniversalPrintEnabledPrinter": [
        "417ae6eb-aac8-42c8-900c-0e50debba688"
    ],
    "MicrosoftAuthenticatorApp": [
        "4813382a-8fa7-425e-ab75-3b753aab3abb"
    ],
    "PowerApps": [
        "4e291c71-d680-4d0e-9640-0a3358e31177"
    ],
    "FXIrisClient": [
        "4b0964e4-58f1-47f4-a552-e2e1fc56dcd7"
    ],
    "SurfaceDashboard": [
        "507a7586-da5c-4e86-80f2-2bc2e55ae394"
    ],
    "GraphFilesManager": [
        "52c2e0b5-c7b6-4d11-a89c-21e42bcec444"
    ],
    "MicrosoftFlowMobilePROD-GCCH-CN": [
        "57fcbcfa-7cee-4eb1-8b25-12d2030b4ee0"
    ],
    "SharePointOnlineClient": [
        "57fb890c-0dab-4253-a5e0-7188c88b2bb4"
    ],
    "MicrosoftOutlook": [
        "5d661950-3475-41cd-a2c3-d671a3162bc1"
    ],
    "MicrosoftWhiteboardClient": [
        "57336123-6e14-4acc-8dcf-287b6088aa28"
    ],
    "WindowsUpdateforBusinessDeploymentService": [
        "61ae9cd9-7bca-458c-affc-861e2f24ba3b"
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
    "MicrosoftPlanner": [
        "66375f6b-983f-4c2c-9701-d680650f588f"
    ],
    "ZTNADataAcquisition-PROD": [
        "7dd7250c-c317-4bc6-8528-8d27b02707ef"
    ],
    "MicrosoftStreamMobileNative": [
        "844cca35-0656-46ce-b636-13f48b0eecbd"
    ],
    "PowerBIDesktop": [
        "7f67af8a-fedc-4b08-8b4e-37c4d127b6cf"
    ],
    "UniversalPrintConnector": [
        "80331ee5-4436-4815-883e-93bc833a9a15"
    ],
    "VisualStudio-Legacy": [
        "872cd9fa-d31f-45e0-9eab-6e460a02d1f1"
    ],
    "OutlookWebAppWidgets": [
        "87223343-80b1-4097-be13-2332ffa1d666"
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
    "UniversalPrintPSModule": [
        "aad98258-6bb0-44ed-a095-21506dfb68fe"
    ],
    "CommonJobProvider": [
        "a99783bc-5466-4cef-82eb-ebf285d77131"
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
    "MicrosoftDefenderPlatform": [
        "cab96880-db5b-4e15-90a7-f3f1d62ffe39"
    ],
    "SharePointOnlineClientExtensibility": [
        "c58637bb-e2e1-4312-8a00-04b5ffcd3403"
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
    "MicrosoftTunnel": [
        "eb539595-3fe1-474e-9c1d-feb3625d1be5"
    ],
    "MicrosoftEdge": [
        "f44b1140-bc5e-48c6-8dc0-5cf5a53c0e34"
    ],
    "IDS-PROD": [
        "f36c30df-d241-4c14-a0ee-752c71e4d3da"
    ],
    "SharePointAndroid": [
        "f05ff7c9-f75a-4acd-a3b5-f4b6a870245d"
    ],
    "MicrosoftRemoteAssist": [
        "fca5a20d-55aa-4395-9c2f-c6147f3c9ffa"
    ],
    "MediaRecordingforDynamics365Sales": [
        "f448d7e5-e313-4f90-a3eb-5dbb3277e4b3"
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
    "Microsoft Dynamics CRM Learning Path": [
        "2db8cb1d-fb6c-450b-ab09-49b6ae35186b"
    ],
    "Salesforce": [
        "481732f5-fe5b-48c0-8445-d238ab230658"
    ],
    "Azure Media Service": [
        "803ee9ca-3f7f-4824-bd6e-0b99d720c35c",
        "9716e5d2-76f5-485f-a19f-ce8ec7458fa8"
    ],
    "MicrosoftTeamsCortanaSkills": [
        "2bb78a2a-f8f1-4bc3-8ecf-c1e15a0726e6"
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
    ],
    "Azure HDInsight Service": [
        "b7b6e0a7-d4e4-4bd5-9bac-74c26c1b0cd9"
    ],
    "P2P Server": [
        "4baf8c35-5b76-40cc-b0a0-4d62288dad7d",
        "c27373d3-335f-4b45-8af9-fe81c240d377"
    ],
    "Databricks Resource Provider": [
        "db7dd3d5-0542-48bc-81aa-701346e5844b"
    ],
    "Microsoft.ServiceBus": [
        "9fe2f6a9-96dc-4494-950c-4f5b634f9a1e"
    ],
    "Domain Controller Services": [
        "b5682da3-67a9-45ef-859f-efa0b9d97eb5"
    ],
    "Microsoft.EventGrid": [
        "b0be8fd1-302e-48bc-810c-e8b532e45138"
    ],
    "Azure OSSRDBMS MySQL Flexible Server BYOK": [
        "76742dcf-16ee-448a-949d-48cd6c2d4167"
    ],
    "Afdx Resource Provider": [
        "3999afde-af12-43c1-89ec-68568716d8e1"
    ],
    "Microsoft.CustomProviders RP": [
        "4cebc331-f9c5-4a20-a364-1e229119f623"
    ],
    "Microsoft Defender For Cloud": [
        "6b5b3617-ba00-46f6-8770-1849282a189a"
    ],
    "Azure API Management": [
        "2ad0c3e6-4811-4a33-a85d-f9ee0c7fd805"
    ],
    "Azure Spring Cloud Service Runtime Auth": [
        "b95a5ac6-0182-4059-8f24-54e875a3ab2a"
    ],
    "Azure API for DICOM": [
        "969b0aee-ace2-4a27-92dd-d69cc4512ede"
    ],
    "Microsoft.Relay": [
        "f583498c-b3ee-4be0-b30c-011b5e4b0370"
    ],
    "AML Registries": [
        "27bb8476-8ca7-4034-a3a7-bcdcc76b140f"
    ],
    "Bot Service Resource Provider": [
        "57c13fd7-5246-44bf-99d9-85928b28721d"
    ],
    "Azure Maps": [
        "1cf4a5f2-bf1e-4af8-83ab-f376a8b23b82"
    ],
    "Azure Blueprints": [
        "871fb170-5c42-4db8-93fb-7476090804f8"
    ],
    "Azure Help Resource Provider": [
        "92d9fdf2-d203-4e4f-9ef9-cedd318e174d"
    ],
    "Microsoft Mixed Reality": [
        "a269ec17-9d67-46b3-9822-180a072be1b5"
    ],
    "Azure Healthcare APIs": [
        "aa936b86-846f-4344-ad37-b3884b511016"
    ],
    "Azure Machine Learning Authorization App 1": [
        "910f6787-801a-4880-b971-54d0029386da"
    ],
    "Azure Container Registry Application": [
        "4f5724ac-4dc2-4a82-bf16-b128fc593aff"
    ],
    "Bot Service Token Store": [
        "d29a9894-0700-4b1b-b8d9-f2517818b253"
    ],
    "Azure CosmosDB for PostgreSQL AAD Authentication": [
        "3798f5f7-b3d7-43c2-a40b-825fe34b86ed"
    ],
    "Azure Spring Cloud Resource Provider": [
        "875fa7ec-316c-43a2-ac06-79ae4847857a"
    ],
    "Azure Machine Learning Services": [
        "acf13426-7a5f-47ed-bfa0-680d65b48fe8"
    ],
    "Azure HDInsight Surrogate Service": [
        "77c02f7b-de44-4cab-9cb0-017f8d81d580"
    ],
    "Azure Container Registry - Dataplane": [
        "46b05578-bb96-4cec-b761-d4802bc6ab5b"
    ],
    "Azure Maps Resource Provider": [
        "237ab3a9-d787-4558-8a26-06c12938adaa"
    ],
    "Data Migration Service": [
        "43b50a11-ef3a-4d37-8ee5-e0c8a512dfe9"
    ],
    "Azure Machine Learning Authorization App 2": [
        "8a46fce9-b8a9-4824-bee6-1d3b24d34197"
    ],
    "MicrosoftAzureRedisCache": [
        "1e066e64-955c-4d5f-b19c-bb06dfccb678"
    ],
    "Azure Data Factory": [
        "a306baf0-5ad8-4f6f-babf-6a286b0142ba"
    ],
    "Azure Media Services": [
        "18fc747c-43ab-4199-aead-4371d7bd013b"
    ],
    "ASA Curation Web Tool": [
        "ddd8a68c-6220-41a2-a25d-77153f8b3449"
    ],
    "Azure Search Management": [
        "7dd7d7a1-0348-46f4-a1c7-f237b0a2db65"
    ],
    "Bot Service CMEK Prod": [
        "4d7aad95-9666-4245-9244-0270f94e6e01"
    ],
    "Azure Container Instance Service": [
        "ca0b1992-96fc-47b1-be37-3bdd772f5935"
    ],
    "Azure Spring Cloud Marketplace Integration": [
        "c271e2f9-1edf-44ed-b05f-8dcfeb62fc55"
    ],
    "Microsoft.NotificationHubs": [
        "2a3c2abe-2536-4b6b-b166-95a1d7cb8488"
    ],
    "Azure Machine Learning OpenAI": [
        "b1570ef9-3b2a-4ff0-97aa-bd14ac78c734"
    ],
    "Azure Cognitive Search": [
        "73c2bd24-782c-4927-9522-83e66037d6e8"
    ],
    "Service Bus MSI App": [
        "c568f157-4ebd-43ae-b3c3-9699fcc646c5"
    ],
    "EventGrid Data API": [
        "f72e5ece-ae04-4e8a-88be-b71c4714388e"
    ],
    "Azure Service Fabric Resource Provider": [
        "a59e9528-9141-46ef-bc9b-dd4258dcb96e"
    ],
    "CosmosDBMongoClusterPrivateEndpoint": [
        "7c0b67ba-6398-475f-bbfe-3fee1c71e94e"
    ],
    "Bot Framework Composer": [
        "dfc4d895-6c50-4251-81b8-211b485265b9"
    ],
    "Windows Cloud Login": [
        "e7aa85bb-1a1a-4ab1-8825-cc24db5e4419"
    ],
    "Azure Database for PostgreSQL Marlin": [
        "3a47abca-ce03-418f-891d-18651fe077c5"
    ],
    "Azure Machine Learning Services Asset Notification": [
        "3dbbb70f-6f78-4ddf-939c-2db37105a5d5"
    ],
    "PowerPlatform-commondataserviceforapps-Connector": [
        "5e72ef24-048b-4aae-8fd6-8653ce2d6760"
    ],
    "Prod M365FLWPClient Prod": [
        "226e4631-c980-4b11-9c96-5e26bb14dafc"
    ],
    "Prod M365FLWPClient FirstRelease": [
        "e582717c-581c-4a51-a8d7-5cd28f59497a"
    ],
    "Microsoft Dynamics CRM for Microsoft Office Outlook": [
        "2f29638c-34d4-4cf2-a16a-7caf612cee15"
    ],
    "Visual Studio": [
        "04f0c124-f2bc-4f59-8241-bf6df9866bbd"
    ],
    "make.test.powerapps.com": [
        "719640cd-0337-4b0c-8e6a-431271371fab"
    ],
    "PhysOps.Clients.Worker": [
        "04d97d71-f71f-450b-8b44-f638d5d1b5d6"
    ],
    "Minit Desktop for Windows": [
        "5c17a0cf-5493-4b86-b23d-dabc1cc46f5a"
    ],
    "Microsoft.Data.SqlClient": [
        "2fd908ad-0664-4344-b9be-cd3e8b574c38"
    ],
    "LobeClientDev": [
        "bd414a4d-005a-4a51-a63e-12097e3dcd19"
    ],
    "make.powerpages.microsoft.com": [
        "945d3a88-db20-40bd-a9e3-8f2383a17c88"
    ],
    "Power Platform CLI - pac": [
        "9cee029c-6210-4654-90bb-17e6e9d36617"
    ],
    "Dynamics 365 Customer Insights - Consent - DEV": [
        "8b66798c-a359-423d-8d71-567ee6da1016"
    ],
    "Supply Chain Windblade Development": [
        "50d9b7e0-07b6-4615-a8ae-f7f017db392a"
    ],
    "TrustedPublishersProxyService-DoD": [
        "22618bd1-b6aa-45f0-8ebd-718d158d888d"
    ],
    "Lobe": [
        "37ff607d-6be1-4c1b-a5f8-e5ad92b55975"
    ],
    "TrustedPublishersProxyService-GccModerate": [
        "e8c38929-689f-4155-96f7-ab45b0f67cec"
    ],
    "SharePointMigrationTool": [
        "fdd7719f-d61e-4592-b501-793734eb8a0e"
    ],
    "Dynamics 365 Customer Insights - Consent": [
        "9e3b502c-b4a1-441d-98fd-28e482bf7e88"
    ],
    "Microsoft Dynamics 365 Supply Chain Visibility": [
        "d6037e40-282c-493d-8f63-f255e36c6ef4"
    ],
    "CRM Power BI Integration GCC High": [
        "03509b1f-54e9-4557-a555-19a090903b84"
    ],
    "Search Federation Connector - Dataverse": [
        "9c60a40b-b5c5-4d01-8588-776209c80db3"
    ],
    "Media Recording for Dynamics 365 Sales - TIP": [
        "883d98cb-7d92-43b7-a194-07e51a2fa5bb"
    ],
    "eSeal": [
        "19679030-48d8-445f-b27c-311bb3be8a2c"
    ],
    "PADWAMigrator": [
        "133c4dc0-9d5f-4826-9f7b-6bb3d3867e6a"
    ],
    "PADWAMigratorGCCHigh": [
        "cb47b44e-c0a3-47a5-85ce-3dc039c85e80"
    ],
    "PADWAMigratorGCC": [
        "19a92965-3c11-4ed7-a1bd-9b66785dd4c6"
    ],
    "Power Automate Desktop DoD": [
        "ae7deb89-ca76-4073-bf3e-b72165ac58e9"
    ],
    "Power Automate Desktop GCC High": [
        "f1a1e36a-d61f-4283-9f48-0867636e332c"
    ],
    "ConnectedFieldServiceDeployment": [
        "3852314e-aab9-42c3-a859-5b5b88a90000"
    ],
    "Power Automate Desktop GCC": [
        "041e4c2d-ba3e-46a1-9347-5bc4054c8af4"
    ],
    "ProcessSimpleDoD": [
        "a6d2002e-7db6-4da0-94e8-73765fdbc7fb"
    ],
    "Power Automate Desktop": [
        "ee90a17f-1cb7-4909-be27-dfc2dcc4dc15"
    ],
    "Power BI Report Builder": [
        "f0b72488-7082-488a-a7e8-eada97bd842d"
    ],
    "Dynamics 365 Connected Store": [
        "291bcb22-15e5-4341-8f91-feb152d655ee"
    ],
    "ApiHub-Connectors-DoD": [
        "363a906a-1ceb-41ea-9f20-884c694f2fc2"
    ],
    "Omnichannel for CS Admin App Prod": [
        "fcf50ee5-8107-45e4-9a37-838727a360f5"
    ],
    "OmnichannelEngagementHubAdminApp": [
        "2c37df23-0c28-4fbf-9b2a-d5fd6277bf92"
    ],
    "ApiHub-Connectors-GCCHigh": [
        "36ee54ac-414c-41ef-afde-2ddfd25d5408"
    ],
    "CRM Power BI Integration GCC": [
        "bb0fc165-b959-4e50-a8fc-309c1193e396"
    ],
    "PrcessSimpleGCCHigh": [
        "9856e8dd-37b6-4749-a54b-8f6503ea93b7"
    ],
    "high.create.powerapps.us": [
        "58acb57d-f51b-4993-8f4a-4e41ad77e481"
    ],
    "mil.create.powerapps.us": [
        "d7e0a6a1-dde5-4f6e-81ce-781fa7483834"
    ],
    "PowerApps Fairfax": [
        "a4b559be-784e-49ec-9b63-7208442255e1"
    ],
    "CrmSalesInsightsRA": [
        "6e7d203a-179d-4ae0-87da-a77dd8aa3135"
    ],
    "Field Service Mobile": [
        "0ef09fa7-413d-4a9f-a7a5-32f8f62b7598",
        "110797d6-4a5e-4e58-a06d-f1bf3f3a8069"
    ],
    "MR.Mty.App": [
        "32166110-0424-4622-8b0d-4e50f4da7a74"
    ],
    "DYN365AISERVICEINSIHTSPPE": [
        "11f6c209-c042-4da5-acb9-8d3546fe506f"
    ],
    "APIHub-Connectors-GCC_notUsed": [
        "9a375489-421a-4af5-9f4a-3dd5a8f7b0d8"
    ],
    "PowerAppsGov": [
        "c6d1e3ad-0185-40e0-a11b-0542b185d12c"
    ],
    "MicrosoftDynamics365MRGuidesCoreClient": [
        "655db33f-4580-4e63-bad1-4618764badb9"
    ],
    "ccibots": [
        "a59cef1e-2e32-4703-8dab-810d9807efeb"
    ],
    "CRM Groups Integration": [
        "b15cc146-2b25-46c7-90c1-daa6c3e8386b"
    ],
    "Lobe Client": [
        "0b820e0a-8d08-45d1-8740-bde894f7e1c2"
    ],
    "TrustedPublishersProxyServicePPE": [
        "3d3f56ed-9c38-4480-b172-0fa5d8838516"
    ],
    "Dynamics 365 Field Service": [
        "8d25f88c-09fe-41eb-9ee1-0545adf985df"
    ],
    "Microsoft Dynamics CRM for tablets and phones": [
        "ce9f9f18-dd0c-473e-b9b2-47812435e20d"
    ],
    "Dynamics 365 Development Tools": [
        "2ad88395-b77d-4561-9441-d0e40824f9bc"
    ],
    "Dynamics 365 Example Client Application": [
        "51f81489-12ee-4a9e-aaae-a2591f45987d"
    ],
    "SQL DotNet Client": [
        "4d079b4c-cab7-4b7c-a115-8fd51b6f8239"
    ],
    "Dynamics CRM Unified Service Desk": [
        "4906f920-9f94-4f14-98aa-8456dd5f78a8"
    ],
    "ODBC Client Driver": [
        "2c1229aa-16c5-4ff5-b46b-4f7fe2a2a9c8"
    ],
    "Azure SQL Database and Data Warehouse": [
        "a94f9c62-97fe-4d19-b06d-472bed8d2bcf"
    ],
    "Dynamics Retail Modern POS": [
        "d6b5a0bd-bf3f-4a8c-b370-619fb3d0e1cc"
    ],
    "JDBC Client Driver": [
        "7f98cb04-cd1e-40df-9140-3bf7e2cea4db"
    ],
    "Microsoft Dynamics 365 Project Service Automation Add-in for Microsoft Project": [
        "2f3b013e-5dc4-4b2a-831f-47ba08353237"
    ],
    "Microsoft.Azure.Services.AppAuthentication": [
        "d7813711-9094-4ad3-a062-cac3ec74ebe8"
    ],
    "Microsoft Mashup Engine": [
        "f40b99cd-675e-4ce8-ae86-47b77d2a9c4d"
    ],
    "Power BI Gateway": [
        "ea0616ba-638b-4df5-95b9-636659ae5121"
    ],
    "Project Finder Mobile": [
        "dd63a01a-ae84-4d07-bf60-69dadeaa8c89"
    ],
    "Aadrm Admin Powershell": [
        "90f610bf-206d-4950-b61d-37fa6fd1b224"
    ],
    "Microsoft Dynamics Document Routing Agent": [
        "cf8f0657-7610-4b05-8723-a4322ae045c6"
    ],
    "Microsoft SharePoint Online Management Shell": [
        "9bc3ab49-b65d-410a-85ad-de819febfddc"
    ],
    "Azure Data Studio": [
        "a69788c6-1d43-44ed-9ca3-b83e194da255"
    ],
    "Azure Analysis Services Client": [
        "cf710c6e-dfcc-4fa8-a093-d47294e44c66"
    ],
    "DataSyncService": [
        "ab9468a9-c559-47ec-86f6-2f1b48612c09"
    ],
    "SIAutoCapture": [
        "b9f7f9ce-78c7-4651-8663-c2ba51a2556a"
    ],
    "Dynamics 365 Sales Service": [
        "44f229e1-5c76-4d68-8b7c-83cbfd54ab7a"
    ],
    "Dynamics 365 CCA Prod - CDS to Azure data lake": [
        "299fa2bd-f53a-45b1-b501-1056398454bc"
    ],
    "Dynamics 365 Customer Insights Prod - CDS to Azure data lake": [
        "6ec6a75c-d04e-4613-92da-069f88c74a13"
    ],
    "DynamicsCRMCortanaCacheService@microsoft.com": [
        "d4a55fa7-2c20-434d-8942-689200452979"
    ],
    "Production-DPS-1P-SQLIaaS": [
        "56a02f66-b2ce-4568-954b-907d5476c479"
    ],
    "EAPortals-AAD-PROD-PME": [
        "d48cb907-3a0f-481e-a0d1-41097337a938"
    ],
    "Verifiable Credentials Issuer Service": [
        "603b8c59-ba28-40ff-83d1-408eee9a93e5"
    ],
    "RPA - Machine Management Relay Service - Application": [
        "db040338-7cb4-44df-a22b-785bde7ce0e2"
    ],
    "AzNet Security Guard": [
        "38808189-fa7a-4d8a-807f-eba01edacca6"
    ],
    "Microsoft Assessment React": [
        "c4b110d7-6f1d-473d-aa9e-6e74b8b8bd4b"
    ],
    "Zero Trust Assessment TBD": [
        "62f85080-9912-4a16-b0be-aff63ee2eeea"
    ],
    "Reset Viral Users Redemption Status": [
        "cc7b0696-1956-408b-876a-ad6bf2b9890b"
    ],
    "Azure AD Assessment": [
        "68bc31c0-f891-4f4c-9309-c6104f7be41b"
    ],
    "Zero Trust Assessment - Dev": [
        "be58d912-b9d5-41a0-8b56-779409e017b8"
    ],
    "Microsoft Photos": [
        "0ec2d138-5a70-4a33-b2c7-7d296c996ace"
    ],
    "Zero Trust Assessment": [
        "df2798fc-2aed-4c3a-98ae-1776949480c4"
    ],
    "Exchange Online": [
        "fe93bfe1-7947-460a-a5e0-7a5906b51360",
        "d396de1f-10d4-4023-aae2-5bb3d724ba9a",
        "a3883eba-fbe9-48bd-9ed3-dca3e0e84250",
        "82d8ab62-be52-a567-14ea-1616c4ee06c4",
        "34421fbe-f100-4e5b-9c46-2fea25aa7b88",
        "1150aefc-07de-4228-b2b2-042a536703c0"
    ],
    "Windows Sign In": [
        "38aa3b87-a06d-4817-b275-7a316988d93b"
    ],
    "Report Message": [
        "6046742c-3aee-485e-a4ac-92ab7199db2e"
    ],
    "Message Header Analyzer": [
        "62916641-fc48-44ae-a2a3-163811f1c945"
    ],
    "Azure Gallery RP": [
        "b28ec8e1-950e-4bd0-b3d0-c1e93074b88b"
    ],
    "Azure Marketplace Container Management API": [
        "737d58c1-397a-46e7-9d12-7d8c830883c2"
    ],
    "Azure Classic Portal": [
        "00000013-0000-0000-c000-000000000000"
    ],
    "MS-CE-CXG-MAC-AadShadowRoleWriter": [
        "2f5afa01-cdcb-4707-a62a-0803cc994c60"
    ],
    "ViewPoint": [
        "8338dec2-e1b3-48f7-8438-20c30a534458"
    ],
    "Microsoft_Azure_CloudServices": [
        "6108d6de-1838-4cbc-9679-bdd847e0c357"
    ],
    "Microsoft_Azure_Linux": [
        "dcceb79b-67c2-4b15-a03e-2299d8b413bb"
    ],
    "Liftr-SW-FPA-Portal-AME": [
        "f848a18e-965c-4a93-aa4d-461455d5c90c"
    ],
    "CCE Apps - Azure Portal Extension": [
        "9345c922-3ba0-411e-a35a-baf504780b7a"
    ],
    "ContainerInsightsExt 1st Party AAD App": [
        "5217e4ff-9fc6-4207-ac4e-d1cb98e21d6e"
    ],
    "Liftr Nginx Prod Portal Extension": [
        "b9942e41-18bb-4e2e-8b19-3e68d9a1e0f6"
    ],
    "AppPlatformExtension": [
        "fdf7ff35-02a6-4bcc-b7e5-ec58492e549f"
    ],
    "IoT Firmware Defense Portal Extension": [
        "01fb7e5f-b97c-49ef-a8d8-3a42749598e0"
    ],
    "Microsoft.SecurityDevOps": [
        "e4641a82-72f6-4171-a0ca-6aaf93f1bf6f"
    ],
    "Microsoft_Azure_Toolbox": [
        "4e652bf8-6698-46b0-8cbe-cdfea0359587"
    ],
    "Microsoft_Azure_Lockbox": [
        "e399b3f2-dc91-483a-ad8d-68d1b7de243b"
    ],
    "ADP Portal Extension": [
        "cf3da98f-3b14-444a-a1d8-5fb31fdec4eb"
    ],
    "AzureTfsExtension": [
        "d07786ab-a18e-4283-8271-08b599ce4bd6"
    ],
    "HDIUX_APP": [
        "6af07558-09e0-40fd-8af6-7759d010cf82"
    ],
    "Microsoft_Azure_ResourceMove": [
        "8146ae4f-bb41-4b3e-907b-fb6748544972"
    ],
    "HPC Cache Resource Provider": [
        "26c57cfa-0e4f-4f4c-8183-65dd3562dcbf"
    ],
    "Common Job Provider": [
        "2789980b-ce2c-4d1d-9fa3-094504a5645e"
    ],
    "Azure Monitor for VMs": [
        "2904b861-3fb2-4c0b-9a16-bb32a2a384e9"
    ],
    "Windows Virtual Desktop": [
        "291173f2-badd-4ff3-9bc0-d648484e72a3"
    ],
    "Azure Time Series Insights": [
        "332dd5ef-2bce-468b-aab1-940bc4ebd97f"
    ],
    "Windows 365": [
        "373a9149-afef-4cef-93b9-648fabe529bd"
    ],
    "Azure Machine Learning Singularity": [
        "3b5879d4-86ea-470d-a17e-f7366dae504a"
    ],
    "Azure Spring Cloud Domain-Management Dogfood": [
        "57d2b469-6257-4341-8a00-c18414024ae2"
    ],
    "JanetDesktop": [
        "5a0ad617-6fba-4faf-9f58-d4e2784d2adb"
    ],
    "MIP Exchange Solutions - SPO": [
        "670b1e76-42e9-42cd-b6bf-343c191754aa"
    ],
    "Virtual Visits App": [
        "6e90d55a-fe3d-492f-872f-f8fd3a48e6ef"
    ],
    "Azure Container Scale Sets": [
        "7dd0ca0e-db35-4484-9bcc-1fca0167175c"
    ],
    "PymAuto": [
        "7e820df5-008e-4193-8a14-2d2e601fd817"
    ],
    "HankDesktop": [
        "8684e85f-feb7-465f-ad32-b8408797e22b"
    ],
    "AnalyzeGraphAPILogs": [
        "86034260-9c03-4bd1-a9e0-5fe157ae0f30"
    ],
    "Meru19 First Party App": [
        "8a752261-dd98-4de2-bd78-2e8536301df0"
    ],
    "Microsoft Azure Authorization Resource Provider": [
        "905ca05e-e2be-4925-ba98-056cd7e1111e"
    ],
    "Atlas": [
        "9d3a77cc-736e-4866-a45f-37aed542557c"
    ],
    "Application Registration Portal": [
        "a1768800-e38a-4b25-a1a9-cafc73ef92b2"
    ],
    "Microsoft Support Diagnostics": [
        "b17022b1-8f0e-4091-980e-a79b5d8a3699"
    ],
    "ScottVM": [
        "aba4d445-85a2-4b5c-9246-92cc5c6b7ae0"
    ],
    "AML Inferencing Frontdoor - Staging": [
        "b414889e-35c4-4183-9e3d-4b037923fe1f"
    ],
    "MIP Exchange Solutions - Teams": [
        "bcc8664b-00fb-4087-9943-14a46d4e537a"
    ],
    "Customer Service Trial PVA - readonly": [
        "bff4471c-acee-4055-a3eb-2fa154c40b2b"
    ],
    "Meeting Migration Service": [
        "e07fbfb6-39b9-43ce-a86a-968354210e8d"
    ],
    "Azure Hilo Client": [
        "e0150823-7e17-4203-8ea3-0519d360fac1"
    ],
    "MIP Exchange Solutions - ODB": [
        "e0ed03d4-10dd-4bff-9572-f59f3ededa8b"
    ],
    "Customer Service Trial PVA": [
        "e2bcdfa9-dd6d-4352-ad8f-c13d2026e4a6"
    ],
    "Windows Virtual Desktop Client": [
        "f1609691-5d6a-40b9-b678-489435fbd34c"
    ],
    "Azure AD Domain Services Sync": [
        "ec7ff229-8301-48d7-8be1-575d70631ec9"
    ],
    "Messaging Augmentation Application": [
        "f47e1068-2614-4579-b5bf-7028cfe2abb1"
    ],
    "Microsoft Exchange Message Tracking Service": [
        "6326e366-9d6d-4c70-b22a-34c7ea72d73d"
    ],
    "Contact Center": [
        "05c3e7fe-59c1-4d68-b334-336aa7ed4b64"
    ],
    "Impression Signatures": [
        "05de51e6-8f7d-43f3-a0d5-b576c18abd96",
        "be181d9c-9060-40a0-a692-b29f2e314d16"
    ],
    "AAD Pin redemption client": [
        "06c6433f-4fb8-4670-b2cd-408938296b8e"
    ],
    "Eva": [
        "07c3de2f-6e55-4fae-8c97-90964ff2b934"
    ],
    "Powell Teams": [
        "086ae3fb-fdf0-4c49-8c38-57d082b00dc4"
    ],
    "Azure Android App": [
        "0c1307d4-29d6-4389-a11c-5cbe7f65d7fa"
    ],
    "absentify": [
        "0f5eabc0-89bf-4cc6-80d1-10094b5919d2"
    ],
    "Decisions": [
        "1064f7e4-a9e2-467d-8d42-f45cc59f145d"
    ],
    "ThinkBase": [
        "10efd24e-58e9-45fe-8aca-29d4012b6921"
    ],
    "Axis": [
        "12c3ee39-9735-4cca-8006-94650d19f770"
    ],
    "BHN Rewards": [
        "14279eef-ef42-44d9-8168-29766786c1f9"
    ],
    "Heedify Contact Centre": [
        "15367a30-a5de-467a-8c1d-00f3c8e56fa9"
    ],
    "Sync client": [
        "1651564e-7ce4-4d99-88be-0a65050d8dc3"
    ],
    "OfficeTogether": [
        "86f76b8b-3355-4e40-a55a-8463a407a327"
    ],
    "EasyLife 365": [
        "192ba193-b68c-464c-a920-7eaa93b59a12",
        "2e8b6192-7ea3-44a7-921e-86e0afd8cd0a",
        "716a0b19-6f38-4909-a80a-ffaac7957316"
    ],
    "DeskManager": [
        "e5d4c7df-50aa-4c15-aa06-c108d0225832"
    ],
    "Theta Lake Recording & Compliance for Teams Video": [
        "1cc8eecf-56f3-4137-a0fe-4b0466ca0677"
    ],
    "Exclaimer Cloud for Outlook": [
        "214c49cc-b1f4-4105-bdd9-468bedc2056a"
    ],
    "Luware Nimbus for Microsoft Teams": [
        "23694b6c-5a4a-45ce-9c6a-37c5f1880d4e"
    ],
    "PowerBI content pack": [
        "2a0c3efa-ba54-4e55-bdc0-770f9e39e9ee"
    ],
    "Contextere AVA": [
        "2b6eff1c-9e11-4010-82da-c4f310c251c0"
    ],
    "Manager360": [
        "2f05d0f8-3f87-4a59-952d-33c69c24a6d9"
    ],
    "IXCloud - Teams Compliance Recording & Intelligence": [
        "77578a4c-117a-4cd4-b36d-3ea09ca2eded"
    ],
    "ChallengeRunner": [
        "311df43b-4397-4635-9029-de779ed38476"
    ],
    "ACV": [
        "317696dd-0e3b-4117-9694-ca65942c02f3"
    ],
    "Showpad": [
        "34430110-c9d4-479a-88eb-e335c7889356"
    ],
    "Edpuzzle": [
        "bffbcd4d-00b8-4375-9951-1928250b636e"
    ],
    "Attender": [
        "3741153e-2490-463c-aff7-5283fb1bd1b4"
    ],
    "DigitalOps Toolbox": [
        "3662a4ca-d108-4f34-9e08-914f33363235"
    ],
    "Blippbuilder": [
        "3a292e75-bd45-4b7a-ab85-2032a9c9c4c1"
    ],
    "Q": [
        "418a1ee4-ca76-4b38-b4b3-8cca25417a6c"
    ],
    "MyHub": [
        "478c769e-bab3-4049-9cfc-302d08a232bf"
    ],
    "PlanIt": [
        "49cd11e3-cd7c-422a-9e2c-98a0a40fa418"
    ],
    "GuineaPig": [
        "d6a2090f-1447-456b-bd5f-121e4efd8c89"
    ],
    "iTalent": [
        "4fc7d06a-a9f5-4ade-beb1-2e9b9ef4d859"
    ],
    "MindManager": [
        "51e2b67d-9854-446a-8da1-cdd89ef0b987"
    ],
    "StoragePool Resource Provider": [
        "5741a1ff-751d-4ad7-bcd1-dfe3c998fd11"
    ],
    "Office2SharePoint": [
        "5971c986-9d39-409c-a6f8-1385b1f690ef"
    ],
    "TINYpulse": [
        "58cac74c-be05-4edf-b6de-294e856ecd7b"
    ],
    "Keepass Pro": [
        "597cc93d-8951-4f62-b549-eca97ba5c042"
    ],
    "Fingertip Decision Matrix": [
        "5a6a4d82-42ce-42c4-88f0-df529fe54dcc"
    ],
    "Now Virtual Agent": [
        "5a87eaa0-a00c-4382-9bdd-cdada0b6820f"
    ],
    "Priority Matrix": [
        "5be2b320-a5b7-4221-893c-dee506e4e365",
        "affadfb6-f17b-428f-97f9-9aae3b6175bc",
        "d76f016f-52c7-41b5-835b-900361d7040c"
    ],
    "WindowsDefenderATPSiemConnector": [
        "5cec7726-ab26-409b-9928-8483fe79222b"
    ],
    "Luware Compliance Recording for Microsoft Teams": [
        "5e5d72e0-2df7-4ca7-be58-81dc28d3bdad"
    ],
    "CrossCheck": [
        "5edad654-f2d5-41d8-bfc0-92c2735252e1"
    ],
    "My Stickers": [
        "695d3f13-6131-4224-aacd-26c8aff039d2"
    ],
    "Intune MAM client": [
        "6c7e8096-f593-4d72-807f-a5f86dcc9c77"
    ],
    "AAD Connect v2": [
        "6eb59a73-39b2-4c23-a70f-e2e3ce8965b1"
    ],
    "Expensya": [
        "6ce7c411-d7c9-4c4f-882e-164447c9b44a"
    ],
    "Peer to Peer": [
        "6fdf9d65-bc4b-44c5-b301-dbb339529ae5"
    ],
    "Koare Rotation chairs": [
        "719780b6-b763-478c-aa5c-9441738529b2"
    ],
    "vimheslo": [
        "73ee6b52-6b68-41c1-a7c5-91919e05b845"
    ],
    "Microsoft Azure Graph Client Library 2.1.9 Internal": [
        "7492bca1-9461-4d94-8eb8-c17896c61205"
    ],
    "Interprefy-Translation": [
        "7bc3fffa-48d6-442b-a300-5b3209ef8606"
    ],
    "Cytric Easy": [
        "7d7761c0-8b7a-49bb-8975-a6aa1be7c38b"
    ],
    "Streamline": [
        "7f6565a7-45e4-4bba-94d4-bac64886ed83"
    ],
    "DisasterTech DICE": [
        "7df3e67b-ed62-48e9-a950-c95bd7ebce80"
    ],
    "Moneypenny": [
        "8277a51c-3ad6-446c-9b7e-e3f6e27257c1"
    ],
    "e2e-assure": [
        "8bdf3437-e038-4a93-abdc-00461630f6c3"
    ],
    "Priority Matrix Government": [
        "8cbdb27d-6b59-402d-a9c0-a588cfb4030c"
    ],
    "EcoMatcher": [
        "915f5e4f-89d9-4469-8450-fac533326fcd"
    ],
    "Aimful": [
        "93544582-de9c-42a0-baa5-df3d25e9bd48"
    ],
    "Tigim Analytics": [
        "98172521-768f-4271-a872-00bd46bd9460"
    ],
    "Wellness Coach": [
        "9913e2ed-5c17-4d66-b9e7-439290238f29"
    ],
    "Meety": [
        "9a68d494-f5ae-4e0c-ad18-478bf6fcd101"
    ],
    "EXO Remote PowerShell": [
        "a0c73c16-a7e3-4564-9a95-2bdf47383716"
    ],
    "LMS365": [
        "a1a0b277-0efb-4f00-9661-6d1a3df3cddc"
    ],
    "MSPbots": [
        "a2af9d71-95f1-4236-be2c-c105ab9b7ee9"
    ],
    "Semplisio e-commerce Manager": [
        "a44c880f-f691-4553-9855-4b256721933c"
    ],
    "Link Spotter": [
        "a4c28379-0840-42c5-9407-f088a7f54048"
    ],
    "Lightning Tools Lightning Conductor": [
        "a96cbd10-e960-47b8-855b-3af4b5dbd6f4"
    ],
    "Discoveries engauge": [
        "af9d939c-9f65-4d1b-ac24-0f9f592418ea"
    ],
    "Eusoft Rdp Manager": [
        "b152baa1-c56c-4fa5-9ae4-7f83e150d141"
    ],
    "Frankie Health": [
        "b2425429-1494-4d6f-a851-39ef771c6fbb"
    ],
    "DataFetch": [
        "b3af1387-3ee6-4074-a594-7a768cd00d44"
    ],
    "AADJ CSP": [
        "b90d5b8f-5503-4153-b545-b31cecfaece2"
    ],
    "Teams Manager": [
        "b9a1aaab-e8aa-4b92-b4ce-f13cae74caa7"
    ],
    "HeyTaco": [
        "be8d11cf-265a-4974-9912-4ff28c29fc21"
    ],
    "Team Survey": [
        "c02f0aa2-8697-4a89-bf06-55235ede9eda"
    ],
    "Jetdocs": [
        "bf75bbb7-8d86-434e-86f2-4ec7bd24d149"
    ],
    "Teamflect": [
        "c5da92a9-873e-4ea1-86c7-03ec9c1384f0"
    ],
    "Waldo": [
        "c71a6f53-cf0c-426d-a826-cedae8b073f7"
    ],
    "BEDORE": [
        "ca2d1b0a-dd6a-4c50-9617-e3fb3245fbee"
    ],
    "Priority Matrix - Turn emails into tasks": [
        "cf9bdbc1-18c7-4700-b6b3-093f241e2d8a"
    ],
    "1st Reporting": [
        "d1091476-648b-4c6c-b629-52207dfd4a72"
    ],
    "Anywhere365 Contact Center for Teams": [
        "d1762bac-3696-429d-ab0b-2a61463d6b7a"
    ],
    "Anakage": [
        "d2133ef6-1b22-4182-b932-9109dd7a80a6"
    ],
    "Thrive Global": [
        "d4774f88-9a5e-470c-9a8f-c77b63b6e322"
    ],
    "Happyforce": [
        "d5ed7567-83fb-4978-8aca-5018e63ece32"
    ],
    "Skype": [
        "d924a533-3729-4708-b3e8-1d2445af35e3"
    ],
    "Interactio": [
        "db521db7-52a0-487c-a37b-8712bcf58561"
    ],
    "Windows Configuration Designer (WCD)": [
        "de0853a1-ab20-47bd-990b-71ad5077ac7b"
    ],
    "Zoom for Outlook": [
        "e48b7efb-a618-4297-ad12-f45c73a0ff4c"
    ],
    "illustrationprocess": [
        "e548672a-be02-455c-af4b-a93e1bed3353"
    ],
    "MIPA - My Intelligent Personal Assistant": [
        "e854ea05-68ab-4204-babe-db4a784fb4d8"
    ],
    "Tap My Back": [
        "e91949df-2533-41ba-8981-f39160efa808"
    ],
    "Adobe Acrobat": [
        "4e9b8b9a-1001-4017-8dd1-6e8f25e19d13"
    ],
    "Apple Internet Accounts": [
        "f8d98a96-0999-43f5-8af3-69971c7bb423"
    ],
    "Wats": [
        "f9eaef18-fbd1-4045-b417-c26598755298"
    ],
    "CI-Out-of-Office Lite": [
        "fc1e4e41-1e20-49ba-88aa-5f26fa8bc4da"
    ],
    "SPO": [
        "else9bc3ab49-b65d-410a-85ad-de819febfddc"
    ],
    "Azure admin interface": [
        "lsec44b4083-3bb0-49c1-b47d-974e53cbdf3c"
    ],
    "MS Commerce": [
        "3d5cffa9-04da-4657-8cab-c7f074657cad"
    ],
    "Azure AD Join": [
        "else29d9ed98-a469-4536-ade2-f981bc1d605e"
    ],
    "Napa Office 365 Development Tools": [
        "48717084-a59c-4306-9dc4-3f618dbecdf9"
    ],
    "RbacBackfill": [
        "914ed757-9257-4200-b68e-a2bed2f12c5a"
    ],
    "My sign-ins": [
        "else19db86c3-b2b9-44cc-b339-36da233a3be2"
    ],
    "Windows Azure RemoteApp Service": [
        "31d3f3f5-7267-45a8-9549-affb00110054"
    ],
    "Power BI": [
        "89f80565-bfac-4c01-9535-9f0eba332ffe"
    ],
    "BasicDataOperationsREST": [
        "38285dce-a13d-4107-9b04-3016b941bb3a"
    ],
    "BasicSelfHostedAppREST": [
        "92bb96c8-321c-47f9-bcc5-8849490c2b07"
    ],
    "Office365RESTAPIExplorer.Office365App": [
        "8ad28d50-ee26-42fc-8a29-e41ea38461f2"
    ],
    "WindowsFormsApplication2.Office365App": [
        "488a57a0-00e2-4817-8c8d-cf8a15a994d2"
    ],
    "Azure AD Account": [
        "else0000000c-0000-0000-c000-000000000000"
    ],
    "My SharePoint Sites": [
        "a393296b-5695-4463-97cb-9fa8638a494a"
    ],
    "OAuth Sandbox": [
        "32613fc5-e7ac-4894-ac94-fbc39c9f3e4a"
    ],
    "Edmodo": [
        "ef4a2a24-4b4e-4abf-93ba-cc11c5bd442c"
    ],
    "OfficeDelve": [
        "b4114287-89e4-4209-bd99-b7d4919bcf64"
    ],
    "LastPass": [
        "159b90bb-bb28-4568-ad7c-adad6b814a2f"
    ],
    "Protected Message Viewer": [
        "3a9ddf38-83f3-4ea1-a33a-ecf934644e2d"
    ],
    "Responsive Banner Slider": [
        "5635d99c-c364-4411-90eb-764a511b5fdf"
    ],
    "drawio": [
        "45c10911-200f-4e27-a666-9e9fca147395"
    ],
    "Skype Web": [
        "e48d4214-364e-4731-b2b6-47dabf529218"
    ],
    "Workflow": [
        "562e1694-7fae-4b07-b69f-7560ae99bb05",
        "bbb99509-a5fe-40f4-9c26-b892bc6ac9c0",
        "60850bcf-0ed0-4f34-bb47-8697b26ec0fd",
        "cf7cfb15-601e-4df5-93e4-541fe820c33c",
        "4b5e1344-2351-f7ac-f195-6ecb1d6b5483",
        "793fee30-4e36-4f8a-8eb0-9728a289d5f8",
        "4204a689-25aa-4d5f-8458-d1dfe7d3b4a8",
        "434c7e91-d2b4-4623-a9a3-f60b5412317d"
    ],
    "Sharegate": [
        "241f691a-2424-4ef0-9161-57b7249e2bfc"
    ],
    "Azure Notebooks": [
        "0d973830-135d-4ffa-92cd-4c57650dc220"
    ],
    "Cisco Webex": [
        "3befd9dc-dfb4-4df9-a029-739b8b9b95ff"
    ],
    "Fresh Service ITSM": [
        "6bcc5848-c73a-4953-9066-9ceab1f5256"
    ],
    "Unknown": [
        "aed8c6c1-22ce-466f-8d04-81daba240b0f"
    ],
    "Microsoft Events": [
        "e462442e-6682-465b-a31f-652a88bfbe51"
    ],
    "MS teams PowerShell": [
        "12128f48-ec9e-42f0-b203-ea49fb6af367"
    ]
}

REQUIRE_SECRET_APPS = {
    "App Service": [
        "7ab7862c-4c57-491e-8a45-d52a7e023983"
    ],
    "ADIbizaUX": [
        "74658136-14ec-4630-ad9b-26e160ff0fc6"
    ],
    "ACOM Azure Website": [
        "23523755-3a2b-41ca-9315-f81f3f566a95"
    ],
    "ASM Campaign Servicing": [
        "0cb7b9ec-5336-483b-bc31-b15b5788de71"
    ],
    "AEM-DualAuth": [
        "69893ee3-dd10-4b1c-832d-4870354be3d8"
    ],
    "Azure Advanced Threat Protection": [
        "7b7531ad-5926-4f2d-8a1d-38495ad33e17"
    ],
    "Azure Lab Services Portal": [
        "835b2a73-6e10-4aa5-a979-21dfda45231c"
    ],
    "Azure SQL Database": [
        "022907d3-0f1b-48f7-badc-1ba6abab6d66"
    ],
    "Azure Portal": [
        "c44b4083-3bb0-49c1-b47d-974e53cbdf3c"
    ],
    "Azure Data Lake": [
        "e9f49c6b-5ce5-44c8-925d-015017e9f7ad"
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
    "Focused Inbox": [
        "b669c6ea-1adf-453f-b8bc-6d526592b419"
    ],
    "Exchange Admin Center": [
        "497effe9-df71-4043-a8bb-14cf78c4b63b"
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
        "944f0bd1-117b-4b1c-af26-804ed95e767e"
    ],
    "Microsoft 365 Security and Compliance Center": [
        "80ccca67-54bd-44ab-8625-4b79c4dc7775"
    ],
    "Microsoft App Access Panel": [
        "0000000c-0000-0000-c000-000000000000"
    ],
    "Microsoft Approval Management": [
        "65d91a3d-ab74-42e6-8a2f-0add61688c74"
    ],
    "Microsoft 365 Support Service": [
        "ee272b19-4411-433f-8f28-5c13cb6fd407"
    ],
    "MicrosoftAzureActiveAuthn": [
        "0000001a-0000-0000-c000-000000000000"
    ],
    "Microsoft Bing Default Search Engine": [
        "1786c5ed-9644-47b2-8aa0-7201292175b6"
    ],
    "Microsoft Defender for Identity (formerly Radius Aad Syncer)": [
        "60ca1954-583c-4d1f-86de-39d835f3e452"
    ],
    "Microsoft Dynamics ERP": [
        "00000015-0000-0000-c000-000000000000"
    ],
    "Microsoft Defender for Cloud Apps": [
        "3090ab82-f1c1-4cdf-af2c-5d7a6f3e2cc7"
    ],
    "Microsoft Edge Insider Addons Prod": [
        "6253bca8-faf2-4587-8f2f-b056d80998a7"
    ],
    "Microsoft Exchange Online Protection": [
        "00000007-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Exchange ForwardSync": [
        "99b904fd-a1fe-455c-b86c-2f9fb1da7687"
    ],
    "Microsoft Forms": [
        "c9a559d2-7aab-4f13-a6ed-e7e9c52aec87"
    ],
    "Microsoft Exchange ProtectedServiceHost": [
        "51be292c-a17e-4f17-9a7e-4b661fb16dd2"
    ],
    "Microsoft Graph": [
        "00000003-0000-0000-c000-000000000000"
    ],
    "Microsoft Office 365 Portal": [
        "00000006-0000-0ff1-ce00-000000000000"
    ],
    "Microsoft Intune Web Company Portal": [
        "74bcdadc-2fdc-4bb3-8459-76d06952a0e9"
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
    "Microsoft Substrate Management": [
        "98db8bd6-0cc0-4e67-9de5-f187f1cd1b41"
    ],
    "Microsoft Stream Portal": [
        "cf53fce8-def6-4aeb-8d30-b158e7b1cf83"
    ],
    "Microsoft Storefronts": [
        "28b567f6-162c-4f54-99a0-6887f387bbcc"
    ],
    "Microsoft Support": [
        "fdf9885b-dd37-42bf-82e5-c3129ef5a302"
    ],
    "Microsoft Teams Services": [
        "cc15fd57-2c6c-4117-a88c-83b1d56b4bbe"
    ],
    "Microsoft Whiteboard Services": [
        "95de633a-083e-42f5-b444-a4295d8e9314"
    ],
    "Microsoft Teams Web Client": [
        "5e3ce6c0-2b1f-4285-8d4b-75ee78787346"
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
    "Office Online Add-in SSO": [
        "93d53678-613d-4013-afc1-62e9e444a0a5"
    ],
    "Office Online Client Microsoft Entra ID- Augmentation Loop": [
        "2abdc806-e091-4495-9b10-b04d93c3f040"
    ],
    "Office Online Client Microsoft Entra ID- Loki": [
        "b23dd4db-9142-4734-867f-3577f640ad0c"
    ],
    "Office Online Core SSO": [
        "243c63a3-247d-41c5-9d83-7788c43f1c43"
    ],
    "Office Online Client Microsoft Entra ID- Maker": [
        "17d5e35f-655b-4fb0-8ae6-86356e9a49f5"
    ],
    "Office Online Client MSA- Loki": [
        "b6e69c34-5f1f-4c34-8cdf-7fea120b8670"
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
    "OfficeShredderWacClient": [
        "4d5c2d63-cf83-4365-853c-925fd1a64357"
    ],
    "OfficeHome": [
        "4765445b-32c6-49b0-83e6-1d93765276ca"
    ],
    "OfficeClientService": [
        "0f698dd4-f011-4d23-a33e-b36416dcb1e6"
    ],
    "OneNote": [
        "fa7ff576-8e31-4a58-a5e5-780c1cd57caa"
    ],
    "OMSOctopiPROD": [
        "62256cef-54c0-4cb4-bcac-4c67989bdc40"
    ],
    "Partner Customer Delegated Admin Offline Processor": [
        "a3475900-ccec-4a69-98f5-a65cd5dc5306"
    ],
    "PeoplePredictions": [
        "35d54a08-36c9-4847-9018-93934c62740c"
    ],
    "Password Breach Authenticator": [
        "bdd48c81-3a58-4ea9-849c-ebea7f6b6360"
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
    "WeveEngine": [
        "3c896ded-22c5-450f-91f6-3d1ef0848f6e"
    ],
    "Sway": [
        "905fcf26-4eb7-48a0-9ff0-8dcc7194b5ba"
    ],
    "Transcript Ingestion": [
        "97cb1f73-50df-47d1-8fb0-0271f2728514"
    ],
    "Windows Azure Active Directory": [
        "00000002-0000-0000-c000-000000000000"
    ],
    "Viva Engage (formerly Yammer)": [
        "00000005-0000-0ff1-ce00-000000000000"
    ],
    "Windows Azure Security Resource Provider": [
        "8edd93e1-2103-40b4-bd70-6e34e586362d"
    ],
    "Yammer Web": [
        "c1c74fed-04c9-4704-80dc-9f79a2e515cb"
    ],
    "Windows Store for Business": [
        "45a330b1-b1ec-4cc1-9161-9f03992aa49f"
    ],
    "Yammer Web Embed": [
        "e1ef36fd-b883-4dbf-97f0-9ece4b576fc6"
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
    "Dynamics 365 Business Central": [
        "996def3d-b36c-4153-8607-a6fd3c01b89f"
    ],
    "Skype For Business Powershell Server Application": [
        "39624784-6cbe-4a60-afbe-9f46d10fdb27"
    ],
    "Power Query Online GCC-L2": [
        "939fe80f-2eef-464f-b0cf-705d254a2cf2"
    ],
    "Microsoft.MileIQ.Dashboard": [
        "f7069a8d-9edc-4300-b365-ae53c9627fc4"
    ],
    "O365 UAP Processor": [
        "df09ff61-2178-45d8-888c-4210c1c7b0b2"
    ],
    "Microsoft To-Do": [
        "2087bd82-7206-4c0a-b305-1321a39e5926"
    ],
    "Demeter.WorkerRole": [
        "3c31d730-a768-4286-a972-43e9b83601cd"
    ],
    "O365 Secure Score": [
        "8b3391f4-af01-4ee8-b4ea-9871b2499735"
    ],
    "Microsoft Teams AuditService": [
        "978877ea-b2d6-458b-80c7-05df932f3723"
    ],
    "Microsoft Mobile Application Management": [
        "0a5f63c0-b750-4f38-a71c-4fc0d58b89e2"
    ],
    "IDML Graph Resolver Service and CAD": [
        "d88a361a-d488-4271-a13f-a83df7dd99c2"
    ],
    "Microsoft Intune API": [
        "c161e42e-d4df-4a3d-9b42-e7a3c31f59d4"
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
    "Substrate Instant Revocation Pipeline": [
        "eace8149-b661-472f-b40d-939f89085bd4"
    ],
    "Microsoft Parature Dynamics CRM": [
        "8909aac3-be91-470c-8a0b-ff09d669af91"
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
    "Application Insights Configuration Service": [
        "6a0a243c-0886-468a-a4c2-eff52c7445da"
    ],
    "Dynamics CRM Online Administration": [
        "637fcc9f-4a9b-4aaa-8713-a2a3cfda1505"
    ],
    "ConnectionsService": [
        "b7912db9-aa33-4820-9d4f-709830fdd78f"
    ],
    "Directory and Policy Cache": [
        "7b58f833-4438-494c-a724-234928795a67"
    ],
    "Microsoft Teams AadSync": [
        "62b732f7-fc71-40bc-b27d-35efcb0509de"
    ],
    "Microsoft Office Licensing Service vNext": [
        "db55028d-e5ba-420f-816a-d18c861aefdf"
    ],
    "Microsoft Teams Partner Tenant Administration": [
        "0c708d37-30b2-4f22-8168-5d0cba6f37be"
    ],
    "Export to data lake": [
        "7f15f9d9-cad0-44f1-bbba-d36650e07765"
    ],
    "Azns AAD Webhook": [
        "461e8683-5575-4561-ac7f-899cc907d62a"
    ],
    "Microsoft Cognitive Services": [
        "7d312290-28c8-473c-a0ed-8e53749b6d6d"
    ],
    "MicrosoftAzureActiveDirectoryIntegratedApp": [
        "af47b99c-8954-4b45-ab68-8121157418ef"
    ],
    "Call Recorder": [
        "4580fd1d-e5a3-4f56-9ad1-aab0e3bf8f76"
    ],
    "Office 365 Reports": [
        "507bc9da-c4e2-40cb-96a7-ac90df92685c"
    ],
    "ProjectWorkManagement": [
        "09abbdfd-ed23-44ee-a2d9-a627aa1c90f3"
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
    "Azure AD Identity Governance": [
        "bf26f092-3426-4a99-abfb-97dad74e661a"
    ],
    "Common Data Service": [
        "00000007-0000-0000-c000-000000000000"
    ],
    "KaizalaActionsPlatform": [
        "9bb724a5-4639-438c-969b-e184b2b1e264"
    ],
    "M365 Admin Services": [
        "6b91db1b-f05b-405a-a0b2-e3f60b28d645"
    ],
    "Intune CMDeviceService": [
        "14452459-6fa6-4ec0-bc50-1528a1a06bf0"
    ],
    "SharePoint Notification Service": [
        "3138fe80-4087-4b04-80a6-8866c738028a"
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
    "Microsoft.Azure.SyncFabric": [
        "00000014-0000-0000-c000-000000000000"
    ],
    "Azure AD Identity Governance Insights": [
        "58c746b0-a0b0-4647-a8f6-12dde5981638"
    ],
    "M365 License Manager": [
        "aeb86249-8ea3-49e2-900b-54cc8e308f85"
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
    "OfficeFeedProcessors": [
        "98c8388a-4e86-424f-a176-d1288462816f"
    ],
    "WindowsDefenderATP": [
        "fc780465-2017-40d4-a0c5-307022471b92"
    ],
    "Skype for Business": [
        "7557eb47-c689-4224-abcf-aef9bd7573df"
    ],
    "Azure AD Notification": [
        "fc03f97a-9db0-4627-a216-ec98ce54e018"
    ],
    "Log Analytics API": [
        "ca7f3f0b-7d91-482c-8e09-c5d840d0eac5"
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
    "Microsoft Intune Service Discovery": [
        "9cb77803-d937-493e-9a3b-4b49de3f5a74"
    ],
    "Skype Team Substrate connector": [
        "1c0ae35a-e2ec-4592-8e08-c40884656fa5"
    ],
    "AAD App Management": [
        "f0ae4899-d877-4d3c-ae25-679e38eea492"
    ],
    "Yammer": [
        "00000005-0000-0ff1-ce00-000000000000"
    ],
    "Skype for Business Name Dictionary Service": [
        "e95d8bee-4725-4f59-910d-94d415da51b9"
    ],
    "Office 365 Import Service": [
        "3eb95cef-b10f-46fe-94e0-969a3d4c9292"
    ],
    "Microsoft.ExtensibleRealUserMonitoring": [
        "e3583ad2-c781-4224-9b91-ad15a8179ba0"
    ],
    "Microsoft Information Protection API": [
        "40775b29-2688-46b6-a3b5-b256bd04df9f"
    ],
    "Azure Notification Service": [
        "b503eb83-1222-4dcc-b116-b98ed5216e05"
    ],
    "Azure Storage": [
        "e406a681-f3d4-42a8-90b6-c2b029497af1"
    ],
    "Microsoft Discovery Service": [
        "6f82282e-0070-4e78-bc23-e6320c5fa7de"
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
    "Azure Information Protection": [
        "5b20c633-9a48-4a5f-95f6-dae91879051f"
    ],
    "Microsoft SharePoint Online \u2013 SharePoint Home": [
        "dcad865d-9257-4521-ad4d-bae3e137b345"
    ],
    "Microsoft Exact Data Match Service": [
        "273404b8-7ebc-4360-9f90-b40417f77b53"
    ],
    "Office Change Management": [
        "601d4e27-7bb3-4dee-8199-90d47d527e1c"
    ],
    "Azure Resource Graph": [
        "509e4652-da8d-478d-a730-e9d4a1996ca4"
    ],
    "O365 Demeter": [
        "982bda36-4632-4165-a46a-9863b1bbcf7d"
    ],
    "Microsoft Cloud App Security": [
        "05a65629-4c1b-48c1-a78b-804c4abdd4af"
    ],
    "Microsoft Intune": [
        "0000000a-0000-0000-c000-000000000000"
    ],
    "Azure Analysis Services": [
        "4ac7d521-0382-477b-b0f8-7e1d95f85ca2"
    ],
    "Microsoft Seller Dashboard": [
        "0000000b-0000-0000-c000-000000000000"
    ],
    "Microsoft Power BI Information Service": [
        "0000001b-0000-0000-c000-000000000000"
    ],
    "Service Encryption": [
        "dbc36ae1-c097-4df9-8d94-343c3d091a76"
    ],
    "MS Teams Griffin Assistant": [
        "c9224372-5534-42cb-a48b-8db4f4a3892e"
    ],
    "Microsoft Office Licensing Service Agents": [
        "d7097cd1-c779-44d0-8c71-ab1f8386a97e"
    ],
    "Microsoft.OfficeModernCalendar": [
        "ab27a73e-a3ba-4e43-8360-8bcc717114d8"
    ],
    "Cortana Runtime Service": [
        "81473081-50b9-469a-b9d8-303109583ecb"
    ],
    "Azure Multi-Factor Auth Connector": [
        "1f5530b3-261a-47a9-b357-ded261e17918"
    ],
    "Storage Resource Provider": [
        "a6aa9161-5291-40bb-8c5c-923b567bee3b"
    ],
    "PushChannel": [
        "4747d38e-36c5-4bc3-979b-b0ef74df54d1"
    ],
    "Graph Connector Service": [
        "56c1da01-2129-48f7-9355-af6d59d42766"
    ],
    "Microsoft Teams Graph Service": [
        "ab3be6b7-f5df-413d-ac2d-abf1e3fd9c0b"
    ],
    "Skype Business Voice Directory": [
        "27b24f1f-688b-4661-9594-0fdfde972edc"
    ],
    "Azure Multi-Factor Auth Client": [
        "981f26a1-7f43-403b-a875-f8b09b8cd720"
    ],
    "Centralized Deployment": [
        "257601fd-462f-4a21-b623-7f719f0f90f4"
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
    "Microsoft Azure Policy Insights": [
        "1d78a85d-813d-46f0-b496-dd72f50a3ec0"
    ],
    "O365 Customer Monitoring": [
        "3aa5c166-136f-40eb-9066-33ac63099211"
    ],
    "Discovery Service": [
        "d29a4c00-4966-492a-84dd-47e779578fb7"
    ],
    "Azure Monitor Restricted": [
        "035f9e1d-4f00-4419-bf50-bf2d87eb4878"
    ],
    "Policy Administration Service": [
        "0469d4cd-df37-4d93-8a61-f8c75b809164"
    ],
    "App Studio for Microsoft Teams": [
        "e1979c22-8b73-4aed-a4da-572cc4d0b832"
    ],
    "Microsoft Exact Data Match Upload Agent": [
        "b51a99a9-ccaa-4687-aa2c-44d1558295f4"
    ],
    "Application Insights API": [
        "f5c26e74-f226-4ae8-85f0-b4af0080ac9e"
    ],
    "Targeted Messaging Service": [
        "4c4f550b-42b2-4a16-93f9-fdb9e01bb6ed"
    ],
    "Microsoft Social Engagement": [
        "e8ab36af-d4be-4833-a38b-4d6cf1cfd525"
    ],
    "Azure Advisor": [
        "c39c9bac-9d1f-4dfb-aa29-27f6365e5cb7"
    ],
    "Microsoft Teams VSTS": [
        "a855a166-fd92-4c76-b60d-a791e0762432"
    ],
    "Microsoft Service Trust": [
        "d6fdaa33-e821-4211-83d0-cf74736489e1"
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
    "Microsoft Intune Enrollment": [
        "d4ebce55-015a-49b5-a083-c84d1797ae8c"
    ],
    "Microsoft Invoicing": [
        "b6b84568-6c01-4981-a80f-09da9a20bbed"
    ],
    "AzureLockbox": [
        "a0551534-cfc9-4e1f-9a7a-65093b32bb38"
    ],
    "Skype Teams Calling API Service": [
        "26a18ebc-cdf7-4a6a-91cb-beb352805e81"
    ],
    "Microsoft Teams Chat Aggregator": [
        "b1379a75-ce5e-4fa3-80c6-89bb39bf646c"
    ],
    "Reply-At-Mention": [
        "18f36947-75b0-49fb-8d1c-29584a55cac5"
    ],
    "Microsoft Rights Management Services": [
        "00000012-0000-0000-c000-000000000000"
    ],
    "Microsoft Teams \u2013 Teams And Channels Service": [
        "b55b276d-2b09-4ad2-8de5-f09cf24ffba9"
    ],
    "Request Approvals Read Platform": [
        "d8c767ef-3e9a-48c4-aef9-562696539b39"
    ],
    "Microsoft Device Directory Service": [
        "8f41dc7c-542c-4bdd-8eb3-e60543f607ca"
    ],
    "Windows Azure Application Insights": [
        "11c174dc-1945-4a9a-a36b-c79a0f246b9b"
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
    "Microsoft Office Licensing Service": [
        "8d3a7d3c-c034-4f19-a2ef-8412952a9671"
    ],
    "Data Classification Service": [
        "7c99d979-3b9c-4342-97dd-3239678fb300"
    ],
    "Microsoft Intune Checkin": [
        "26a4ae64-5862-427f-a9b0-044e62572a4f"
    ],
    "Office 365 Management APIs": [
        "c5393580-f805-4401-95e8-94b7a6ef2fc2"
    ],
    "Microsoft Azure AD Identity Protection": [
        "a3dfc3c6-2c7d-4f42-aeec-b2877f9bce97"
    ],
    "Microsoft Mobile Application Management Backend": [
        "354b5b6d-abd6-4736-9f51-1be80049b91f"
    ],
    "OCPS Checkin Service": [
        "23c898c1-f7e8-41da-9501-f16571f8d097"
    ],
    "Microsoft.DynamicsMarketing": [
        "9b06ebd4-9068-486b-bdd2-dac26b8a5a7a"
    ],
    "OneProfile Service": [
        "b2cc270f-563e-4d8a-af47-f00963a71dcd"
    ],
    "Microsoft Flow CDS Integration Service TIP1": [
        "eacba838-453c-4d3e-8c6a-eb815d3469a3"
    ],
    "Microsoft Teams Shifts": [
        "aa580612-c342-4ace-9055-8edee43ccb89"
    ],
    "Azure AD Identity Governance \u2013 SPO Management": [
        "396e7f4b-41ea-4851-b04d-65de6cf1b4a3"
    ],
    "Microsoft Flow Service": [
        "7df0a125-d3be-4c96-aa54-591f83ff541c"
    ],
    "Microsoft Intune Advanced Threat Protection Integration": [
        "794ded15-70c6-4bcd-a0bb-9b7ad530a01a"
    ],
    "AADPremiumService": [
        "bf4fa6bf-d24c-4d1c-8cfd-12063dd646b2"
    ],
    "IAMTenantCrawler": [
        "66244124-575c-4284-92bc-fdd00e669cea"
    ],
    "Microsoft.Azure.DataMarket": [
        "00000008-0000-0000-c000-000000000000"
    ],
    "O365SBRM Service": [
        "9d06afd9-66c9-49a6-b385-ea7509332b0b"
    ],
    "Microsoft Policy Insights Provider Data Plane": [
        "8cae6e77-e04e-42ce-b5cb-50d82bce26b1"
    ],
    "Azure AD Identity Governance \u2013 Entitlement Management": [
        "810dcf14-1858-4bf2-8134-4c369fa3235b"
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
    "Microsoft.SMIT": [
        "8fca0a66-c008-4564-a876-ab3ae0fd5cff"
    ],
    "AI Builder Authorization Service": [
        "ad40333e-9910-4b61-b281-e3aeeb8c3ef3"
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
    "O365Account": [
        "1cda9b54-9852-4a5a-96d4-c2ab174f9edf"
    ],
    "PowerAI": [
        "8b62382d-110e-4db8-83a6-c7e8ee84296a"
    ],
    "Dynamics Lifecycle services": [
        "913c6de4-2a4a-4a61-a9ce-945d2b2ce2e0"
    ],
    "Microsoft Teams RetentionHook Service": [
        "f5aeb603-2a64-4f37-b9a8-b544f3542865"
    ],
    "Skype and Teams Tenant Admin API": [
        "48ac35b8-9aa8-4d74-927d-1f4a14a0b239"
    ],
    "OCaaS Client Interaction Service": [
        "c2ada927-a9e2-4564-aae2-70775a2fa0af"
    ],
    "Microsoft Teams Wiki Images Migration": [
        "823dfde0-1b9a-415a-a35a-1ad34e16dd44"
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
    "PowerAppsService": [
        "331cc017-5973-4173-b270-f0042fddfd75"
    ],
    "PowerApps-Advisor": [
        "c9299480-c13a-49db-a7ae-cdfe54fe0313"
    ],
    "StreamToSubstrateRepl": [
        "607e1f95-b519-4bac-8a15-6196f40e8977"
    ],
    "Teams ACL management service": [
        "6208afad-753e-4995-bbe1-1dfd204b3030"
    ],
    "MicrosoftPowerBI": [
        "871c010f-5e61-4fb1-83ac-98610a7e9110"
    ],
    "PowerApps": [
        "0cb2a3b9-c0b0-4f92-95e2-8955085f78c2"
    ],
    "AzureHDInsightonAKSClient": [
        "a6943a7f-5ba0-4a34-bf91-ab439efdda3f"
    ],
    "OneDrive": [
        "766d89a4-d6a6-444d-8a5e-e1a18622288a",
        "6a9b9266-8161-4a7b-913a-a9eda19da220"
    ],
    "BrowserStack": [
        "180f19aa-1b79-4b4a-b716-068b81cfb145"
    ],
    "Azure ContainerApps Auth": [
        "6104ad52-755e-428b-9fb5-5fdf4d2c4d53"
    ],
    "Azure HDInsight Service": [
        "9191c4da-09fe-49d9-a5f1-d41cbe92ad95"
    ],
    "Azure Monitor Edge resource provider application": [
        "7d307c7e-d1c0-4b3f-976d-094279ad11ab"
    ],
    "o365.servicecommunications.microsoft.com": [
        "cb1bda4c-1213-4e8b-911a-0a8c83c5d3b7"
    ],
    "Azure SQL Managed Instance to Azure AD Resource Provider": [
        "9c8b80bc-6887-42d0-b1af-d0c40f9bf1fa"
    ],
    "Azure Database for PostgreSQL Flexible Server Private Network Integration": [
        "93efed00-6552-4119-833a-422b297199f9"
    ],
    "P2P Server": [
        "ec371b95-98fd-482b-abbe-bb6dc47ac04e"
    ],
    "blackbox-lab-1-sql-identity": [
        "3e861d75-0d91-4031-8425-f31d98b2177d",
        "df86db7c-a8df-4912-8db2-660efbac95bd"
    ],
    "CABProvisioning": [
        "5da7367f-09c8-493e-8fd4-638089cddec3"
    ],
    "Microsoft Rights Management Services Default": [
        "934d626a-1ead-4a36-a77d-12ec63b87a0d"
    ],
    "Azure Files": [
        "69dda2a9-33ca-4ed0-83fb-a9b7b8973ff4"
    ],
    "f69ef6de-iam-lab-1-start-point": [
        "cefdce59-40c7-40e5-8644-3a31f8a1fc5d"
    ],
    "Databricks Resource Provider": [
        "d9327919-6775-4843-9037-3fb0fb0473cb"
    ],
    "Microsoft Azure Signup Portal": [
        "8e0e8db5-b713-4e91-98e6-470fed0aa4c2"
    ],
    "Azure Data Warehouse Polybase": [
        "0130cc9f-7ac5-4026-bd5f-80a08a54e6d9"
    ],
    "Narada Notification Service": [
        "51b5e278-ed7e-42c6-8787-7ff93e92f577"
    ],
    "MDC Data Sensitivity": [
        "bd6d9218-235b-4abd-b3be-9ff157dcf36c"
    ],
    "Azure CosmosDB for PostgreSQL Microsoft EntraId": [
        "ecafc2d9-cf1a-49a7-b60f-e44e34a988d2"
    ],
    "Azure Vmware Solutions RP Internal": [
        "abbab087-6193-40ef-a96c-6be85a5f43a0"
    ],
    "Azure Iot Hub Publisher App": [
        "29f411f1-b2cf-4043-8ac8-2185d7316811"
    ],
    "AzS VIS Prod App": [
        "a766fecb-91ef-4d42-8bd3-41a61b3eb0e5"
    ],
    "Azure DNS": [
        "19947cfd-0303-466c-ac3c-fcc19a7a1570"
    ],
    "Microsoft.ServiceBus": [
        "80a10ef9-8168-493d-abf9-3297c4ef6e3c"
    ],
    "Domain Controller Services": [
        "2565bd9d-da50-47d4-8b85-4c97f669dc36",
        "443155a6-77f3-45e3-882b-22b3a8d431fb",
        "d87dcbc6-a371-462e-88e3-28ad15ec4e64",
        "abba844e-bc0e-44b0-947a-dc74e5d09022"
    ],
    "Microsoft Azure Network Copilot": [
        "40c49ff3-c6ae-436d-b28e-b8e268841980"
    ],
    "Microsoft.EventGrid": [
        "4962773b-9cdb-44cf-a8bf-237846a00ab7"
    ],
    "Managed Service Identity": [
        "ef5d5c69-a5df-46bb-acaf-426f161a21a2"
    ],
    "Backup Management Service": [
        "262044b1-e2ce-469f-a196-69ab7ada62d3"
    ],
    "Azure OSSRDBMS MySQL Flexible Server BYOK": [
        "cb43afba-eb6b-4cef-bf00-758b6c233beb"
    ],
    "Azure Iot Hub": [
        "89d10474-74af-4874-99a7-c23c2f643083"
    ],
    "Azure Spring Apps Domain-Management Dogfood": [
        "584a29b4-7876-4445-921e-71e427d4f4b3"
    ],
    "Billing RP": [
        "80dbdb39-4f33-4799-8b6f-711b5e3e61b6"
    ],
    "daa48835-lab3_vm_network": [
        "b943a7a2-80bd-40e7-831d-41c1f4094aa5"
    ],
    "Azure Lab Services": [
        "1a14be2a-e903-4cec-99cf-b2e209259a0f"
    ],
    "Azure App Configuration": [
        "35ffadb3-7fc1-497e-b61b-381d28e744cc"
    ],
    "Managed Service": [
        "66c6d0d1-f2e7-4a18-97a9-ed10f3347016"
    ],
    "Defender for Storage Advanced Threat Protection Resource Provider": [
        "080765e3-9336-4461-b934-310acccb907d"
    ],
    "Microsoft Azure App Service": [
        "abfa0a7c-a6b6-4736-8310-5855508787cd"
    ],
    "AzureVirtualNetworkManager": [
        "6d057c82-a784-47ae-8d12-ca7b38cf06b4"
    ],
    "blackbox-lab-1-user-identity": [
        "6b34094b-1288-414a-93cb-9d29d5644f0b"
    ],
    "Afdx Resource Provider": [
        "92b61450-2139-4e4a-a0cc-898eced7a779"
    ],
    "Microsoft.CustomProviders RP": [
        "bf8eb16c-7ba7-4b47-86be-ac5e4b2007a5"
    ],
    "CosmosDB Dedicated Instance": [
        "36e2398c-9dd3-4f29-9a72-d9f2cfc47ad9"
    ],
    "Azure API Management": [
        "8602e328-9b72-4f2d-a4ae-1387d013a2b3"
    ],
    "Azure Virtual Desktop ARM Provider": [
        "50e95039-b200-4007-bc97-8d5790743a63"
    ],
    "Cloud Infrastructure Entitlement Management": [
        "b46c3ac5-9da6-418f-a849-0a07a10b3c6c"
    ],
    "Azure Spring Cloud Service Runtime Auth": [
        "366cbfa5-46b3-47fb-9d70-55fb923b4833"
    ],
    "Access IoT Hub Device Provisioning Service": [
        "0cd79364-7a90-4354-9984-6e36c841418d"
    ],
    "Microsoft Azure IPAM": [
        "60b2e7d5-a27f-426d-a6b1-acced0846fdf"
    ],
    "Microsoft Defender for Cloud Apps - Customer Experience": [
        "ac6dbf5e-1087-4434-beb2-0ebf7bd1b883"
    ],
    "Azure Spring Cloud DiagSettings App": [
        "b61cc489-e138-4a69-8bf3-c2c5855c8784"
    ],
    "f69ef6de-app-service-lab-3-start-point": [
        "57d1b1e9-b593-4e07-9818-2d5bcffe77dd"
    ],
    "Sherlock": [
        "0e282aa8-2770-4b6c-8cf8-fac26e9ebe1f"
    ],
    "Azure API for DICOM": [
        "75e725bf-66ce-4cea-9b9a-5c4caae57f33"
    ],
    "Microsoft Modern Contact Master": [
        "224a7b82-46c9-4d6b-8db0-7360fb444681"
    ],
    "Diagnostic Services Data Access": [
        "3603eff4-9141-41d5-ba8f-02fb3a439cd6"
    ],
    "ResourceHealthRP": [
        "8bdebf23-c0fe-4187-a378-717ad86f6a53"
    ],
    "Microsoft Azure Legion": [
        "55ebbb62-3b9c-49fd-9b87-9595226dd4ac"
    ],
    "Microsoft.Relay": [
        "91bb937c-29c2-4275-982f-9465f0caf03d"
    ],
    "blackbox-lab-1-vm-2": [
        "242847be-a574-4252-b4d4-55ceecdd23cc"
    ],
    "ComplianceAuthServer": [
        "9e5d84af-8971-422f-968a-354cd675ae5b"
    ],
    "Azure Security for IoT": [
        "cfbd4387-1a16-4945-83c0-ec10e46cd4da"
    ],
    "AML Registries": [
        "44b7b882-eb46-485c-9c78-686f6b67b176"
    ],
    "Defender for IoT - Management": [
        "3157152d-b5ae-4606-a145-6c660069bc5e"
    ],
    "storageDataScanner": [
        "6194fed8-4d8c-4325-abba-765419dcc96b"
    ],
    "Azure Container Scale Sets - CS2": [
        "63ea3c01-7483-456e-8073-d3fed34fbdda"
    ],
    "Bot Service Resource Provider": [
        "e6650347-047f-4e51-9386-839384472ea5"
    ],
    "NFV Resource Provider": [
        "328fd23b-de6e-462c-9433-e207470a5727"
    ],
    "Azure Maps": [
        "ba1ea022-5807-41d5-bbeb-292c7e1cf5f6"
    ],
    "Metrics Monitor API": [
        "12743ff8-d3de-49d0-a4ce-6c91a4245ea0"
    ],
    "lab2-runcommand": [
        "887c0706-5ec3-4f10-a28a-290d704fad47"
    ],
    "f69ef6de-iam-lab-2-start-point": [
        "58a5cae3-760e-4e30-8c9c-c05a690f33af"
    ],
    "Azure Blueprints": [
        "f71766dc-90d9-4b7d-bd9d-4499c4331c3f"
    ],
    "Hyper-V Recovery Manager": [
        "b8340c3b-9267-498f-b21a-15d5547fd85e"
    ],
    "Azure OSSRDBMS PostgreSQL Flexible Server AAD Authentication": [
        "5657e26c-cc92-45d9-bc47-9da6cfdb4ed9"
    ],
    "Azure Bastion": [
        "79d7fb34-4bef-4417-8184-ff713af7a679"
    ],
    "Microsoft Azure Alerts Management": [
        "161a339d-b9f5-41c5-8856-6a6669acac64"
    ],
    "Azure Key Vault": [
        "cfa8b339-82a2-471a-a3c9-0fc0be7a4093"
    ],
    "PPE-DataResidencyService": [
        "dc457883-bafe-4f8b-a333-29685e7eaa9e"
    ],
    "Azure Help Resource Provider": [
        "fd225045-a727-45dc-8caa-77c8eb1b9521"
    ],
    "networkcopilotRP": [
        "d66e9e8e-53a4-420c-866d-5bb39aaea675"
    ],
    "Azure Commercial Services Tool - CST": [
        "801546d2-55cc-4ff4-b66d-134b1208deb5"
    ],
    "Azure Update Manager": [
        "c476eb34-4c94-43bc-97fc-94ede0534615"
    ],
    "Azure Logic Apps": [
        "7cd684f4-8a78-49b0-91ec-6a35d38739ba"
    ],
    "Azure Virtual Desktop Client": [
        "a85cf173-4192-42f8-81fa-777a763e6e2c"
    ],
    "Microsoft Mixed Reality": [
        "c7ddd9b4-5172-4e28-bd29-1e0792947d18"
    ],
    "EASM API": [
        "b7faa489-a4c8-4b39-bb0c-842c3de2de6a"
    ],
    "SQLDBControlPlaneFirstPartyApp": [
        "ceecbdd6-288c-4be9-8445-74f139e5db19"
    ],
    "Azure Cosmos DB Virtual Network To Network Resource Provider": [
        "57c0fc58-a83a-41d0-8ae9-08952659bdfd"
    ],
    "Azure Service Connector Resource Provider": [
        "c4288165-6698-45ba-98a5-48ea7791fed3"
    ],
    "Azure Cost Management XCloud": [
        "3184af01-7a88-49e0-8b55-8ecdce0aa950"
    ],
    "AzureBackup_WBCM_Service": [
        "c505e273-0ba0-47e7-a0bd-f48042b4524d"
    ],
    "Diagnostic Services Trusted Storage Access": [
        "562db366-1b96-45d2-aa4a-f2148cef2240"
    ],
    "Office 365 Information Protection": [
        "2f3f02c9-5679-4a5c-a605-0de55b07d135"
    ],
    "Microsoft B2B Admin Worker": [
        "1e2ca66a-c176-45ea-a877-e87f7231e0ee"
    ],
    "AML Inferencing Frontdoor": [
        "6608bce8-e060-4e82-bfd2-67ed4f60262f"
    ],
    "Azure Compute": [
        "579d9c9d-4c83-4efc-8124-7eba65ed3356"
    ],
    "Azure HDInsight Cluster API": [
        "7865c1d2-f040-46cc-875f-831a1ef6a28a"
    ],
    "Compute Recommendation Service": [
        "b9a92e36-2cf8-4f4e-bcb3-9d99e00e14ab"
    ],
    "Azure Windows VM Sign-In": [
        "372140e0-b3b7-4226-8ef9-d57986796201"
    ],
    "Azure Monitor Control Service": [
        "e933bd07-d2ee-4f1d-933c-3752b819567b"
    ],
    "Microsoft Defender for Cloud for AI": [
        "1efb1569-5fd6-4938-8b8d-9f3aa07c658d"
    ],
    "Azure Virtual Desktop": [
        "9cdead84-a844-4324-93f2-b2e6bb768d07"
    ],
    "3b6d0d3d-keyvault-lab-3-start-point": [
        "160a31a4-4a07-4dad-80c3-b64bbf662fda"
    ],
    "3b6d0d3d-keyvault-lab-1-start-point": [
        "6ae40586-e725-40a3-b7c4-5549df5c3393"
    ],
    "Azure Healthcare APIs": [
        "4f6778d8-5aef-43dc-a1ff-b073724b9495"
    ],
    "Azure Machine Learning Authorization App 1": [
        "fb9de05a-fecc-4642-b3ca-66b9d4434d4d"
    ],
    "Azure Spring Cloud Domain-Management": [
        "03b39d0f-4213-4864-a245-b1476ec03169"
    ],
    "Azure Container Registry Application": [
        "76c92352-c057-4cc2-9b1e-f34c32bc58bd"
    ],
    "Marketplace SaaS v2": [
        "5b712e99-51a3-41ce-86ff-046e0081c5c0"
    ],
    "People Profile Event Proxy": [
        "65c8bd9e-caac-4816-be98-0692f41191bc"
    ],
    "MS-PIM": [
        "01fc33a7-78ba-4d2f-a4b7-768e336e890e"
    ],
    "ACR-Tasks-Network": [
        "62c559cd-db0c-4da0-bab2-972528c65d42"
    ],
    "Azure Kubernetes Service - Fleet RP": [
        "609d2f62-527f-4451-bfd2-ac2c7850822c"
    ],
    "AzureBackup_Fabric_Service": [
        "e81c7467-0fc3-4866-b814-c973488361cd"
    ],
    "Azure Linux VM Sign-In": [
        "ce6ff14a-7fdc-4685-bbe0-f6afdfcfa8e0"
    ],
    "MarketplaceAPI ISV": [
        "20e940b3-4c77-4b0b-9a53-9e16a1b010a7"
    ],
    "Azure VMware Solution RP": [
        "608f9929-9737-432e-860f-4e1c1821052f"
    ],
    "Azure Application Change Service": [
        "3edcf11f-df80-41b2-a5e4-7e213cca30d1",
        "2cfc91a4-7baa-4a8f-a6c9-5f3d279060b8"
    ],
    "12345TestingRegistry/credentialSets/qwergtfd": [
        "8856febc-1450-47cf-b24e-5373b123df45"
    ],
    "Azure SQL Database Backup To Azure Backup Vault": [
        "e4ab13ed-33cb-41b4-9140-6e264582cf85"
    ],
    "K8 Bridge": [
        "319f651f-7ddb-4fc6-9857-7aef9250bd05"
    ],
    "Compute Artifacts Publishing Service": [
        "a8b6bf88-1d1a-4626-b040-9a729ea93c65"
    ],
    "MicrosoftGuestConfiguration": [
        "e935b4a5-8968-416d-8414-caed51c782a9"
    ],
    "CloudPosture/securityOperators/DefenderCSPMSecurityOperator": [
        "4ef102c8-8b6a-4e62-a214-907290e7f75b"
    ],
    "My Profile": [
        "8c59ead7-d703-4a27-9e55-c96a0054c8d2"
    ],
    "Microsoft Azure Vnet Verifier": [
        "6e02f8e9-db9b-4eb5-aa5a-7c8968375f68"
    ],
    "Bot Service Token Store": [
        "5b404cf4-a79d-4cfe-b866-24bf8e1a4921"
    ],
    "Microsoft Azure Log Search Alerts": [
        "f6b60513-f290-450e-a2f3-9930de61c5e7"
    ],
    "Managed Disks Resource Provider": [
        "60e6cd67-9c8c-4951-9b3c-23c25a2169af"
    ],
    "Azure Regional Service Manager": [
        "5e5e43d4-54da-4211-86a4-c6e7f3715801"
    ],
    "Azure Machine Learning Compute": [
        "607ece82-f922-494f-88b8-30effaf12214"
    ],
    "Microsoft_Azure_Support": [
        "959678cf-d004-4c22-82a6-d2ce549a58b8"
    ],
    "SubscriptionRP": [
        "e3335adb-5ca0-40dc-b8d3-bedc094e523b"
    ],
    "Compute Usage Provider": [
        "a303894e-f1d8-4a37-bf10-67aa654a0596"
    ],
    "Microsoft Invitation Acceptance Portal": [
        "4660504c-45b3-4674-a709-71951a6b0763"
    ],
    "Azure ContainerApps Sessions": [
        "2c7dd73f-7a21-485b-b97d-a2508fa152c3"
    ],
    "Microsoft Azure Stream Analytics": [
        "66f1e791-7bfb-4e18-aed8-1720056421c7"
    ],
    "Azure CosmosDB for PostgreSQL AAD Authentication": [
        "b4fa09d8-5da5-4352-83d9-05c2a44cf431"
    ],
    "Azure Healthcare APIs RBAC": [
        "3274406e-4e0a-4852-ba4f-d7226630abb7"
    ],
    "Microsoft Remote Desktop": [
        "a4a365df-50f1-4397-bc59-1a1564b8bb9c"
    ],
    "Azure Spring Cloud Resource Provider": [
        "e8de9221-a19c-4c81-b814-fd37c6caf9d2"
    ],
    "Azure Container Apps Arc - Data Plane": [
        "409eb69a-5e20-4e1e-a8bf-c23300057950"
    ],
    "Microsoft Operations Management Suite": [
        "d2a0a418-0aac-4541-82b2-b3142c89da77"
    ],
    "1db82ba9-app-service-lab-3-start-point": [
        "6e531ba0-edf9-436e-a587-b60a75b63458"
    ],
    "ACR-Tasks-Prod": [
        "d2fa1650-4805-4a83-bcb9-cf41fe63539c"
    ],
    "GatewayRP": [
        "486c78bf-a0f7-45f1-92fd-37215929e116"
    ],
    "Microsoft Defender for Cloud CIEM": [
        "a70c8393-7c0c-4c1e-916a-811bd476ee11"
    ],
    "MDATPNetworkScanAgent": [
        "04687a56-4fc2-4e36-b274-b862fb649733"
    ],
    "app-s-2-f69ef6de": [
        "ca566c25-61ea-42ba-ac73-448bcf187aa5"
    ],
    "Azure Machine Learning Services": [
        "18a66f5f-dbdf-4c17-9dd7-1634712a9cbe"
    ],
    "Network Watcher": [
        "7c33bfcb-8d33-48d6-8e60-dc6404003489"
    ],
    "OMSAuthorizationServicePROD": [
        "50d8616b-fd4f-4fac-a1c9-a6a9440d7fe0"
    ],
    "Azure Security Insights": [
        "98785600-1bb7-4fb9-b9fa-19afe2c8a360"
    ],
    "Meru19 MySQL First Party App": [
        "e6f9f783-1fdb-4755-acaf-abed6c642885"
    ],
    "AzureContainerService": [
        "7319c514-987d-4e9b-ac3d-d38c4f427f4c"
    ],
    "1db82ba9-app-service-lab-2-start-point": [
        "6eca5007-5e28-45f5-b627-7d005b031afa"
    ],
    "aciapi": [
        "c5b17a4f-cc6f-4649-9480-684280a2af3a"
    ],
    "Azure HDInsight Surrogate Service": [
        "5a543d7c-9c4a-4f90-8cc7-6ae082a5b65b"
    ],
    "entra-id-lab-2-app-94a5f990": [
        "97992bab-9916-4237-bf9e-7a667e95f99e"
    ],
    "Azure SignalR Service Resource Provider": [
        "cdad765c-f191-43ba-b9f5-7aef392f811d"
    ],
    "Azure Container Registry - Dataplane": [
        "a3747411-ce7c-4888-9ddc-3a230786ca19"
    ],
    "PROD Microsoft Defender For Cloud XDR": [
        "3f6aecb4-6dbf-4e45-9141-440abdced562"
    ],
    "Azure AD Application Proxy": [
        "47ee738b-3f1a-4fc7-ab11-37e4822b007e"
    ],
    "Azure Maps Resource Provider": [
        "608f6f31-fed0-4f7b-809f-90f6c9b3de78"
    ],
    "CMAT": [
        "64a7b174-5779-4506-b54c-fbb0d80f1c9b"
    ],
    "Data Migration Service": [
        "a4bad4aa-bf02-4631-9f78-a64ffdba8150"
    ],
    "Azure Backup NRP Application": [
        "9bdab391-7bbe-42e8-8132-e4491dc29cc0"
    ],
    "Microsoft Defender for APIs Resource Provider": [
        "56823b05-67d8-413a-b6ab-ad19d7710cf2"
    ],
    "Microsoft Defender for Cloud Pricing Resource Provider": [
        "cbff9545-769a-4b41-b76e-fbb069e8727e"
    ],
    "Office365DirectorySynchronizationService": [
        "18af356b-c4fd-4f52-9899-d09d21397ab7"
    ],
    "AzureDnsFrontendApp": [
        "a0be0c72-870e-46f0-9c49-c98333a996f7"
    ],
    "blackbox-lab-1-vm-1": [
        "d3aee5ed-b79a-4e81-bc0a-9110b1e08bee"
    ],
    "Azure Credential Configuration Endpoint Service": [
        "ea890292-c8c8-4433-b5ea-b09d0668e1a6"
    ],
    "RedisEnterprise Service": [
        "132709ba-1394-4eb6-a565-e62a83ca14f9"
    ],
    "Azure Machine Learning Authorization App 2": [
        "bf283ae6-5efd-44a8-b56a-2a7939982d60"
    ],
    "SQLVMResourceProviderAuth": [
        "bd93b475-f9e2-476e-963d-b2daf143ffb9"
    ],
    "MicrosoftAzureRedisCache": [
        "96231a05-34ce-4eb4-aa6a-70759cbb5e83"
    ],
    "CompliancePolicy": [
        "644c1b11-f63f-45fa-826b-a9d2801db711"
    ],
    "Azure Data Factory": [
        "5d13f7d7-0567-429c-9880-320e9555e5fc",
        "0947a342-ab4a-43be-93b3-b8243fc161e5"
    ],
    "Azure Cosmos DB": [
        "a232010e-820c-4083-83bb-3ace5fc29d0b"
    ],
    "Marketplace Caps API": [
        "184909ca-69f1-4368-a6a7-c558ee6eb0bd"
    ],
    "MaintenanceResourceProvider": [
        "f18474f2-a66a-4bb0-a3c9-9b8d892092fa"
    ],
    "Azure Media Services": [
        "374b2a64-3b6b-436b-934c-b820eacca870"
    ],
    "ASA Curation Web Tool": [
        "a15bc1de-f777-408f-9d2b-a27ed19c72ba"
    ],
    "f69ef6de-app-service-lab-1-start-point": [
        "322d9ee4-d78b-48c4-8360-22dcd4966385"
    ],
    "Microsoft Monitoring Account Management": [
        "e158b4a5-21ab-442e-ae73-2e19f4e7d763"
    ],
    "Azure Traffic Manager and DNS": [
        "2cf9eb86-36b5-49dc-86ae-9a63135dfa8c"
    ],
    "AzureAutomation": [
        "fc75330b-179d-49af-87dd-3b1acf6827fa"
    ],
    "easmApiDev": [
        "9a751391-6e9f-4199-ad8d-360712a1285c"
    ],
    "1db82ba9-app-service-lab-1-start-point": [
        "31a38324-75a1-4393-9148-4c58b6850c00"
    ],
    "Azure Search Management": [
        "408992c7-2af6-4ff1-92e3-65b73d2b5092"
    ],
    "Azure SQL Managed Instance to Microsoft.Network": [
        "76c7f279-7959-468f-8943-3954880e0d8c"
    ],
    "OCaaS Experience Management Service": [
        "6e99704e-62d5-40f6-b2fe-90aafbe3a710"
    ],
    "Azure Container Registry": [
        "6a0ec4d3-30cb-4a83-91c0-ae56bc0e3d26"
    ],
    "Azure DNS Managed Resolver": [
        "b4ca0290-4e73-4e31-ade0-c82ecfaabf6a"
    ],
    "Office365 Shell SS-Server Default": [
        "6872b314-67ab-4a16-98e7-a663b0f772c3"
    ],
    "Bot Service CMEK Prod": [
        "27a762be-14e7-4f92-899c-151877d6d497"
    ],
    "Azure Cloud Shell": [
        "2233b157-f44d-4812-b777-036cdaf9a96e"
    ],
    "OCaaS Worker Services": [
        "167e2ded-f32d-49f5-8a10-308b921bc7ee"
    ],
    "Microsoft Graph Change Tracking": [
        "0bf30f3b-4a52-48df-9a82-234910c4a086"
    ],
    "Azure Container Instance Service": [
        "6bb8e274-af5d-4df2-98a3-4fd78b4cafd9"
    ],
    "AzureBackupReporting": [
        "3b2fa68d-a091-48c9-95be-88d572e08fb7"
    ],
    "Microsoft Defender for Cloud MultiCloud Onboarding": [
        "81172f0f-5d81-47c7-96f6-49c58b60d192"
    ],
    "Azure Support - Network Watcher": [
        "341b7f3d-69b3-47f9-9ce7-5b7f4945fdbd"
    ],
    "Azure Spring Cloud Marketplace Integration": [
        "86adf623-eea3-4453-9f4a-18134ac1410d"
    ],
    "Microsoft.NotificationHubs": [
        "3caf7e80-c1dc-4cbc-811c-d281c9d5e45c"
    ],
    "Azure Container Apps Arc - Control Plane": [
        "1459b1f6-7a5b-4300-93a2-44b4a651759f"
    ],
    "Azure Storage Insights Resource Provider": [
        "b15f3d14-f6d1-4c0d-93da-d4136c97f006"
    ],
    "Microsoft Azure Container Apps - Control Plane": [
        "7e3bc4fd-85a3-4192-b177-5b8bfc87f42c"
    ],
    "Azure Machine Learning OpenAI": [
        "61c50b89-703d-431d-8d80-1e8618748775"
    ],
    "Azure Kubernetes Service AAD Server": [
        "6dae42f8-4368-4678-94ff-3960e28e3630"
    ],
    "Office365 Shell WCSS-Server Default": [
        "a68e1e61-ad4f-45b6-897d-0a1ea8786345"
    ],
    "Microsoft Threat Protection": [
        "8ee8fdad-f234-4243-8f3b-15c294843740"
    ],
    "Microsoft Container Registry": [
        "a4c95b9e-3994-40cc-8953-5dc66d48348d"
    ],
    "3b6d0d3d-keyvault-lab-2-start-point": [
        "735882e3-d313-453a-b1ae-670e3d9d3dd5"
    ],
    "Microsoft Defender for Cloud Scanner Resource Provider": [
        "e0ccf59d-5a20-4a87-a122-f42842cdb86a"
    ],
    "app-s-2-1db82ba9": [
        "167757ef-d3c8-4267-8df1-017162813cc3"
    ],
    "Microsoft Defender for Cloud Defender Kubernetes Agent": [
        "6e2cffc9-52e7-4bfa-8155-be5c1dacd81c"
    ],
    "Microsoft Azure BatchAI": [
        "9fcb3732-5f52-4135-8c08-9d4bbaf203ea"
    ],
    "Azure Management Groups": [
        "f2c304cf-8e7e-4c3f-8164-16299ad9d272"
    ],
    "AzureDatabricks": [
        "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d"
    ],
    "Azure Cognitive Search": [
        "880da380-985e-4198-81b9-e05b1cc53158"
    ],
    "blackbox-lab-1-automation": [
        "818a46f2-0634-42ef-b476-15753299a620"
    ],
    "Service Bus MSI App": [
        "eb070ea5-bd17-41f1-ad68-5851f6e71774"
    ],
    "MRMaps PPE": [
        "96636591-1bce-4eef-b8f9-939c0713889f"
    ],
    "Azure Key Vault Managed HSM Key Governance Service": [
        "a1b76039-a76c-499f-a2dd-846b4cc32627"
    ],
    "Microsoft.EventHubs": [
        "80369ed6-5f11-4dd9-bef3-692475845e77"
    ],
    "EventGrid Data API": [
        "823c0a78-5de0-4445-a7f5-c2f42d7dc89b"
    ],
    "Azure Service Fabric Resource Provider": [
        "74cb6831-0dbb-4be1-8206-fd4df301cdc2"
    ],
    "Avs Fleet Rp": [
        "1a5e141d-70dd-4594-8442-9fc46fa48686"
    ],
    "Azure Graph": [
        "dbcbd02a-d7c4-42fb-8c27-b07e5118b848"
    ],
    "NetworkTrafficAnalyticsService": [
        "1e3e4475-288f-4018-a376-df66fd7fac5f"
    ],
    "lab4-runcommand": [
        "fa7f2624-58db-4ea4-80ae-47578d56bd3a",
        "7d7e3c9b-8c4c-4a27-bcb7-adac7075942c"
    ],
    "Event Hub MSI App": [
        "6201d19e-14fb-4472-a2d6-5634a5c97568"
    ],
    "Marketplace Api": [
        "f738ef14-47dc-4564-b53b-45069484ccc7"
    ],
    "My Apps": [
        "2793995e-0a7d-40d7-bd35-6968ba142197"
    ],
    "Azure Machine Learning": [
        "0736f41a-0425-4b46-bdb5-1563eff02385"
    ],
    "Azure SQL Virtual Network to Network Resource Provider": [
        "76cd24bf-a9fc-4344-b1dc-908275de6d6d"
    ],
    "Azure RBAC Data Plane": [
        "5861f7fb-5582-4c1a-83c0-fc5ffdb531a6"
    ],
    "Microsoft Defender for Cloud Servers Scanner Resource Provider": [
        "0c7668b5-3260-4ad0-9f53-34ed54fa19b2"
    ],
    "Azure Healthcare APIs Resource Provider": [
        "894b1496-c6e0-4001-b69c-81b327564ca4"
    ],
    "CosmosDBMongoClusterPrivateEndpoint": [
        "e95a6071-4f90-4971-84e2-492d9323345b"
    ],
    "CCM TAGS": [
        "997dc448-eeab-4c93-8811-6b2c80196a16"
    ],
    "lab-management": [
        "250bf25e-74d4-4cec-8b0a-59801982e94b"
    ],
    "Microsoft Azure Container Apps - Data Plane": [
        "3734c1a4-2bed-4998-a37a-ff1a9e7bf019"
    ],
    "Bot Framework Composer": [
        "ce48853e-0605-4f77-8746-d70ac63cc6bc"
    ],
    "Windows Cloud Login": [
        "270efc09-cd0d-444b-a71f-39af4910ec45"
    ],
    "Azure MFA StrongAuthenticationService": [
        "b5a60e17-278b-4c92-a4e2-b9262e66bb28"
    ],
    "MRMapsProd": [
        "af7c72b5-1a61-4bf3-958b-4e51e1ddfbe8"
    ],
    "Azure Database for PostgreSQL Marlin": [
        "5ed8fe41-c1bc-4c06-a531-d91e1f1c2fac"
    ],
    "Monitoring Account API": [
        "be14bf7e-8ab4-49b0-9dc6-a0eddd6fa73e"
    ],
    "f69ef6de-app-service-lab-2-start-point": [
        "b3fb589f-929e-4a19-a850-3f88c8f9b73f"
    ],
    "asmcontainerimagescanner": [
        "918d0db8-4a38-4938-93c1-9313bdfe0272"
    ],
    "Azure Key Vault Managed HSM": [
        "589d5083-6f11-4d30-a62a-a4b316a14abf"
    ],
    "entra-id-lab-1-app-94a5f990": [
        "e7986cca-6fbb-43e2-842f-0a7bd0eff2c3"
    ],
    "Microsoft Commerce Accounts Service": [
        "bf9fc203-c1ff-4fd4-878b-323642e462ec"
    ],
    "Azure Cost Management Scheduled Actions": [
        "6b3368c6-61d2-4a72-854c-42d1c4e71fed"
    ],
    "AADReporting": [
        "1b912ec3-a9dd-4c4d-a53e-76aa7adb28d7"
    ],
    "Azure Machine Learning Services Asset Notification": [
        "b8cf62f3-7cc7-4e32-ab3a-41370ef0cfcf"
    ],
    "Azure Data Explorer": [
        "2746ea77-4702-4b45-80ca-3c97e680e8b7"
    ],
    "Azure OSSRDBMS Database": [
        "123cd850-d9df-40bd-94d5-c9f07b7fa203"
    ],
    "PowerPlatformAdminCenter": [
        "065d9450-1e87-434e-ac2f-69af271549ed"
    ],
    "CCM_Pricing_PROD": [
        "91a53dc4-b25b-482c-8e83-8d7ac7065b17"
    ],
    "Azure Managed HSM RP": [
        "1341df96-0b28-43da-ba24-7a6ce39be816"
    ],
    "Finance Copilot": [
        "8c1a9936-578e-4d13-9bd9-9afe53ef7de8"
    ],
    "Dynamics365Assistant": [
        "d024ca46-2708-4d20-903e-b18b7e1d95dc"
    ],
    "d365-dani-exceladdinprod": [
        "7c4f9118-450a-4e75-b96b-df2d0cac4c0d"
    ],
    "MicrosoftServiceCopilot-Prod": [
        "61ccfc51-60d1-470a-9dca-f78fcf640d23"
    ],
    "EHRTeleHealth": [
        "e97edbaf-39b2-4546-ba61-0a24e1bef890"
    ],
    "Mix Tools API": [
        "8463278f-7a65-4b3d-903c-5e66a2ad1164"
    ],
    "Prod M365FLWPService Prod": [
        "325e8307-defd-47df-aeff-15152ea6e5bf"
    ],
    "sophia.api.microsoft.com": [
        "d0af0b2c-272b-4820-80ce-af3cc751950f"
    ],
    "Sophia Platform Service API": [
        "d8fa9ca8-15de-4a33-b719-9c944b9b2e3e"
    ],
    "Prod M365FLWPService FirstRelease": [
        "9e6d7425-da52-4c9d-a3bf-48ce4670f9ef"
    ],
    "WPSTrialSignUpService_Prod": [
        "ebf6b2b7-c635-4217-b6b7-21de4ac65764"
    ],
    "Biz Apps Demo Hub Prod": [
        "46e9667d-34e6-43d8-a494-6759b3ae6a5e"
    ],
    "make.test.powerapps.com": [
        "60f38cf4-a0bf-4fdf-b0b5-14d3131bc031"
    ],
    "Power Platform Admin Center Client Test": [
        "c84a0f23-a0f8-4e8e-918b-57db620d110a"
    ],
    "Viva Goals Integrations": [
        "bee5ee7b-22c7-4e94-9b8b-031319e230a3"
    ],
    "Teams Approvals": [
        "3e050dd7-7815-46a0-8263-b73168a42c10"
    ],
    "Customer Experience Platform FRE TIP Non-Prod": [
        "f10573e9-a3c7-41b4-b203-4b1baed8fc8c"
    ],
    "Cloud for Nonprofit Installer": [
        "a0fe4328-8965-437b-a350-cf71409d002f"
    ],
    "Customer Experience Platform FRE PROD": [
        "6f459c5d-d670-409b-83a6-68b040f4cb78"
    ],
    "Azure API Management Portal extension": [
        "73a510c3-9946-46dd-b5ae-a8f0ae68fd04"
    ],
    "make.gov.powerpages.microsoft.us": [
        "929cb005-cba1-40c4-a962-ef441029cb6c"
    ],
    "SuplariDev": [
        "38ec0b21-8bde-4473-950b-819ceb3ed233"
    ],
    "Teams Work Report": [
        "ea62c1c6-550b-4238-8ea7-c55a85d86be8"
    ],
    "D365SalesProductivityProvisioning": [
        "4787c7ff-7cea-43db-8d0d-919f15c6354b"
    ],
    "make.test.powerpages.microsoft.com": [
        "f9a5ac11-cab3-45f0-9d0f-83463ba2e34c"
    ],
    "make.powerpages.microsoft.com": [
        "75eb2b80-011a-4693-9a47-7971c853603c"
    ],
    "Dynamics 365 collaboration with Microsoft Teams": [
        "a8adde6c-aeb4-4fd6-9d8f-c2dfdecac60a"
    ],
    "Power Cards": [
        "2f7b4d11-d621-4079-9798-27f548d681f1"
    ],
    "TrustedPublishersProxyService": [
        "2b61b865-d0bd-4c60-9efa-6fa934eefaac"
    ],
    "Unify Portal Prod": [
        "9f4bb91b-347a-47ab-aba4-06db0dcb89e3"
    ],
    "BAGSolutionsInstaller": [
        "de490f5e-b798-48d8-ae3b-c220d7494cef"
    ],
    "PowerVirtualAgentsUSGovGCC": [
        "9315aedd-209b-43b3-b149-2abff6a95d59"
    ],
    "BingTest": [
        "ef47e344-4bff-4e28-87da-6551a21ffbe0"
    ],
    "Power Apps Portals - Development": [
        "09be0be4-1874-4f49-bc5c-78e6fc2a8065"
    ],
    "Business Central to Common Data Service": [
        "88c57617-94ff-4043-a396-8a85a8d38922"
    ],
    "BAGSolutionsInstallerTest": [
        "8ad75a3e-ae97-457c-baab-65bd5c95389f"
    ],
    "RSOProvisioningCustomerDashboard": [
        "2f6713e6-1e21-4a83-91b4-5bf9a2378f81"
    ],
    "Dynamics CRM TIP SRS": [
        "257fc75b-c7b8-434b-a467-fcfc16cb7ab6"
    ],
    "Dynamics 365 Human Resources LinkedIn Adapter App": [
        "3a225c96-d62a-44ce-b3ec-bd4e8e9befef"
    ],
    "MicrosoftFlowGCCHigh": [
        "470d0752-cb06-49b2-ac83-5023fc23adae"
    ],
    "MicrosoftFlowDoD": [
        "7abdc2e3-67d5-4ccf-8138-e133192788e3"
    ],
    "MicrosoftFlowGCC": [
        "50351660-e7b1-4621-8bc8-8503296a5535"
    ],
    "Dynamics365AICustomerInsights": [
        "0bfc4568-a4ba-4c58-bd3e-5d3e76bd7fff"
    ],
    "Power Query Online GCC-L5": [
        "8c8fbf21-0ef3-4f60-81cf-0df811ff5d16"
    ],
    "MicrosoftFormsProTest": [
        "19dd5b37-d116-48cb-90d2-4aa56696cba1"
    ],
    "MicrosoftUnifiedCustomerIntelligence": [
        "38c77d00-5fcb-4cce-9d93-af4738258e3c"
    ],
    "PowerApps Web Player Service - play.apps.appsplatform.us": [
        "adc59501-b8c1-453a-a88b-9f4b244c1631"
    ],
    "PowerApps Web Player Service - high.apps.powerapps.us": [
        "dc426ec9-396a-46fd-8445-564554907e34"
    ],
    "PowerApps Web Player Service - apps.gov.powerapp.us": [
        "282c9137-f94e-4287-8223-9b60f2974e5c"
    ],
    "apps.powerapps.com": [
        "9362bc14-3e81-4ef9-8b77-f1c40afe68e0"
    ],
    "Power Query Online GCC-L4": [
        "ef947699-9b52-4b31-9a37-ef325c6ffc47"
    ],
    "Azure API Hub - GCC-Med": [
        "d93420f9-abc8-46b7-b7fc-30ec1f007ee2"
    ],
    "OmnichannelCRMClient": [
        "d9ce8cfa-8bd8-4ff1-b39b-5e5dd5742935"
    ],
    "DYN365_CS_MESSAGING": [
        "3957683c-3a48-4a6c-8706-a6e2d6883b02"
    ],
    "PowerApps - play.apps.appsplatform.us": [
        "44a34657-125d-4be1-b08d-87a07b336d24"
    ],
    "PowerApps - apps.high.powerapps.us": [
        "b145fb8f-d278-464f-8de1-894b596ecbde"
    ],
    "PowerApps - apps.gov.powerapps.us": [
        "a81833f1-fd18-490b-8598-60cd7b6b0382"
    ],
    "Aria": [
        "cd34d57a-a3ef-48b1-b84b-9686f0f7c099"
    ],
    "make.mil.powerapps.us": [
        "fac5b0fe-9b16-4ae3-b20b-324ec3f033d3"
    ],
    "make.high.powerapps.us": [
        "5d21c8e8-6d68-4b62-a3a5-bc1900513fad"
    ],
    "make.gov.powerapps.us": [
        "feb2c8aa-4f70-4881-abec-521141627b04"
    ],
    "ProcessSimpleGCC": [
        "38a893b6-d74c-4786-8fe7-bc3b4318e881"
    ],
    "CrmSalesInsightsTIP": [
        "b80a77b1-a78c-4655-9283-e40bbc285af0"
    ],
    "ccibotsprod": [
        "96ff4394-9197-43aa-b393-6a41652e21f8"
    ],
    "CCIBot": [
        "a522f059-bb65-47c0-8934-7db6e5286414"
    ],
    "Dynamics 365 for Marketing": [
        "5a24b264-c8f3-474d-92f6-a998cca942c1"
    ],
    "make.powerapps.com": [
        "a8f7a65c-f5ba-4859-b2d6-df772c264e9d"
    ],
    "DYN365AISERVICEINSIGHTS": [
        "60d240cc-7621-469e-80f1-584c53e9cafa"
    ],
    "BizQA for CDS": [
        "aeb01831-b358-4750-92ce-722e4f3ea7e8"
    ],
    "Azure AD Identity Governance - Dynamics 365 Management": [
        "c495cfdc-814f-46a1-89f0-657921c9fbe0"
    ],
    "Power Platform API": [
        "8578e004-a5c6-46e7-913e-12f58912df43"
    ],
    "Portfolios": [
        "f53895d3-095d-408f-8e93-8f94b391404e"
    ],
    "Power BI Data Refresh": [
        "b52893c8-bc2e-47fc-918b-77022b299bbc",
        "34cc6120-8c17-428c-b5aa-bede141fb74a"
    ],
    "Microsoft Business Office Add-in": [
        "2bc50526-cdc3-4e36-a970-c284c34cbd6e"
    ],
    "Microsoft Dynamics CRM App for Outlook": [
        "60216f25-dbae-452b-83ae-6224158ce95e"
    ],
    "Microsoft Power BI Government Community Cloud": [
        "fc4979e5-0aa5-429f-b13a-5d1365be5566"
    ],
    "Dynamics RCS Workload": [
        "091c98b0-a1c9-4b02-b62c-7753395ccabe"
    ],
    "Dynamics 365 Sales": [
        "59d7fccf-1f97-4a79-bb78-e722112f9862"
    ],
    "DeflectionTest": [
        "600def3d-4cdb-465f-9dad-dce96b255d6a"
    ],
    "CDSUserManagementNonProd": [
        "db966cd2-032b-4f21-b7c2-eadd3d68c2f2"
    ],
    "DeflectionPreProd": [
        "5443ef98-eb7c-4354-8367-f35dffe3cba7"
    ],
    "PowerAppsCustomerManagementPlaneBackend": [
        "585738fa-4b8c-4f90-b926-7eab8c498c69"
    ],
    "AppDeploymentOrchestration": [
        "886d9650-b672-4531-b16f-4617b5492d2f"
    ],
    "PowerAutomate-ProcessMining": [
        "dad3c6de-ed58-42ef-989f-9c0303aaeedc"
    ],
    "RelevanceSearch": [
        "f034940d-60b7-4587-afc9-ac1786ad7419"
    ],
    "CCaaSCRMClient": [
        "edfdd43b-26b5-498b-b89f-515ddf78dcc2"
    ],
    "PowerAutomate-ProcessMining-PPE": [
        "c4c008ec-e9c5-455c-b7e3-92c49982bc84"
    ],
    "PowerAutomate-ProcessMining-DEV": [
        "630e0ac2-6aa6-41bd-b950-5ade41828d3a"
    ],
    "PowerAutomate-ProcessMining-TEST": [
        "e1255f48-529f-4573-8ad2-8b13d784cd1c"
    ],
    "Flow-CDSNativeConnectorTIP2US": [
        "de8e0d25-0c9e-4230-87d6-cf379be2f1bd"
    ],
    "PowerAppsDataPlaneBackend": [
        "dac3dc4c-8be0-4972-8c97-e0a8500927f3"
    ],
    "DynamicsInstallerTest": [
        "079013fb-85d0-4d99-87d0-aeca060231e3"
    ],
    "JobsServicePreProd": [
        "fa69122a-0a5e-41f1-beed-ca317370fb56"
    ],
    "Omnichannel": [
        "c9b24c1a-09c1-4726-a288-709c86a12a9b"
    ],
    "AIBuilder_StructuredML_PreProd_CDS": [
        "0527d918-8aec-4c44-9f4e-86cc8b88d87b"
    ],
    "PowerPlatformEnvironmentManagement": [
        "a7d42dcf-5f3b-41b0-8ad5-e7c5808c617a"
    ],
    "TPSProxyServiceTST": [
        "de9fe347-3128-4a28-9b19-cd4ecca1f526"
    ],
    "Flow-RP": [
        "bdb3d4c5-dc11-426e-8f04-2621dbcce738"
    ],
    "CatalogServiceTest": [
        "7a7f0ba2-519f-49eb-9b86-1a967ba231f3"
    ],
    "InsightsAppsPlatform": [
        "7255edad-9269-44d0-b153-92ceffbf86fa"
    ],
    "Finance and Operations Runtime Integration User - TST Geo": [
        "71684101-1068-40b0-a0da-062710e1040d"
    ],
    "BAP CDS Application": [
        "978b42f5-e03a-4695-b8df-454959d032c8"
    ],
    "AppDeploymentOrchestration-Preprod": [
        "ce384d7c-6755-471d-91aa-1b48cc519c49"
    ],
    "Relevance Search Service": [
        "1884bdbf-452a-4a11-9c76-afdbdb1b3768"
    ],
    "Common Data Service User Management": [
        "c92229fa-e4e7-47fc-81a8-01386459c021"
    ],
    "PowerApps CDS Service": [
        "27f13ec4-0f4e-4840-b547-1a0181666256"
    ],
    "Product Insights - CDS to Azure data lake - app": [
        "ffa7d2fe-fc04-4599-9f6d-7ca06dd0c4fd"
    ],
    "GlobalDiscoService2": [
        "97d27433-255e-498c-a280-0cbc9aee407e"
    ],
    "ApolloNonProdFirstParty": [
        "265378aa-7259-4b82-af51-0c97c6cbc0ca"
    ],
    "Common Data Service Managed Data Lake Service": [
        "546068c3-99b1-4890-8e93-c8aeadcfe56a"
    ],
    "Common Data Service Global Discovery Service": [
        "6eb29b24-9d89-4f26-bf2f-9a84ed2499b8"
    ],
    "MicrosoftCrmDataSync@microsoft.com": [
        "7a575ec8-8d12-42eb-9edc-b93f3aa92c48"
    ],
    "Flow Xrm System User": [
        "fbc61429-7762-4b4a-8f9d-c728a1a5e792"
    ],
    "ApolloProdFirstParty": [
        "8c04f0eb-27fc-44cc-9e48-914b9202890a"
    ],
    "Dynamics 365 CCA Data analytics Prod - CDS to Azure data lake": [
        "87684a6d-f115-436c-a231-6a4d08eb01a6"
    ],
    "Microsoft Dynamics Jobs Service": [
        "e548fb5c-c385-41a6-a31d-6dbc2f0ca8a3"
    ],
    "Office365 Shell WCSS-Server": [
        "5f09333a-842c-47da-a157-57da27fcbca5"
    ],
    "Managed Meeting Rooms": [
        "eb20f3e3-3dce-4d2c-b721-ebb8d4414067"
    ],
    "Microsoft Account Controls V2": [
        "7eadcef8-456d-4611-9480-4fff72b8b9e2"
    ],
    "Microsoft 365 App Catalog Services": [
        "e8be65d6-d430-4289-a665-51bf2a194bda"
    ],
    "OfficeServicesManager": [
        "9e4a5442-a5c9-4f6f-b03f-5b9fcaaf24b1"
    ],
    "Intune DeviceDirectory ConfidentialClient": [
        "7e313d81-57dd-4bdd-906e-337963583de3"
    ],
    "Configuration Manager Microservice": [
        "557c67cf-c916-4293-8373-d584996f60ae"
    ],
    "My Staff": [
        "ba9ff945-a723-4ab5-a977-bd8c9044fe61"
    ],
    "ZTNA Network Access Control Plane": [
        "9d4afbbc-06a4-49e0-8005-4e5afd1d4fec"
    ],
    "M365DataAtRestEncryption": [
        "c066d759-24ae-40e7-a56f-027002b5d3e4"
    ],
    "MSAI Substrate Meeting Intelligence": [
        "038187f5-ca69-4382-8c0b-8d87708d099f"
    ],
    "Azure Communication Services": [
        "1fd5118e-2576-4263-8130-9503064c837a"
    ],
    "Teams Admin Monitoring Alerting Platform": [
        "f2537abf-644e-4a0d-9f7b-c91c45c643db"
    ],
    "SPAuthEvent": [
        "3340b944-b12e-47d0-b46b-35f08ec1d8ee"
    ],
    "Power Platform Data Analytics": [
        "7dcff627-a295-4553-9229-b1f3513f82a8"
    ],
    "EDU Assignments": [
        "8f348934-64be-4bb2-bc16-c54c96789f43"
    ],
    "Conference Auto Attendant": [
        "207a6836-d031-4764-a9d8-c1193f455f21"
    ],
    "Lifecycle Workflows": [
        "ce79fdc4-cd1d-4ea5-8139-e74d7dbe0bb7"
    ],
    "Microsoft Partner": [
        "4990cffe-04e8-4e8b-808a-1175604b879f"
    ],
    "Cloud Hybrid Search": [
        "feff8b5b-97f3-4374-a16a-1911ae9e15e9"
    ],
    "Azure Edge Zones storage backend": [
        "05d97c70-cb7c-4e66-8138-d5ca7c59d206"
    ],
    "Euclid": [
        "2ca80e7c-4ad1-444f-88f5-58f92b71b7b0"
    ],
    "AzNS EventHub Action": [
        "58ef1dbd-684c-47d6-8ffc-61ea7a197b95"
    ],
    "Azure DevOps": [
        "499b84ac-1321-427f-aa17-267ca6975798"
    ],
    "Microsoft Intune SCCM Connector": [
        "63e61dc2-f593-4a6f-92b9-92e4d2c03d4f"
    ],
    "MIP Exchange Solutions": [
        "a150d169-7d37-47dd-9b20-156207b7b02f"
    ],
    "Microsoft Defender for Cloud Apps MIP Server": [
        "0858ddce-8fca-4479-929b-4504feeed95e"
    ],
    "M365 Pillar Diagnostics Service": [
        "58ea322b-940c-4d98-affb-345ec4cccb92"
    ],
    "Office 365 Mover": [
        "d62121f3-e023-4972-b6b0-794190c0fd98"
    ],
    "Microsoft.SecurityDevOps Resource Provider": [
        "7bf610f7-ecaf-43a2-9dbc-33b14314d6fe"
    ],
    "Office MRO Device Manager Service": [
        "ebe0c285-db95-403f-a1a3-a793bd6d7767"
    ],
    "Microsoft Device Management Checkin": [
        "ca0a114d-6fbc-46b3-90fa-2ec954794ddb"
    ],
    "Azure Portal RP": [
        "5b3b270a-b9ad-46e7-9bbb-a866897c4dc7"
    ],
    "SharePoint Home Notifier": [
        "4e445925-163e-42ca-b801-9073bfa46d17"
    ],
    "SharePoint Framework Azure AD Helper": [
        "e29b5c86-b9ab-4a86-9a20-d10842007599"
    ],
    "M365CommunicationCompliance": [
        "b8d56525-1fd0-4121-a640-e0ede64f74b5"
    ],
    "Microsoft Device Management Enrollment": [
        "709110f7-976e-4284-8851-b537e9bcb187"
    ],
    "Messaging Bot API Application": [
        "5a807f24-c9de-44ee-a3a7-329e88a00ffc"
    ],
    "Viva Learning": [
        "2c9e12e5-a56c-4ba1-b768-7a141586c6fe"
    ],
    "Microsoft Insider Risk Management": [
        "1fe0d6b3-81f0-4cf5-9dfd-fbb297d7848c"
    ],
    "Microsoft Intune IW Service": [
        "b8066b99-6e67-41be-abfa-75db1a2c8809"
    ],
    "M365 App Management Service": [
        "0517ffae-825d-4aff-999e-3f2336b8a20a"
    ],
    "MsgDataMgmt": [
        "61a63147-3824-45f5-a186-ace3f4c9daeb"
    ],
    "Microsoft Teams Admin Portal Service": [
        "2ddfbe71-ed12-4123-b99b-d5fc8a062a79"
    ],
    "teams contacts griffin processor": [
        "e08ab642-962a-4175-913c-165f557d799a"
    ],
    "Prod-AzureSustainability": [
        "d05a94d3-4ebf-4d16-a4b5-c5157fe79490"
    ],
    "Office Store": [
        "c606301c-f764-4e6b-aa45-7caaaea93c9a"
    ],
    "Internet resources with Global Secure Access": [
        "5dc48733-b5df-475c-a49b-fa307ef00853"
    ],
    "Dual-write": [
        "6f7d0213-62b1-43a8-b7f4-ff2bb8b7b452"
    ],
    "Defender Experts for XDR": [
        "9ee7b58d-f9db-45bc-ad7b-c2b97bbc3337"
    ],
    "Microsoft Graph Connectors Core": [
        "f8f7a2aa-e116-4ba6-8aea-ca162cfa310d"
    ],
    "DirectoryLookupService": [
        "9cd0f7df-8b1a-4e54-8c0c-0ef3a51116f6"
    ],
    "Verifiable Credentials Service Request": [
        "3db474b9-6a0c-4840-96ac-1fceb342124f"
    ],
    "Microsoft Intune AAD BitLocker Recovery Key Integration": [
        "ccf4d8df-75ce-4107-8ea5-7afd618d4d8a"
    ],
    "Teams CMD Services and Data": [
        "00edd498-7c0c-4e68-859c-5a55d518c9c0"
    ],
    "Microsoft Device Management EMM API": [
        "8ae6a0b1-a07f-4ec9-927a-afb8d39da81c"
    ],
    "Verifiable Credentials Service Admin": [
        "6a8b4b39-c021-437c-b060-5a14a3fd65f3"
    ],
    "Microsoft Azure": [
        "15689b28-1333-4213-bb64-38407dde8a5e"
    ],
    "Teams Policy Notification Processor Service": [
        "61f9e166-f678-4342-bfd3-b49781ce7a0a"
    ],
    "Office 365 Enterprise Insights": [
        "f9d02341-e7aa-456d-926d-4a0ca599fbee"
    ],
    "M365 Pillar Diagnostics Service API": [
        "8bea2130-23a1-4c09-acfb-637a9fb7c157"
    ],
    "Microsoft Windows AutoPilot Service API": [
        "cbfda01c-c883-45aa-aedc-e7a484615620"
    ],
    "IC3 Gateway TestClone": [
        "55bdc56c-2b15-4538-aa37-d0c008c8c430"
    ],
    "Azure Edge Zones storage": [
        "1609d3a1-0db2-4818-b854-fe1614f0718a"
    ],
    "AD Hybrid Health": [
        "6ea8091b-151d-447a-9013-6845b83ba57b"
    ],
    "Substrate-FileWatcher": [
        "fbb0ac1a-82dd-478b-a0e5-0b2b98ef38fe"
    ],
    "ChatMigrationService1P": [
        "3af5adde-460d-4bc1-ada0-fc648af8fefb"
    ],
    "RPA - Machine Management Relay Service": [
        "aad3e70f-aa64-4fde-82aa-c9d97a4501dc"
    ],
    "CAP Neptune Prod CM Prod": [
        "ab158d9a-0b5c-4cc3-bb2b-f6646581e4e4"
    ],
    "SharePoint Online Web Client Extensibility Isolated": [
        "3bc2296e-aa22-4ed2-9e1e-946d05afa6a2"
    ],
    "SubstrateActionsService": [
        "06dd8193-75af-46d0-84bb-9b9bcaa89e8b"
    ],
    "PROD Microsoft Defender For Cloud Athena": [
        "e807d0e2-91da-40d6-8cee-e33c91a0b051"
    ],
    "MSATenantRestrictions": [
        "1a4b5304-a0fd-4017-8a3d-466fc083b73e"
    ],
    "Microsoft Teams ATP Service": [
        "0fa37baf-7afc-4baf-ab2d-d5bb891d53ef"
    ],
    "Microsoft Defender for Cloud Apps - APIs": [
        "972bb84a-1d27-4bd3-8306-6b8e57679e8c"
    ],
    "CIWebService": [
        "e1335bb1-2aec-4f92-8140-0e6e61ae77e5"
    ],
    "Verifiable Credentials Service": [
        "bb2a64ee-5d29-4b07-a491-25806dc854d3"
    ],
    "MicrosoftEndpointDLP": [
        "c98e5057-edde-4666-b301-186a01b4dc58"
    ],
    "Microsoft Teams Intelligent Workspaces Interactions Service": [
        "0eb4bf93-cb63-4fe1-9d7d-70632ccf3082"
    ],
    "Office365 Shell SS-Server": [
        "e8bdeda8-b4a3-4eed-b307-5e2456238a77"
    ],
    "policy enforcer": [
        "fbb123dc-fe45-41fe-ad9f-e42ab0769328"
    ],
    "Exchange Rbac": [
        "789e8929-0390-42a2-8934-0f9dafb8ec89"
    ],
    "Deprecated - CAS API Security RP Staging": [
        "19b21e10-1304-498b-92d4-4290e94999fa"
    ],
    "Intune Grouping and Targeting Client Prod": [
        "fd14a986-6fe4-409a-883e-cdec1009cd54"
    ],
    "Audit GraphAPI Application": [
        "4bfd5d66-9285-44a1-bb14-14953e8cdf5e"
    ],
    "SQL Copilot PPE": [
        "0fc12b9a-5463-4b87-8f10-765fecb39990"
    ],
    "Power Platform Policy Services CM - PROD": [
        "342f61e2-a864-4c50-87de-86abc6790d49"
    ],
    "All private resources with Global Secure Access": [
        "e92b9b37-1b47-4c01-9fbc-91d84450870e"
    ],
    "Microsoft Workplace Search Service": [
        "f3a218b7-5c8f-460b-93af-56b072788c15"
    ],
    "Power Platform Global Discovery Service": [
        "93bd1aa4-c66b-4587-838c-ffc3174b5f13"
    ],
    "IC3 Gateway": [
        "39aaf054-81a5-48c7-a4f8-0293012095b9"
    ],
    "Branch Connect Web Service": [
        "57084ef3-d413-4087-a28f-f6f3b1ad7786"
    ],
    "Conferencing Virtual Assistant": [
        "9e133cac-5238-4d1e-aaa0-d8ff4ca23f4e"
    ],
    "Office Hive": [
        "166f1b03-5b19-416f-a94b-1d7aa2d247dc"
    ],
    "Marketplace Reviews": [
        "a4c1cdb3-88ab-4d13-bc99-1c46106f0727"
    ],
    "Microsoft Teams Targeting Application": [
        "8e14e873-35ba-4720-b787-0bed94370b17"
    ],
    "Microsoft Visio Data Visualizer": [
        "00695ed2-3202-4156-8da1-69f60065e255"
    ],
    "Power Platform Dataflows Common Data Service Client": [
        "99335b6b-7d9d-4216-8dee-883b26e0ccf7"
    ],
    "Intune DiagnosticService": [
        "7f0d9978-eb2a-4974-88bd-f22a3006fe17"
    ],
    "Substrate Conversation Intelligence Service": [
        "aa813f0e-407a-459d-93af-805f2bf10f33"
    ],
    "Microsoft Graph Bicep Extension": [
        "a1bfe852-bf44-4da0-a9c1-37af2d5e6df9"
    ],
    "Deprecated - CAS API Security RP Dev": [
        "cb250467-fc8f-4c42-8349-9ff9e9a17b02"
    ],
    "Microsoft O365 Scuba": [
        "7ae5462d-d9d1-42f6-93ca-198d7b0ca997"
    ],
    "Microsoft apps with Global Secure Access": [
        "c08f52c9-8f03-4558-a0ea-9a4c878cf343"
    ],
    "M365 Label Analytics": [
        "75513c96-801d-4559-830a-6754de13dd19"
    ],
    "Microsoft.Azure.ActiveDirectoryIUX": [
        "bb8f18b0-9c38-48c9-a847-e1ef3af0602d"
    ],
    "Customer Experience Platform PROD": [
        "2220bbc4-4518-4fef-aac6-c6f32e9f9fd1"
    ],
    "Office Online OWLNest": [
        "d7d7af51-cdcd-4a4c-9467-86e7dc5d2b90"
    ],
    "Office Online Search SSO": [
        "5a4eed13-c4c4-4b4c-9506-334ab200bf31"
    ],
    "My Signins": [
        "19db86c3-b2b9-44cc-b339-36da233a3be2"
    ],
    "Office Online Print SSO": [
        "3ce44149-e365-40e4-9bb4-8c0ecb710fe6"
    ],
    "Microsoft Community v2": [
        "a81d90ac-aa75-4cf8-b14c-58bf348528fe"
    ],
    "Message Recall": [
        "0e90d0b8-039a-4936-a6f4-d25dd510be5d"
    ],
    "MM_Reactions_PME_PROD": [
        "e8e8fc40-94d5-4ed6-89f2-9e5ec6c1e11e"
    ],
    "Office 365": [
        "72782ba9-4490-4f03-8d82-562370ea3566"
    ],
    "Microsoft Entra AD Synchronization Service": [
        "6bf85cfa-ac8a-4be5-b5de-425a0d0dc016"
    ],
    "Olympus": [
        "bb893c22-978d-4cd4-a6f7-bb6cc0d6e6ce"
    ],
    "Azure Region Move Orchestrator Application": [
        "51df634f-ddb4-4901-8a2d-52f6393a796b"
    ],
    "Azure Reserved Instance Application": [
        "4d0ad6c7-f6c3-46d8-ab0d-1406d5e6c86b"
    ],
    "AzureUpdateCenter": [
        "8c420feb-03df-47cc-8a05-55df0cf3064b"
    ],
    "BenefitsFD": [
        "09a984f4-014c-43de-ae0c-7ec73dc053d3"
    ],
    "Capacity": [
        "fbc197b7-9e9c-4f98-823f-93cb1cb554e6"
    ],
    "ConfidentialLedger": [
        "4353526e-1c33-4fcf-9e82-9683edf52848"
    ],
    "Intune oAuth Graph": [
        "0f6e3eff-886c-4f7a-a1d7-6f1f0177273b"
    ],
    "Microsoft Command Service": [
        "19686ca6-5324-4571-a231-77e026b0e06f"
    ],
    "Microsoft Azure Batch": [
        "ddbf3205-c6bd-46ae-8127-60eb93363864"
    ],
    "Microsoft 365 Ticketing": [
        "510a5356-1745-4855-93a5-113ea589fb26"
    ],
    "Microsoft Azure Authorization Private Link Provider": [
        "de926fbf-e23b-41f9-ae15-c943a9cfa630"
    ],
    "Microsoft DataMovement Metadata Service": [
        "1c827867-9069-4bde-8155-1a0267a3dea5"
    ],
    "Microsoft.Azure.DomainRegistration": [
        "ea2f600a-4980-45b7-89bf-d34da487bda1"
    ],
    "Microsoft Project Babylon": [
        "73c2949e-da2d-457a-9607-fcc665198967"
    ],
    "Microsoft.Azure.GraphExplorer": [
        "0000000f-0000-0000-c000-000000000000"
    ],
    "Microsoft.Azure.GraphStore": [
        "00000010-0000-0000-c000-000000000000"
    ],
    "Microsoft.SupportTicketSubmission": [
        "595d87a1-277b-4c0a-aa7f-44f8a068eafc"
    ],
    "MTS": [
        "6682cfa5-2710-44c9-adb8-5ac9d76e394a"
    ],
    "Office Online Third Party Storage": [
        "c1f33bc0-bdb4-4248-ba9b-096807ddb43e"
    ],
    "MicrosoftOffAzureApp": [
        "728a93e3-065d-4678-93b1-3cc281223341"
    ],
    "MicrosoftMigrateProject": [
        "e3bfd6ac-eace-4438-9dc1-eed439e738de"
    ],
    "On-Premises Data Gateway Connector": [
        "d52485ee-4609-4f6b-b3a3-68b6f841fa23"
    ],
    "Skype Business Voice Fraud Detection and Prevention": [
        "b73f62d0-210b-4396-a4c5-ea50c4fab79b"
    ],
    "Outlook Service for Exchange": [
        "13d54852-ae25-4f0b-823a-b09eea89f431"
    ],
    "Outlook Service for OneDrive": [
        "2728b157-fe96-4203-a49f-cc31c93a2ba3"
    ],
    "SmartList Designer": [
        "c9d254a9-346a-4c00-95eb-950cb62a58f0"
    ],
    "Universal Store Entitlements Service": [
        "bf7b96b3-68e4-4fd9-b697-637f0f1e778c"
    ],
    "Weve": [
        "71a7c376-13e6-4100-968e-92ce98c5d3d2"
    ],
    "Micorsoft Azure AppInsightsExtension": [
        "95a5d94c-a1a0-40eb-ac6d-48c5bdee96d5"
    ],
    "Windows Notification Service": [
        "04436913-cf0d-4d2a-9cc6-2ffe7f1d3d1c"
    ],
    "Microsoft_Azure_Policy": [
        "c556d48a-da18-409b-817d-064fa2fcf2a0"
    ],
    "Microsoft_Azure_Resources": [
        "0fdc37af-a69e-49ea-8ee9-a1d69e7edb0c"
    ],
    "Kubernetes Runtime RP": [
        "087fca6e-4606-4d41-b3f6-5ebdf75b8b4c"
    ],
    "DevTest Labs Portal": [
        "a3bda2b7-dead-402f-8a9f-13b8ce878dc1"
    ],
    "Microsoft_Azure_CustomerHub": [
        "1d9f6aaf-ea7d-4193-a99f-ad27ad037e15"
    ],
    "Managed Labs Ibiza PROD": [
        "bad22d78-f2ba-40cb-9218-665a00dcab72"
    ],
    "Fidalgo Ibiza Public": [
        "4481e210-f747-4590-b65b-37aa6bd1056a"
    ],
    "Microsoft_Azure_SAPManagement": [
        "4f71e121-13fa-44c9-a463-dd0fb1c56f17"
    ],
    "Microsoft_Azure_WorkloadInsight": [
        "4a5c9d53-dc84-47d0-8a22-ea6502aeed62"
    ],
    "Microsoft_Azure_WorkloadMonitor": [
        "e6ce1a54-4f33-4fdc-a782-6c14e4095474"
    ],
    "Marketplace Transact Ext": [
        "4f18ed62-806c-4424-9576-71c53ea11f49"
    ],
    "Microsoft Azure Marketplace": [
        "0a2057a8-149c-40ca-859e-98de032535fb"
    ],
    "Microsoft_Azure_Compute": [
        "03ec703c-bc36-4494-b8ab-73e84692823a"
    ],
    "Microsoft_Azure_IotHub": [
        "102b3235-5b2f-432e-aee9-109e3afb15e1"
    ],
    "Liftr-Pure-Network": [
        "ddddf4be-ff49-4144-b6e9-a82ff1226c5f"
    ],
    "MicrosoftSecurityCopilotAzureExtensionApp": [
        "21fd57f2-6ca5-43b9-b502-5611ab3b3930"
    ],
    "Microsoft Azure DataLake portal extension": [
        "92ff45f0-dfb0-4078-804a-6cf3e52a3d8c"
    ],
    "Microsoft_Azure_Storage": [
        "691458b9-1327-4635-9f55-ed83a7f1b41c"
    ],
    "Microsoft_Azure_Kailani": [
        "e4d7e78b-c114-46b9-9880-29f5b1cf4a90"
    ],
    "Microsoft_Azure_Network": [
        "03e204c9-d1db-4685-895c-00603f8bfb98"
    ],
    "Azure Arc UX Client - Public Cloud": [
        "55850760-a3b5-4271-8dd2-3cd9c4d05869"
    ],
    "Microsoft_Azure_ServiceFabric": [
        "efdffe3a-aeb7-40c4-9490-e2d563152033"
    ],
    "Microsoft_Azure_FileStorage": [
        "ac212b6d-5417-46fc-a74a-bd8f1ccf3501"
    ],
    "Microsoft_Azure_DiskMgmt": [
        "5a287bbb-2eb6-45e4-b133-8030c415e7fb"
    ],
    "Microsoft_Azure_ContainerService": [
        "0c50de64-92f9-4ad5-bf88-1af4b40c3b8e"
    ],
    "Microsoft_Azure_CloudServices_Arm": [
        "187f8db2-105c-43ce-b6ba-5d4112236e10"
    ],
    "Microsoft_Entra_PM": [
        "7655d621-3c86-4a9a-92f8-47244f293b55"
    ],
    "Microsoft_AAD_RegisteredApps": [
        "18ed3507-a475-4ccb-b669-d66bc9f2a36e"
    ],
    "Microsoft_Entra_PM_Dashboard": [
        "657f475f-6af7-4958-a07d-84ce676716d9"
    ],
    "Microsoft_Azure_EdgeGateway": [
        "344280e9-601d-401c-b634-416276f48e3e"
    ],
    "Microsoft_AzureStackHCI_PortalExtension": [
        "e0497406-d33e-45d9-82be-371739e437a9"
    ],
    "Liftr-IN-FPA-PRT-AME": [
        "f4548917-4954-4f48-8185-cd902208436c"
    ],
    "Microsoft_Azure_PIMCommon": [
        "50aaa389-5a33-4f1a-91d7-2c45ecd8dac8"
    ],
    "Microsoft_Azure_ELMAdmin": [
        "0032593d-6a05-4847-8ca4-4b6220ed2a1e"
    ],
    "Microsoft_AAD_ERM": [
        "2a508b4a-9a5e-45ee-a60a-6380ede07f65"
    ],
    "ChangeManagementHub": [
        "9d15ec9c-4104-48aa-9688-c907238f257b"
    ],
    "M365 Compliance Assessment Toolkit": [
        "b312d4d5-a2c0-4480-b588-a5024677eb5c"
    ],
    "ComplianceCenterAAD": [
        "7c0d6b85-a577-4d00-8fcb-f583c0d8286c"
    ],
    "Microsoft_AAD_SubscriptionManagement": [
        "6fa49422-16be-406e-9980-36c88077cda3"
    ],
    "Microsoft Engage Hub": [
        "fe1b2b53-eb41-4515-a3b4-d62059faf520"
    ],
    "CreateUiDef graph access": [
        "57f352fe-8f23-4781-8bae-1bbde5e1d8fd"
    ],
    "VLCentral_Home": [
        "3094c60e-793a-4caf-8a58-0e2e78546847"
    ],
    "Azure Cognitive Search Portal Extension": [
        "477cd9f9-408b-42a1-a47d-30721817f25b"
    ],
    "Microsoft_OperationsManagementSuite_Workspace": [
        "6e00b31f-06d4-4c93-8b14-e08b568b4a04"
    ],
    "AFDX-Portal-1stPartyAAD-Prod": [
        "189fe8f3-4e48-4a4b-9459-c230524890e6"
    ],
    "Microsoft_Azure_WorkloadInsights": [
        "c5eb93c5-ea21-48c2-a137-4a7641c61bc8"
    ],
    "Microsoft_AAD_LifecycleManagement": [
        "7b32d65b-837b-4365-931e-3c87e8a860aa"
    ],
    "EASM PORTAL": [
        "6ba358df-b33d-4bfe-a7b7-fe139acebe7b"
    ],
    "Liftr-DT-FPA-PRT-AME": [
        "80ee910d-3412-4991-aa65-1380520e5ff9"
    ],
    "Liftr-LZ-FPA-PRT-AME": [
        "f3ffc46c-a723-4752-9bf5-899adb285bf7"
    ],
    "Liftr portal extension app for ms graph": [
        "26109b29-37da-419b-9fe3-c080749aac85"
    ],
    "CloudNativeTesting Portal": [
        "00daac17-a7ce-4990-a494-a7120e0b5c6c"
    ],
    "Liftr-AN-FPA-Portal-AME": [
        "701860c7-4ffa-4813-b18d-0c0af02faed7"
    ],
    "Data Center Portal": [
        "242f2be3-9ef4-4f7a-8df2-8ff24e10f697"
    ],
    "liftr-split-portal-fpa-prod": [
        "73b67c52-525b-4470-9c5c-1e02c60b8a05"
    ],
    "ZTNA UX Portal": [
        "ea8d014c-04e7-450c-a600-eaa309e42309"
    ],
    "Microsoft_Azure_Billing": [
        "631d36ba-ddbd-4e88-807a-b8cd54f9b390"
    ],
    "Microsoft_AAD_GTM": [
        "4ba4d253-8ed1-42a1-b919-37fad5e5f06e"
    ],
    "Microsoft.CodeSigning.PortalExt.PROD": [
        "42f00fc9-f5d0-4270-8ff8-d66b2b27d9c7"
    ],
    "Microsoft_Azure_AzConfig": [
        "1e2401ea-428f-4575-9bbf-b301f7e1eb67"
    ],
    "Microsoft_Azure_PinToGrafana": [
        "82afb2e3-126a-42ce-a39c-b2734e769a69"
    ],
    "Microsoft_Azure_Security_Insights": [
        "bda0771f-b6df-474a-b348-26a308db88aa"
    ],
    "AFOI-NC-PORTAL-EXTENSION-PME-PROD": [
        "670b3109-680a-4d63-b99e-b0510e4c0688"
    ],
    "Azure Service Linker Extension": [
        "a941dc67-8fed-413a-bd6c-78b97250b257"
    ],
    "Azure Portal Fx Copilot Web": [
        "5a6fd92b-8a2c-41d2-b3bb-98d35d258d9e"
    ],
    "Microsoft_AAD_UsersAndTenants": [
        "f9885e6e-6f74-46b3-b595-350157a27541"
    ],
    "Mission Enclave": [
        "851682fd-88ff-44cb-ac39-8a2624c539b1"
    ],
    "Microsoft Defender for APIs UI": [
        "61e987ea-ea8c-4843-903e-1b58e57b7ab1"
    ],
    "AzureDefenderForDataApp": [
        "b52fa633-d1c6-4449-98f2-cdab2456e94a"
    ],
    "Azure Managed HSM Portal Extension": [
        "89141436-bde0-4a2c-ad51-ebb3163e3e58"
    ],
    "Microsoft_Azure_Security": [
        "962225de-d127-40d7-ae7e-7beaa246ee3a"
    ],
    "CPIM Portal Extension Application": [
        "aced0c89-3b79-49ab-b2f1-27b67d3f0054"
    ],
    "Identity Protection UX": [
        "7f7ba5f2-edd7-4b6c-af4c-f48dfb5beec5"
    ],
    "Microsoft_Azure_FlowLog_FirstPartyApp": [
        "291524a3-5e57-4e82-a38d-62f56293190f"
    ],
    "Microsoft_Azure_ActivityLog": [
        "2c879423-ba8d-42b3-9fb4-a444905905c4"
    ],
    "Microsoft_Azure_Experimentation": [
        "a1b0286a-3c06-4ab0-8cdb-3ff8dbc09709"
    ],
    "Microsoft_Azure_Dashboard": [
        "cd39c5ca-1d6a-44a4-bf0d-8fbb623a6666"
    ],
    "Websites Extensions": [
        "f64071b9-a79b-4655-9dad-3b3535e00b84"
    ],
    "Microsoft Azure SQL": [
        "8f10c021-391a-4dfa-894c-cca96be320f7"
    ],
    "Azure Modeling and Simulation Workbench": [
        "5bd9995f-b6f8-4c7a-a024-e8c5eab9c85d"
    ],
    "Microsoft_AAD_Devices": [
        "c40dfea8-483f-469b-aafe-642149115b3a"
    ],
    "Microsoft_Azure_Monitoring": [
        "46ff7383-ea2d-47fe-92a0-e27d7dc2fee9"
    ],
    "Microsoft_Azure_CtsExtension": [
        "a634a778-2379-4632-92cd-6d66540ddca4"
    ],
    "Microsoft Intune multi-tenant management UX extension": [
        "3f1abb3f-12cc-42c3-ad06-5b608dc5fb67"
    ],
    "Microsoft Quantum Azure Portal": [
        "4f5d63ba-4a86-48e0-89b3-1df09c0dbb82"
    ],
    "Microsoft AzureCacheExtension": [
        "11519663-03b7-4dd3-a316-5580360da33f"
    ],
    "AzurePortal Console App": [
        "b677c290-cf4b-4a8e-a60e-91ba650a4abe"
    ],
    "DEC-AME-AppID-PROD": [
        "224445b2-0e0f-48d4-be8e-fc9b27f60f96"
    ],
    "Azure Managed Grafana": [
        "ce34e7e5-485f-4d76-964f-b3d2b16d1e4f"
    ],
    "Azure Certified for IoT Device Catalog": [
        "822c8694-ad95-4735-9c55-256f7db2f9b4"
    ],
    "Azure Digital Twins": [
        "0b07f429-9f4b-4714-9392-cc5e8e80c8b0"
    ],
    "Capri": [
        "5b0b1829-551e-44c8-ab85-e37f2437eb63"
    ],
    "Microsoft_AAD_DomainServices": [
        "721b7c62-eec0-4d88-9b77-5e7c15e210a8"
    ],
    "Azure Device Update": [
        "6ee392c4-d339-4083-b04d-6b7947c6cf78"
    ],
    "Microsoft_AAD_HybridAuthentication": [
        "8062e3ed-4248-451f-a2af-0404e0362a39"
    ],
    "Microsoft Azure Analysis Services": [
        "68282534-2e2f-45fa-a8ed-898bce6ba449"
    ],
    "Azure API Center": [
        "c3ca1a77-7a87-4dba-b8f8-eea115ae4573"
    ],
    "Microsoft Azure Batch Portal Extension": [
        "0fac0caa-efd0-46cc-a6df-945f8c5eae54"
    ],
    "Windows 365 Ibiza Extension": [
        "69cc3193-b6c4-4172-98e5-ed0f38ab3ff8"
    ],
    "Microsoft Azure AttestationExtension": [
        "b1d0e860-2368-4a20-97bb-067f0fb302d4"
    ],
    "Microsoft Azure Automation portal extension": [
        "fe8f0c38-d9f1-42cc-ad58-0080879a4b9b"
    ],
    "AzureCommunicationsGateway": [
        "8502a0ec-c76d-412f-836c-398018e2312b"
    ],
    "Azure Data Factory Ibiza Extension": [
        "e8caf904-b6ac-4b01-85f6-b0d8e15e58a6"
    ],
    "Microsoft_Azure_RecoveryServices": [
        "20a3058f-cd75-4115-8166-83f8c3767069"
    ],
    "Microsoft Azure Databricks portal extension": [
        "b675d171-daad-4ba1-813b-4792504ae6e2"
    ],
    "Microsoft_Azure_DataShare": [
        "a03453e2-fed9-4e6a-8566-f141028d83e6"
    ],
    "Azure_Digital_Twins": [
        "69cfcf0a-625d-409f-b381-8f036e2773b3"
    ],
    "Microsoft_Azure_DocumentDB": [
        "4f8d3fcc-c1ad-411c-8421-c7a41b65ff5f"
    ],
    "Microsoft_Azure_Education": [
        "01941e19-f441-4835-b4a0-546a1da6d99c"
    ],
    "Microsoft_Azure_EMA": [
        "553a8bc3-7740-43c1-bd40-3112510766f8"
    ],
    "Event Hub Portal App": [
        "dd34f6e5-71d9-4a89-95bb-75e237d6ae71"
    ],
    "Microsoft Graph Data Connect - Azure Portal": [
        "7ec03bdb-0e14-495d-9f6c-c0fd4bf2cff0"
    ],
    "ApplicationGatewayV1ToV2CloningPortalClient": [
        "b4c79f90-05ef-4edb-a980-de88f6952049"
    ],
    "Microsoft Azure KeyVault portal extension": [
        "3686488a-04fc-4d8a-b967-61f98ec41efe"
    ],
    "Microsoft_Azure_Kusto": [
        "08617521-6d76-4eb0-b336-a9efef0d8a68"
    ],
    "Microsoft.Azure.ManagedIdentities.UX": [
        "c56f381d-fc23-4d17-98a9-75fdd5a3a114"
    ],
    "Microsoft Azure MediaServices Portal Extension": [
        "e26464aa-f675-4313-a499-89e9db930949"
    ],
    "Microsoft_Azure_Migrate": [
        "22b20989-8944-48d7-9b61-9f5e8b5d6c8f"
    ],
    "Microsoft_Azure_Monitoring_Alerts": [
        "42aeded7-654f-4021-8573-a861f8c0eb60"
    ],
    "Azure Sphere API": [
        "7c209960-a417-423c-b2e3-9251907e63fe"
    ],
    "Microsoft_Azure_WVD": [
        "21ff6926-4d49-46ea-a34e-e9937fd65fea"
    ],
    "Microsoft_Azure_StackMigrate": [
        "1c8fc834-e4ea-42f6-8f09-8db8fde75446"
    ],
    "Microsoft_EMM_ModernWorkplace": [
        "e9c19b55-5325-4cf3-a268-e380bc74c907"
    ],
    "Modern Workplace Customer APIs": [
        "c9d36ed4-91b3-4c87-b8d7-68d92826c96c"
    ],
    "Microsoft Intune portal extension": [
        "5926fc8e-304e-4f59-8bed-58ca97cc39a4"
    ],
    "Configuration Manager portal extension": [
        "0673e721-d668-419d-b8c7-709bfd1e7928"
    ],
    "Microsoft Intune for Education portal extension": [
        "f52f5287-0be2-4052-83e8-e69620aa67cc"
    ],
    "AI Log Analytics UI": [
        "4c011fb8-5afd-4a16-9283-8bee6e25cb33"
    ],
    "ScanXManagement": [
        "c4fe64aa-7e1f-4995-bfb8-107e8ef9bbe3"
    ],
    "Microsoft_Print_Extension": [
        "90c17bc4-8398-44d4-9b47-89ed4ea32d25"
    ],
    "Azure Time Series Insights": [
        "120d688d-1518-4cf7-bd38-182f158850b6"
    ],
    "Windows 365": [
        "0af06dc6-e4b5-4f28-818e-e78e62d137a5"
    ],
    "MIP Exchange Solutions - SPO": [
        "192644fe-6aac-4786-8d93-775a056aa1de"
    ],
    "Virtual Visits App": [
        "2b479c68-8d9b-4e27-9d85-5d74803de734"
    ],
    "Microsoft Azure Authorization Resource Provider": [
        "1dcb1bc7-c721-498e-b2fa-bcddcea44171"
    ],
    "Atlas": [
        "d10de03d-5ba3-497a-90e6-7ff8c9736059"
    ],
    "Application Registration Portal": [
        "02e3ae74-c151-4bda-b8f0-55fbf341de08"
    ],
    "Microsoft Support Diagnostics": [
        "5b534afd-fdc0-4b38-a77f-af25442e3149"
    ],
    "MIP Exchange Solutions - Teams": [
        "2c220739-d44d-4bf7-ba5f-95cf9fb7f10c"
    ],
    "Customer Service Trial PVA - readonly": [
        "6abc93dc-978e-48a3-8e54-458e593ed8cf"
    ],
    "Meeting Migration Service": [
        "82f45fb0-18b4-4d68-8bed-9e44909e3890"
    ],
    "MIP Exchange Solutions - ODB": [
        "8adc51cc-7477-49a4-be4e-263946b4d561"
    ],
    "Customer Service Trial PVA": [
        "944861d3-5975-4f8b-afd4-3422c0b1b6ce"
    ],
    "Microsoft Visual Studio Services API": [
        "9bd5ab7f-4031-4045-ace9-6bebbad202f6"
    ],
    "Office Online Speech SSO": [
        "467423d3-dc5d-4c1e-b0e7-12d85ade8da8"
    ],
    "Microsoft Services": [
        "9ed4cd8c-9a98-405f-966b-38ab1b0c24a3"
    ],
    "Teams NRT DLP Ingestion Service": [
        "0ef94e72-e4fc-4aa0-a8f4-ff27deb3e6eb"
    ],
    "EOP Admin API Web Service": [
        "10214c11-ebd3-44e8-af2f-ebcb8a79c569"
    ],
    "Consumption Billing": [
        "12ff570a-8284-47ed-adb3-fcc72b594c36"
    ],
    "Microsoft Teams IP Policy Service": [
        "1303f293-64bd-48ba-89b0-6bf538bc67f3"
    ],
    "Group Configuration Processor": [
        "1690c5aa-925a-4d0e-836b-722c795bd0d0"
    ],
    "Virtual Connector Provider": [
        "1762e607-063e-431a-a25a-f0f782acb73b"
    ],
    "Policy Processor": [
        "1b489150-9b00-413a-83fd-6ef8f05b6e28"
    ],
    "IpLicensingService": [
        "189cf920-d3d8-4133-9145-23adcc6824fa"
    ],
    "Reading Assignments": [
        "22d27567-b3f0-4dc2-9ec2-46ed368ba538"
    ],
    "Power Platform Governance Services - TIRPS": [
        "2b5e68f0-bdc2-45b0-920a-217d5cbbd505"
    ],
    "Partner Customer Delegated Administration": [
        "2832473f-ec63-45fb-976f-5d45a7d4bb91"
    ],
    "TeamsLinkedInLiveApp": [
        "31ba6d5c-2e14-40fb-bbcb-27dc8a1bfaf5"
    ],
    "AssistAPI": [
        "2b8844d8-6c87-4fce-97a0-fbec9006e140"
    ],
    "PartnerCenterCustomerServiceAppProd": [
        "34cabb34-90ae-4aca-b8c3-c457dbedf145"
    ],
    "ZTNA Policy Service Graph Client": [
        "3b80cd3f-61ca-49b0-8d0f-7b6760e08705"
    ],
    "SEAL All credentials": [
        "38df11dd-582e-4207-be6f-b214675f44a1"
    ],
    "teamsupgradeorchestrator-app": [
        "3cf798a6-b0c5-4d5c-9645-b5273d471fc5"
    ],
    "Intune DeviceCheckIn ConfidentialClient": [
        "4c1a3aed-b389-4824-99b0-514c07906851"
    ],
    "IC3 Modern Effective Config Worker": [
        "481115cb-6d15-4cc0-8caf-f2fee7bfbd2b"
    ],
    "TeamsChatServiceApp": [
        "4cba1704-a0c1-45ee-9d41-fe75b4ef9190"
    ],
    "CAP Package Deployer Service": [
        "4c9fc70a-8d18-4528-9113-c6f1318c4d89"
    ],
    "M365 Lighthouse API": [
        "4eaa7769-3cf1-458c-a693-e9827e39cc95"
    ],
    "OneDriveLTI": [
        "4f547b5f-c3f7-4d2c-a14f-0f8f1286d7d5"
    ],
    "Gatekeeper PPE App": [
        "5a8800f2-f31d-4654-9bed-f5b368c703f8"
    ],
    "Iris Provider EOP Web Service": [
        "61c28d8b-814f-4a57-9c7f-8cd0580aead2"
    ],
    "Gatekeeper Prod App": [
        "5bab4c7f-51c3-479b-a199-06b31afecc8f"
    ],
    "Skype Core Calling Service": [
        "66c23536-2118-49d3-bc66-54730b057680"
    ],
    "Teams CMD Services Artifacts": [
        "6bc3b958-689b-49f5-9006-36d165f30e00"
    ],
    "Power Platform Insights and Recommendations Prod": [
        "6b650392-d446-472e-a422-e47047790237"
    ],
    "Microsoft Dynamics ERP Microservices CDS": [
        "703e2651-d3fc-48f5-942c-74274233dba8"
    ],
    "Funnel and Engagement Data Service": [
        "707aa1ac-be0a-478d-9ce7-0d2765a5c1d6"
    ],
    "Modern Support Connector": [
        "75861f5e-a448-49d7-9c99-6b59bc88c6dc"
    ],
    "Teams NRT DLP Service": [
        "7a274595-3618-4e6f-b54e-05bb353e0153"
    ],
    "Microsoft Teams Admin Gateway Service": [
        "78462efa-e271-409c-a90b-ce3fbd93538a"
    ],
    "Grade Sync": [
        "75cba773-c367-4ba4-8d4f-65f91b68c384"
    ],
    "Intune Remote Help": [
        "7e9f2fca-0cd8-4a6c-a1a0-7ffe48aec7c6"
    ],
    "Medeina Service Dev": [
        "826870f9-9fbb-4f23-81b8-3a957080dfa2"
    ],
    "Microsoft Alchemy Service": [
        "91ad134d-5284-4adc-a896-d7fd24e9fa15"
    ],
    "Arc Public Cloud - Networking": [
        "9449a792-6831-40e2-9097-29dbc6dd4753"
    ],
    "Microsoft Defender for Cloud Apps - Session Controls": [
        "8a0c2593-9cbc-4f86-a247-beb7aab00d83"
    ],
    "One Outlook Web": [
        "9199bf20-a13f-4107-85dc-02114787ef48"
    ],
    "Power Virtual Agents Service": [
        "9d8f559b-5984-46a4-902a-ad4271e83efa"
    ],
    "Purview Ecosystem": [
        "9ec59623-ce40-4dc8-a635-ed0275b5d58a"
    ],
    "PTSS": [
        "9f6c88b7-0272-4581-a75a-ec0340824ed1"
    ],
    "Azure Arc Data Services Billing": [
        "a12e8ccb-0fcd-46f8-b6a1-b9df7a9d7231"
    ],
    "Arc Public Cloud - Servers": [
        "aacceff9-8ec3-413c-83eb-cb131aaf55c6"
    ],
    "Mimir": [
        "aaf3f152-fe17-487b-b671-44d3f7bad293"
    ],
    "Microsoft.ConnectedVMwarevSphere Resource Provider": [
        "ac9dc5fe-b644-4832-9d03-d9f1ab70c5f7"
    ],
    "FrontendTransport": [
        "b24835c0-6b13-41e7-822c-94c9effb98ee"
    ],
    "Partner Customer Delegated Admin Migration": [
        "b39d63e7-7fa3-4b2b-94ea-ee256fdb8c2f"
    ],
    "Dynamics 365 Universal Resource Scheduling": [
        "b2b4502c-fedd-4748-8828-09e1eae11d6a"
    ],
    "Medeina Service": [
        "bb3d68c2-d09e-4455-94a0-e323996dbaa3"
    ],
    "AI Builder Prod Non God Mode": [
        "be5f0473-6b57-40f8-b0a9-b3054b41b99e"
    ],
    "Azure Arc Data Services": [
        "bb55177b-a7d9-4939-a257-8ab53a3b2bc6"
    ],
    "SEAL SNI": [
        "c10f411a-874c-485c-9d66-6e0b34202c41"
    ],
    "ProductsLifecycleApp": [
        "c09dc6d6-3bff-482b-8e40-68b3ad65f3fa"
    ],
    "Medeina Service PPE": [
        "c4de86e3-e322-4889-a781-968c76b6b325"
    ],
    "Office 365 Client Insights Substrate Services Prod": [
        "c94526fa-9f4b-4d30-99f5-849636e4552f"
    ],
    "Azure Guest Container Update Manager": [
        "c8f5141d-83e0-4e9a-84d0-bb6677e26f64"
    ],
    "Messaging Bot API Application for GCC": [
        "c9475445-9789-4fef-9ec5-cde4a9bcd446"
    ],
    "MAPG": [
        "cc46c2aa-d508-409b-aeb7-df7cd1e07aaa"
    ],
    "App Protection": [
        "c6e44401-4d0a-4542-ab22-ecd4c90d28d7"
    ],
    "M365 Compliance Drive": [
        "cedebc57-38a2-4f0a-8472-dfcbba5b04c6"
    ],
    "Arc Token Service": [
        "d00b5d58-cae5-42ad-ae0a-5a2e6f7ee6c9"
    ],
    "Hybrid RP Application": [
        "d2a590e7-6906-4a45-8f41-cecfdca9bca1"
    ],
    "OneLTI": [
        "d3ee6f25-becc-4659-9bc6-bbe6af7d18e6"
    ],
    "Dataverse Resource Provider": [
        "d6101214-691f-47d0-8ea3-dca752e62d71"
    ],
    "M365 Lighthouse Service": [
        "d9d5c99e-b0b4-4bad-92cc-5a6eb5421985"
    ],
    "AADPasswordProtectionProxy": [
        "dda27c27-f274-469f-8005-cce10f270009"
    ],
    "Universal Print": [
        "da9b70f6-5323-4ce6-ae5c-88dcc5082966"
    ],
    "Audit Search Api Service": [
        "e158eb19-34ac-4d1b-a930-ec92172f7a97"
    ],
    "Hybrid Connectivity RP": [
        "e18cedde-9458-482f-9dd1-558c597ac42e"
    ],
    "Microsoft.HybridCompute Agent Service": [
        "eec53b1f-b9a4-4479-acf5-6b247c6a49f2"
    ],
    "Customer Experience Platform CDPA Provisioning PROD": [
        "e3cf99e1-a6e5-4284-9f92-261c7713bc54"
    ],
    "console-m365d": [
        "f18b59c9-5926-4a65-8605-c23ec8c7e074"
    ],
    "Skype For Business Entitlement": [
        "ef4c7f67-65bd-4506-8179-5ddcc5509aeb"
    ],
    "Customer Experience Platform CDPA Provisioning TIP": [
        "f5223e1a-4d50-4fda-9049-55d819fbb03e"
    ],
    "IC3 Modern Effective Config": [
        "f6e5c0c2-4746-4152-b162-91309d5556df"
    ],
    "Membership View Service": [
        "f7a2a81e-ab33-4560-a3dd-6ddca3c5ec6d"
    ],
    "Microsoft Purview Platform": [
        "fd642066-7bfc-4b65-9463-6a08841c12f0"
    ],
    "Microsoft Teams Copilot Bot": [
        "8e55a7b1-6766-4f0a-8610-ecacfe3d569a"
    ],
    "Zoho CRM": [
        "003a8a54-9d27-41cd-9c28-aec5875a3497"
    ],
    "FireHydrant": [
        "00485db5-81b3-4299-833a-8d6c366d0ac0"
    ],
    "tiLly": [
        "032857b6-4d91-4617-bb1a-c44626985bd5"
    ],
    "ESi-Tik": [
        "00ee4a74-9dc3-4bd9-9a6d-f18b640fd69d"
    ],
    "ENA SmartUC Connector": [
        "029cfd5a-4413-499d-bda6-a2a0a3f5e70e"
    ],
    "Dost - Inclusive Language Bot": [
        "01d607db-287c-4354-943d-f015ac938b90"
    ],
    "ContractZen": [
        "0492ead3-ee26-40df-9757-d95cc693d856"
    ],
    "Teameo Class Space": [
        "05525b77-8ca6-462f-8902-15788cb405c6"
    ],
    "Contact Center": [
        "341e195c-b261-4b05-8ba5-dd4a89b1f3e7",
        "3a08b250-02ce-4316-94f7-069f4ae0c41b",
        "c22c3a9e-5d2c-4177-8ea1-1c53c5af36b8"
    ],
    "Workday Peakon Employee Voice": [
        "075a01db-a69f-4975-a713-aa85d004f3b5"
    ],
    "NewCOS": [
        "07d4a8e0-3d1d-4f70-bdc2-f46593d7fa0e",
        "ea4de024-dd5f-4d3e-a092-3b8de6c64200"
    ],
    "Schabi": [
        "084b4a43-c386-443d-ae90-bf9a3fc2995e"
    ],
    "Plandisc": [
        "08da38c2-089b-4c58-9995-60bc2ca54561"
    ],
    "Egnyte for Outlook": [
        "092aa7d1-522d-4d9d-90b6-7186e28eaf4a"
    ],
    "Berrycast": [
        "094f3986-3951-4f0c-88fa-514d117c8dd0"
    ],
    "Assembly": [
        "0a1b7ca8-390e-4f55-a7b5-eee089c5a905"
    ],
    "Coachello": [
        "0b1d36f2-4057-42a1-bfdd-5b7b6b3b8016"
    ],
    "iGlobe CRM Office 365 for Microsoft Office 365": [
        "0bb1641a-3b3b-47f7-a11e-01279d92abfb"
    ],
    "WorkJam Schedule": [
        "0b87cb84-073e-4cf6-a1ef-45d864ef2918"
    ],
    "Excel-to-Word Document Automation": [
        "0bc545b8-97c9-48d1-a62e-7813ed0c2d7d"
    ],
    "Helpfy": [
        "0c4ca6bc-6cc8-43a0-aa3c-4a36af3c3dac"
    ],
    "Wizard": [
        "0c67871c-ffbc-4b37-bd61-afce12b299f9"
    ],
    "Wide Ideas - Innovation Software": [
        "0d56e89d-8356-457f-89a2-618386a39eb8"
    ],
    "DocuWare": [
        "0ef0b13e-3cec-413c-b3ce-2b1ef5ba5570"
    ],
    "RingCentral": [
        "0dd4bfdf-dc86-4f05-9991-a14bc0144ebf"
    ],
    "absentify": [
        "4dce2abf-3f8e-4281-9f7a-d602fc391886",
        "3dbcb38b-8d2f-4e97-9bd1-975fb770b31c"
    ],
    "Jira Integration Plus": [
        "0f22abfb-b687-489d-9fd6-ad1bc95d6d68"
    ],
    "Skedda": [
        "0f198a3c-ad80-44d5-af34-61cfd28e022e"
    ],
    "SignalZen": [
        "102d757e-fe44-49c5-80c2-278c1a2b11b6"
    ],
    "FinTech Studios": [
        "108faf40-9d61-4b6f-bd6f-3b71fcce9a5d",
        "93b14320-d9b5-4876-b621-172af4d36985"
    ],
    "Talkdesk Microsoft Teams Connector": [
        "10d8604b-e6ea-4c59-8414-aca1bf1ffda8"
    ],
    "Citasion": [
        "12397cb1-c0e5-42ae-a5be-ca4084aeadd8"
    ],
    "Glowbl": [
        "12d736b4-dd63-4d2a-a527-e4ab0edb08e9"
    ],
    "ServiceDesk Plus Cloud": [
        "127e5be9-da2c-4335-a284-da367379428a"
    ],
    "SmartStash": [
        "13a1db81-cc98-4568-867f-f902fdcc7335",
        "acc6e49c-7adf-408c-a36f-901c5045c3f3",
        "ded79b59-64ff-4622-8248-42111e954301",
        "f6adea4e-96a4-4d9e-96db-a0bae63a0208"
    ],
    "Lumio": [
        "14cf575a-fae2-48e2-af39-e3448d3a48bb"
    ],
    "Wazoku": [
        "15439749-b811-4e89-b777-4fe6ef247801"
    ],
    "Minecraft Education Edition Services": [
        "16556bfc-5102-43c9-a82a-3ea5e4810689"
    ],
    "OfficeTogether": [
        "17bd2add-67cb-4ffe-b69b-10b130558e89"
    ],
    "Buzzeasy Contact Center for Teams": [
        "1b81b79d-10ff-4614-81cc-5ac3dc64a40c",
        "cbc8bfef-8dd2-4714-ab18-18e15566b63e"
    ],
    "Groopit": [
        "1bc34af7-7913-481b-b251-5444ecc06a61"
    ],
    "Cyberday": [
        "1c7d277c-ff8a-4ea4-bc14-7d06314f8941"
    ],
    "Document Drafter": [
        "1c529524-183e-40db-b1d7-1acf275354b4"
    ],
    "DeskManager": [
        "1d154166-6bd3-423b-b13e-d93ca6327a3e",
        "40aab3eb-744c-42e1-868d-d0227e026690"
    ],
    "Bizfone": [
        "fc8f7563-e8ea-4b6d-9622-82775a21a35a",
        "1dd6ac57-e6f0-4995-a57f-b6d074c16e11"
    ],
    "ComplianceCow": [
        "1d3dca20-8c66-49ac-816c-36d4f3f33073"
    ],
    "Empowering.Cloud": [
        "20882d08-fa82-476c-bded-e77efeb6717f",
        "5e0686a6-0bde-42bb-9691-8a0f85aabf5c"
    ],
    "PayaFy": [
        "1e96a64b-9c1c-4cbc-b015-70243ea06c9b"
    ],
    "Laduma": [
        "21759f96-a64d-450b-bf2a-b5e932d6ea01"
    ],
    "Project Insight": [
        "2201df78-1d70-41da-ba2b-c19b00da1215"
    ],
    "Soundbite?": [
        "2274e9f2-89b3-4a1b-aa01-f7b0af1900cb",
        "e852716e-f657-42f1-b81b-f3c06d2b37c9"
    ],
    "B12": [
        "228af2d7-23b5-4d1f-a5bf-9a1670e4fb6a",
        "75932bb9-5e71-449a-b584-b5cc01c2d118"
    ],
    "Luware Nimbus for Microsoft Teams": [
        "7e1fc6b3-90a7-4a98-a766-5627193e95bc"
    ],
    "Ambition": [
        "24a9cf21-407c-41f9-8cc6-e7015f4e02af"
    ],
    "Sift": [
        "270b510a-7cfb-4a9a-8071-5ceab03cf357",
        "d2a1ed44-6cca-44d2-9b9c-1c9c1d597093"
    ],
    "SQQ": [
        "25379fc8-577f-4935-b681-6f027977fbe3"
    ],
    "BravoNow": [
        "272032ad-0c2e-4928-910e-5d52b19f70d5"
    ],
    "Yoxel Signals": [
        "285303c0-e070-414a-8d97-f20f510012d6"
    ],
    "Smy": [
        "2858d81b-9eb1-4ba1-a79b-b42390bb0015"
    ],
    "Egnyte": [
        "28b871ff-85bf-48a5-9bee-364f2b74d104"
    ],
    "CodeTwo Email Signatures for Office 365": [
        "2a93620e-4345-4e3b-9bae-0195f08aab69",
        "7afd058a-f568-4496-96b1-28d06ab3500f",
        "ce60db2f-439f-4e45-bfdc-d4c827c1820d",
        "cb657bc2-9910-4b9c-82a0-6f4f3a47006b"
    ],
    "Qualified": [
        "2c951ed5-c5c6-493f-9b02-4b42e3ba536c"
    ],
    "Emailgistics": [
        "2c9fb9b7-5112-4a91-af52-f98682bc7bf3"
    ],
    "Weekly10": [
        "6fd1421e-89e8-4a8b-bd01-9397656a50d5",
        "2cc7f3cd-05e3-4ebb-b9f9-d92f1bcda7fb",
        "494610b2-b490-4f54-8384-312d6f9b4869"
    ],
    "EN-UA Dictionary": [
        "2da850e4-5b9d-455c-ae32-bec270de4b60"
    ],
    "Findit": [
        "2e57054c-4326-46ed-8482-40d9a6d20e79"
    ],
    "LawToolBox Deadlines & Matter Management - Outlook": [
        "2fa142be-31b5-4fda-bd37-591541b501aa",
        "6be25d92-7c0e-4b2f-829e-108766e095df"
    ],
    "IXCloud - Teams Compliance Recording & Intelligence": [
        "30c7a49f-89f6-45ba-9938-ed627d102c54",
        "c2395027-53de-4f00-b658-246d82ed7e6f"
    ],
    "SmartPods": [
        "312728bc-5d02-49a5-9230-1f09884f6d04",
        "c884866a-50e4-4b61-a96c-1d22432f7139"
    ],
    "Cegid HR Experience": [
        "342f90c0-6377-4d59-af95-5e1d8c35af4e"
    ],
    "Clypp": [
        "34ed2c1e-bccf-463d-8fbc-0403e72e89fc"
    ],
    "OLIVE VLE": [
        "350df48b-1bc3-452c-9bfa-e02aa435f8ed"
    ],
    "Edpuzzle": [
        "3540209e-c425-4c2e-b3dc-be79e8c0abee"
    ],
    "Read Meeting Navigator": [
        "35e7f5d2-9978-464f-8710-c7a05d5b9fdf"
    ],
    "Autopilot Workflows": [
        "3bc7be07-dc8d-4dc4-a1be-0e8c7ebe9ebc"
    ],
    "SWOOP Analytics": [
        "39cb9f28-b9d0-4bf7-a4f4-d9e38508a0db",
        "ad38b691-43a7-4261-8ad6-f6ebbb229116",
        "c6257830-ff1a-4e7f-86ca-da35c0278de2",
        "49bdbb27-4c8b-4ec9-9812-5ed59027c70d",
        "f4609298-6163-4ae3-9366-72a9d9c4c854",
        "e208746a-2666-4d95-b925-e2ff64b3181d"
    ],
    "DSMN8": [
        "3cf056e3-1c08-4cda-b6d6-962f7c7a1f7c"
    ],
    "Move Work Forward with Jira": [
        "39d845a0-3fa2-4fba-acc2-61afe40cfcea"
    ],
    "Meetgeek": [
        "3f1a3775-c192-4e8c-ae48-d70d144a46c2",
        "6f5cab29-c1ad-4048-bf96-fdbe54dba6ba"
    ],
    "Evocom": [
        "3e745135-a761-48a7-ab54-5c0277b2e642"
    ],
    "Casedoc Virtual Hearing": [
        "3e701664-cc46-49e4-b356-1a7ac6500998"
    ],
    "DZ Notification Bot": [
        "3e63f4cc-5aac-4774-8d2d-fc7b516f9f51"
    ],
    "ezMark": [
        "c1509a1b-f320-4812-b0cd-2802066fe957",
        "413eeea5-41bb-4914-92f1-03cd9e1339ff"
    ],
    "officeatwork - Slide Chooser for Office": [
        "3f2fa737-e376-4c4d-a49d-b8eb08ca7e8d"
    ],
    "Svava for Meetings": [
        "421da895-5e99-4254-b038-209f1ddd5cbb"
    ],
    "Eloops": [
        "431a9917-9c32-480e-a584-6c149e7b7213"
    ],
    "OnePlaceMail for Outlook": [
        "44a72516-136f-4a55-ae26-ef09977230be"
    ],
    "Koare I-management": [
        "45aa6c59-3764-4c2f-abef-178757957e62"
    ],
    "Joye": [
        "42f7cf35-98e6-417e-b5da-8913a5bbec79"
    ],
    "MetaVisitor": [
        "43067020-c59f-49f8-a532-e84ed3bb5f4e"
    ],
    "MyHub": [
        "4d69a8e1-9c38-4b33-b76f-9d59b5ae051b"
    ],
    "Range": [
        "475edd72-5b00-4f77-afdf-33587b9fe594"
    ],
    "Five9 MS Teams Adapter v2": [
        "486d17ac-027c-42da-a78c-9f8c6e33b101"
    ],
    "EmailNotes for Outlook": [
        "471294e9-96d6-475b-b503-e02acd9ed2cd"
    ],
    "Confluence Cloud": [
        "4aa38041-66a2-41a4-ac97-55bc828a9803"
    ],
    "GuineaPig": [
        "4b538c54-11fb-454f-9ac1-6437dcf5f15a"
    ],
    "SyncoBox": [
        "4ace256b-80b8-4b6f-81aa-5fde57a7a25e"
    ],
    "Rungway": [
        "4bea8f81-966b-45fe-8c33-4c8843fda977"
    ],
    "Oncallabot EU": [
        "4da058c6-d88b-4893-a3a0-fb0d338986f7"
    ],
    "Distribution Lists Pro": [
        "4cda80df-64fe-4961-8d73-cbe8d5ad0724"
    ],
    "ZeroTime Bot": [
        "4db812e1-4d29-44e4-b72e-9654c0c91ce4"
    ],
    "MetaLuck": [
        "4c708a72-75bd-4da5-9764-bf0b14e15098"
    ],
    "Appraisd": [
        "4f037969-20ef-4a41-8330-422b7b115eb6"
    ],
    "Push Security": [
        "4ed8651a-5a01-44f0-abdf-536bbc441c02"
    ],
    "Data Hu": [
        "4f953314-c0bf-40cb-96f6-7e4990abb040"
    ],
    "Tonkean": [
        "4fcff517-e16b-42b4-b6f0-5fe449d45479"
    ],
    "Company Navigator": [
        "5123b34d-663d-4ae9-a3c9-d2298be203f2"
    ],
    "Financial Times": [
        "50bff4f3-8dcf-4f58-bf77-180988c2dc3d"
    ],
    "Jira Cloud": [
        "512b84d2-5840-45d6-8d01-5f073836d039"
    ],
    "News - Jalios": [
        "5159b699-a8c3-4170-ae49-c22ccb76cdde"
    ],
    "ahead": [
        "53360535-c93f-497f-b2a1-95bd9aa34283"
    ],
    "Lucca": [
        "53628f6a-ac66-4fde-8945-d639c8da4c0d"
    ],
    "Zavvy": [
        "54a3aa2f-d1de-4565-800e-82f950e26306"
    ],
    "Natterhub": [
        "54cd93cb-c60e-43b7-bbee-686a2b241794"
    ],
    "Navigator": [
        "5490ef0e-c320-4216-ac51-24ea34b9ec7e"
    ],
    "Timeneye": [
        "56412014-bafe-474e-95b4-ebfea106a167"
    ],
    "Tikit Virtual Agent": [
        "55f323bf-3622-4624-b3b5-0582d8be4ad5"
    ],
    "Dynamics 365": [
        "5712d3fd-8e22-4040-afbf-70fa18f63627"
    ],
    "Dynamics 365 Int": [
        "574df941-661b-4bfc-acb0-0a07de7de341"
    ],
    "HubSite 365": [
        "574ae729-b842-4cbb-a767-ab68edc0d51b"
    ],
    "Easy Projects": [
        "59db444e-f9c5-4bff-822d-908279c49b09"
    ],
    "Introhive": [
        "5aee1ae9-72f4-4cf6-a38d-557821f995fd",
        "d2ba6abb-1d2f-477a-9344-1a7581053461"
    ],
    "Bing Places for Business": [
        "5bfe8a29-054e-4348-9e7a-3981b26b125f"
    ],
    "Beep": [
        "5d0905b2-a6de-4480-b5e0-059140592517"
    ],
    "bNear": [
        "5d655b39-963c-465a-89ab-bdad7ab7af7f"
    ],
    "CorporateFitness.app": [
        "5d1cde38-6b6f-4a7c-ab8a-12bb0d449c1d"
    ],
    "Quadra Thankz": [
        "5d8eb1a9-2188-4292-86f6-f4964d49e8b3"
    ],
    "SkillScape": [
        "5dcf4bd7-eccd-4f6d-b5f0-a4e04aab4ff9",
        "95a2eca4-fb4b-4488-8ba8-6bacf3812c76"
    ],
    "Adobe Acrobat Sign Government": [
        "5f17d846-7cdd-4fc3-822f-815b5b737d26"
    ],
    "Office & Microsoft 365 Management & Automation": [
        "5fae112f-79a3-424c-a032-945bd02211dc"
    ],
    "huminos": [
        "5f5ab403-96ae-46a9-b78e-a06d60cc9e4e"
    ],
    "Kami": [
        "5fb90a92-665c-4ec3-863e-e37572074eb2"
    ],
    "Moments365": [
        "60e7d0d4-07ce-4afa-94e5-b8fa14f7629e"
    ],
    "School Day": [
        "61dc5e28-775a-4dd0-8990-aaabe3be9e2f"
    ],
    "Tailored Talks": [
        "61f93bfb-a23c-4043-9187-fbd3326e614b"
    ],
    "Zoho Projects": [
        "621d9ae7-c14e-4fab-9604-63e1ffc9e721"
    ],
    "Canary": [
        "626ce0a3-4620-483d-953d-53b106b9ffad"
    ],
    "DirectFax": [
        "6530e8a1-213e-4847-ba53-5a36d8f4e20c"
    ],
    "HubEngage": [
        "63e17eec-6b5f-476b-a26b-54fde8bd2c83"
    ],
    "Smartsheet EU": [
        "68af659c-8971-4741-b1dd-dba1570f3086"
    ],
    "Kudozza": [
        "69e59100-2fb7-4f6e-a311-987f52b3007b"
    ],
    "BitFractal": [
        "6a1d567b-1106-46a0-83bc-ffe9ada78b9b",
        "8f261936-59e1-44b3-8234-a746c5e4eab7",
        "fb5ad138-bf16-44c0-bdc2-2a9c0e6f246f"
    ],
    "My Reminders": [
        "6b0ce2dd-a270-4ade-babb-7cf54bab8edd"
    ],
    "In Case of Crisis": [
        "6b4a2fee-5642-41a7-b452-d555fac690b0"
    ],
    "CentrePal": [
        "6bf48a21-8a4a-479d-9b32-787a4668475f"
    ],
    "Sembly": [
        "6fbc7944-c8bb-41c2-9628-c5b71150c290"
    ],
    "Base": [
        "6fc1cb88-00f2-412d-84e4-eb1b772d4a06"
    ],
    "Dropbox Sign for SharePoint": [
        "6fcff87e-0f86-49c3-81eb-bc028d1ccfe6"
    ],
    "Ditox": [
        "6fdbc0f1-4be2-4222-b39c-c1de6e21e5d0"
    ],
    "CloudExtend Analytics for NetSuite": [
        "7040f194-bf08-400e-acb1-69df7939416a"
    ],
    "GoBright": [
        "71118671-6b16-46af-94a6-bb72e65eeec5"
    ],
    "Cuckoo": [
        "71138876-8738-4935-95b6-ae7c2fbe4e54"
    ],
    "Vibe": [
        "71a7c2ef-6e5f-4d3d-8665-119a2bef0035"
    ],
    "Mail Signature": [
        "722e11e1-c87f-4f97-803f-3d012d532427"
    ],
    "Senso": [
        "72ffde9e-5189-4085-92b0-1a1bc1d28e7e",
        "a9d28fcf-036e-4a85-9003-332303e3a29b",
        "b8d51467-a865-4e56-8164-938249a5b4bc"
    ],
    "Genesys Cloud CX Teams Integration": [
        "728ece5a-0f26-4c43-9705-cea9debe3fb5"
    ],
    "To-do Checklist for Team": [
        "777d9a9f-feef-48dd-b62d-562ff21aeda2"
    ],
    "Project Migrator": [
        "77b31e8c-65d0-484d-a72f-9404ec9dfcfa",
        "c36d31a2-8de1-4eb5-9e7d-01da45244c04",
        "ca9b0417-d519-4ed6-ae2a-d939583a083c"
    ],
    "Pling by IntraActive": [
        "78472101-8565-4ebe-a478-fbeb5ac8b1e0",
        "83797eec-6657-4fda-a566-d1ac05bfe874"
    ],
    "Howspace": [
        "78497803-9a33-45eb-a368-0657b4a3a540"
    ],
    "Inperly": [
        "79f899cb-c32a-4f7f-8d2d-be8206e2bcc3"
    ],
    "Colloquial": [
        "79b08482-6a09-41ff-a303-7ad2fd9c3531"
    ],
    "Clixie Media": [
        "7ad6b1e9-c645-411d-9ff9-bd590d3fb1c6"
    ],
    "Mia": [
        "7b90f2e4-fe97-4a56-952f-b3c553e537a7"
    ],
    "Microsoft B2B Cross Cloud Worker - Government": [
        "7d9b9ef5-b3c8-45ea-87bc-2da008dc4f72"
    ],
    "Global Administrator - Elevate Access": [
        "7f59a773-2eaf-429c-a059-50fc5bb28b44"
    ],
    "Streamline": [
        "c7cdd862-2527-49ea-b873-0c5f51a83292"
    ],
    "Kadence": [
        "7f89bd86-5355-4c43-b680-929fb7329478"
    ],
    "yuccaHR": [
        "815a5165-fd61-44b8-be99-6301f780bd68"
    ],
    "email-texting": [
        "806359be-da23-4538-80bb-baa82107ec2d"
    ],
    "Okta APAC": [
        "81a69dcc-7a02-46af-8b97-883f4621117d"
    ],
    "Passport 360": [
        "81daf623-cac2-4861-a939-19fdbde90b4d"
    ],
    "DailyBot": [
        "82bfb2e1-cad3-4e99-8995-5d140f295ef2"
    ],
    "Unified Contacts": [
        "83ff0fe1-a544-4390-bd72-3aaaa040db7e"
    ],
    "Checklist as a Service": [
        "8221944c-ce54-485c-a13f-4206648ac3ff"
    ],
    "BrainStorm": [
        "84927bad-d8a3-4cdf-9d5d-e226aca7aad5"
    ],
    "check.it": [
        "898cccfe-ed44-4140-ad2f-c5dd98a12820"
    ],
    "Quadra Visitorz": [
        "86458973-657f-4072-8e6a-f1baf684c62f"
    ],
    "PA PEOPLE": [
        "894d2c27-987c-4426-ab25-b0d6ea4bd0d6"
    ],
    "Remind": [
        "88546d4f-9973-4716-98e4-cd181c04bc2d"
    ],
    "Smart Connect for Jira": [
        "89d5ca9f-d63b-4885-bd30-6e7433c1540c"
    ],
    "Vendict": [
        "8ab99247-f591-45f0-a704-1f40b98b5a73"
    ],
    "Zoho Desk": [
        "8a35e217-58cf-4eab-b2b4-384260d3d7f3"
    ],
    "qChange Leadership Experience": [
        "8ade4647-a577-47a6-963b-2b17a894f34a"
    ],
    "DELTAoverC": [
        "8b893db3-8c29-4983-b905-ee0b3daa6a46"
    ],
    "Verifier": [
        "8cf0fbc9-28f7-4bfb-94db-237b049fcbf7"
    ],
    "Voicero": [
        "8d812966-f462-47cc-b7ef-6cdcbea8f94c",
        "b67e7066-d87e-460b-a84b-ba7d4d7991c0"
    ],
    "MyCheckins": [
        "8f43fc50-571c-4eab-b6ea-675d55e1755e"
    ],
    "smenso Cloud": [
        "931e8ac8-5d36-469b-8d95-938856b206ca"
    ],
    "Delayed Send": [
        "93b661be-66e3-4468-b802-64bb952f1471"
    ],
    "CC4Teams": [
        "9430520a-241f-4a00-b041-56aa8bbc9cc9"
    ],
    "Grytics Companion": [
        "94efdec0-aa15-42e4-b45a-cd6437be5752"
    ],
    "Core Strengths": [
        "95316b85-f9a1-4025-8883-af25638923da"
    ],
    "Cursum": [
        "962ef41c-0088-4cf2-b8ac-df68a8111022"
    ],
    "Foxit PDF Editor": [
        "959a79dd-69d0-4d05-b9a8-b9f02e28c049"
    ],
    "A1 Max UC": [
        "9796decc-6d5d-434e-a42c-f7a6e76b17dc"
    ],
    "CAP Neptune Test CM PreProd": [
        "98189d62-66a9-46d5-8965-11f41aae4606"
    ],
    "Booking Room Pro": [
        "984562b3-6a46-4a7f-a19b-681442b0cdc0"
    ],
    "isLucid": [
        "98b70422-b0b2-41bf-8673-60d85f5d38c7"
    ],
    "Classroom.cloud": [
        "99455ec0-6207-4889-9c8c-96216a274a6b",
        "a554bdf0-866f-4ee2-b95b-3afbfc70d5bc"
    ],
    "Zoho Notebook": [
        "9944c8e1-fc22-4546-8023-9459b75c472a"
    ],
    "365Projects": [
        "99a0a9b1-5d28-45df-9f99-792aa32795f4"
    ],
    "Adobe Acrobat Sign for Microsoft SharePoint Online": [
        "99a3ad8d-8682-4f2a-9c2c-b4b27e99585c"
    ],
    "HPCBOX": [
        "9b3f6e2c-b17d-4c66-bc7e-cd38eebb2785"
    ],
    "Netskope for Microsoft Teams": [
        "9b5751f4-eb23-43ad-ad90-da7afb9300ae"
    ],
    "Webex Call": [
        "9a7ce614-bdc8-4640-aaea-d8c626c58966"
    ],
    "Supermetrics": [
        "9ba8b757-066e-497e-b9d6-c9e087289d8c",
        "f31f0d2b-4955-43a0-b963-f82536093861"
    ],
    "Sharpen Notes": [
        "9ccf0efb-ce3b-4216-ac42-9b3388e4edb9"
    ],
    "Microsoft Azure Data Catalog": [
        "9d3e55ba-79e0-4b7c-af50-dc460b81dca1"
    ],
    "Workplace Analytics": [
        "9d827643-d003-4cca-9dc8-71213a8f1644"
    ],
    "Employee Training Management": [
        "9e8e113c-8a08-4606-b08a-de4decc7252f"
    ],
    "Replay by IntraActive": [
        "9e997761-d28c-4542-8897-94e7b5dc2484"
    ],
    "Enterprise File Sync Service": [
        "a07d3a2b-436e-40ce-9eba-4e5a5664f14c"
    ],
    "Microsoft AppSource": [
        "a0e1e353-1a3e-42cf-a8ea-3a9746eec58c"
    ],
    "speek connecteur": [
        "a1319b29-7801-46a1-a355-bb2498ee1f1e"
    ],
    "Skype for Business Announcement Service": [
        "a15e8d6c-a224-4c00-937a-4fe7287706d1"
    ],
    "MURAL": [
        "a1ef3a23-74fc-4c91-909f-691cc47a1c8e"
    ],
    "ASC Recording Insights": [
        "a22e0150-3615-46aa-b0a7-086c87a9f38d"
    ],
    "Diggspace": [
        "a6604cc9-a6f7-4009-96ba-9f837e528977"
    ],
    "IdeaScale": [
        "a4de8de4-33b1-4e55-97ac-9f87b5978c0f"
    ],
    "Zoho Sign": [
        "a67ee0a9-b008-4e90-986d-1eb8d55a81d6"
    ],
    "Ideas by Sideways 6": [
        "a6bf99af-63e8-40fc-bcfe-77347cb52326"
    ],
    "iPlanner Pro for Office 365": [
        "a6f5c2f4-0bc2-48bf-8afe-6c93583a152b"
    ],
    "TeamLinx42": [
        "a788e8ed-f5e5-46c1-869c-b6495214b96c",
        "d4b6a9ae-16c7-420e-93ed-9ec2082fb3f0"
    ],
    "CoffeePals": [
        "a70d21af-f6a0-450c-8c81-9c3862823578"
    ],
    "Attendant": [
        "a7bdb4c6-23d0-4e4a-958a-168b50d67465"
    ],
    "Voice Elements": [
        "a7f20956-7af0-4e03-8582-3812a87e029e"
    ],
    "Appspace": [
        "a9a866c4-e5cf-47f2-932c-db14cb89008f"
    ],
    "Machine Learning Services Network Management": [
        "aa175e40-6f9c-4aa5-856a-4638955d2366"
    ],
    "Adobe Acrobat Sign for Microsoft Outlook": [
        "a9b0c190-bafb-49ca-a61a-dab99cf2c43b"
    ],
    "Ticketing As A Service": [
        "aa6b770e-6b8c-4096-9648-5239295ecadc"
    ],
    "CAI Adoption Bot": [
        "abe28a0d-6acc-47d8-9169-cfcc2553bc13"
    ],
    "JustLogin": [
        "af5883db-bda9-4d1a-b1ce-022bea20f021"
    ],
    "TeamOrgChart": [
        "b12699ab-e60a-46b1-8c9e-231d489947aa"
    ],
    "CyDesk": [
        "acafd8f7-a6d3-420e-89d7-7729751b7c04"
    ],
    "RowShare": [
        "affa8732-9527-4cb1-9051-85d43fba3ce7"
    ],
    "Tikit": [
        "b13c40ee-e073-459e-96b5-3f3cca046a37"
    ],
    "Contacts Pro": [
        "b2380441-bb33-439e-bf4a-8cd277dcebc8"
    ],
    "Plumm": [
        "b1d1c038-a1f3-4802-be93-0f4a66589e73"
    ],
    "Forza Board": [
        "b4db3055-5e98-4935-862e-7ffd42761eaa"
    ],
    "Microsoft Volume Licensing": [
        "b4ec8d8b-0275-4833-8568-690db4af4b45",
        "3ab9b3bc-762f-4d62-82f7-7e1d653ce29f"
    ],
    "Journey Automation": [
        "b4ee3df9-abff-4c0b-9d4d-408295a95707"
    ],
    "Remoto": [
        "b601b4e6-b126-4c70-b8ec-e800f28ae2ea",
        "fd7d9d09-58cb-45e9-940a-7ec22c96937c"
    ],
    "Cloud Hub": [
        "b5d4e933-e001-4168-83f8-abdd974877bd"
    ],
    "Vizito": [
        "b6e2ef19-7612-4ab7-a700-9669d49b88b9"
    ],
    "Viima": [
        "b8ea7030-ce4d-4ecd-98d7-dc16d8298d1b"
    ],
    "Tendfor": [
        "b7e8237f-d86d-4874-8f8b-7faa8f768436"
    ],
    "Perfect Wiki": [
        "b9604964-9c3a-483e-abf2-1b5cba495081"
    ],
    "Pandos": [
        "b979eaca-19be-437e-9dc4-bc59418a2034"
    ],
    "Canva": [
        "ba283eae-0bde-47ad-bb66-31058c778294"
    ],
    "Crewting": [
        "ba095977-4e55-4b89-b1ad-628c551b40c9"
    ],
    "Rattle": [
        "bacd48e3-a2e1-48db-992f-609eb58ac326"
    ],
    "Okta": [
        "bc502afe-55af-47c9-beca-3a6e56547285"
    ],
    "Photo Filer": [
        "be3cd296-fc8e-44d5-968b-32cf0371749c",
        "e54fe734-bab8-48b2-9ec8-05c2545cc49d"
    ],
    "Geekbot": [
        "bd2aaebe-63b9-434b-aad8-e7010f2ece20"
    ],
    "TeamSticker by Communitio": [
        "bceca1f0-723f-44d0-b732-b3506c0a641d"
    ],
    "Quantum Workplace for Teams": [
        "be93046b-63ab-4216-9bcc-78faa55eeaa7"
    ],
    "SurveyMoodbit": [
        "bed944b9-c7f5-459a-b7af-53c421248893"
    ],
    "SightCall": [
        "c5312ffd-d146-4515-89e0-b43fa5282368"
    ],
    "GoLinks": [
        "c1abaf93-e823-4e9a-a810-34a47e77ef71"
    ],
    "Loopio": [
        "c2f87ddb-d2e0-4268-851f-88d57ac6e0a0"
    ],
    "Call Quality Dashboard": [
        "c61d67cf-295a-462c-972f-33af37008751"
    ],
    "Timewax": [
        "c6557591-6b74-430d-b25e-87ab28766f32"
    ],
    "Solo": [
        "c626ce8b-6d15-4c07-bfb1-a5fd0bc3c20e"
    ],
    "Smartsheet": [
        "c68947ae-a07f-44ce-9a13-7b559251731d",
        "3290e3f7-d3ac-4165-bcef-cf4874fc4270"
    ],
    "AIRS": [
        "c7d28c4f-0d2c-49d6-a88d-a275cc5473c7"
    ],
    "Desk reservations": [
        "c9b3645e-2695-46c5-970d-e06f5c74bcfa"
    ],
    "novaCapta Compass": [
        "ca801596-7c3b-4fe8-a1d5-e25155970304"
    ],
    "Myfone": [
        "cdd5ed6f-ceda-4d46-a522-b7526d6d9e50",
        "f0199b83-0ca3-4b41-a23b-d9b234484438"
    ],
    "Offishall Planning": [
        "cbdfe641-3e2e-449d-b4f7-7e377c7060aa"
    ],
    "Berry": [
        "cbc1f86a-32a7-4efb-8c6c-cde1964aa9a2"
    ],
    "Skype for Business OrgAA": [
        "ce933385-9390-45d1-9512-c8d228074e07"
    ],
    "Team Today": [
        "d1d8d8c3-5199-45c2-afcc-aaab4dd8da5d"
    ],
    "Beesy": [
        "d27f56ed-ddc7-4cf8-86ac-721b76c7d287"
    ],
    "polumana Tour Route Planner": [
        "d361752a-c257-474d-bb79-324fbe4898b5"
    ],
    "Forbury": [
        "d2c7af43-2e9d-41b2-b374-e9ffbe316d61"
    ],
    "EducationHUB Lesmateriaal": [
        "d3c78487-7def-49e1-9d17-40e94d66ac5b"
    ],
    "Map Pro": [
        "d44d071f-a9e5-4f99-b72e-5ab38cd7b175"
    ],
    "Feeder": [
        "d6286bf8-c566-4451-a252-fc96ac6d8787"
    ],
    "Ideanote": [
        "d7db1079-6f45-4373-bb2b-ae5d71169b31"
    ],
    "Funtivity by Hermis": [
        "d75e14a9-9bfd-43b4-8430-7264da3b6995"
    ],
    "Akouo Interpretation": [
        "d863a24b-7cdd-46c9-8309-a15878f4f7bf"
    ],
    "1Page": [
        "d7e20ef1-fc4b-42e0-a74f-a3c9a806aa73"
    ],
    "Powow": [
        "d871e46e-e346-445d-bfe8-2a66419bf278",
        "f121a92d-d9a9-43fd-be70-f7a47ff83d4f"
    ],
    "Verto 365": [
        "d8843264-a57b-41e3-aea6-b83ea56f6bd6"
    ],
    "Quitch": [
        "d980249e-fb0c-40a9-8706-f77f95660bdc"
    ],
    "Skype for Business Voicemail": [
        "db7de2b5-2149-435e-8043-e080dd50afae"
    ],
    "Template Chooser": [
        "dae2eacf-3eb5-4440-baff-984fbd5cae68"
    ],
    "Loops - Creative Learning": [
        "dc171e47-c074-4bc2-9e7b-3856b71e0630"
    ],
    "SimplyDo": [
        "dbf692fe-35c1-4511-9178-9131e6511712"
    ],
    "T-Workspace": [
        "dbba83f3-792a-4e38-9d15-8521bfdf82c8"
    ],
    "Workpath": [
        "dc8facfc-c606-44b4-a0ad-04f81446845c"
    ],
    "CloudLicensingSystem": [
        "de247707-4e4a-47d6-89fd-3c632f870b34"
    ],
    "Fond": [
        "dea67e43-444e-4852-b57b-b57878a4022b"
    ],
    "Tilde Meeting Assistant": [
        "e382dc52-27aa-4e5c-8f0b-e7943203bd60"
    ],
    "QuickMinutes": [
        "e340e520-b8f4-4752-8e1c-60270c863b12"
    ],
    "Amplify by Hootsuite": [
        "e308040f-41b5-4b8c-8f08-c2c38056f7e2"
    ],
    "Creately": [
        "e4218775-2e3c-44eb-807f-78f8f39a04d8"
    ],
    "NetDocuments (US Vault)": [
        "e5508a21-c77a-4e62-a230-603d5b3ce019"
    ],
    "Team GPS": [
        "e5e41086-e65f-464d-a225-784c944cfdca"
    ],
    "GoConqr": [
        "e5e5c455-c92a-46b7-adbc-da0f9a3e787f"
    ],
    "Degreed": [
        "e5e829df-1793-40fb-806a-8f9ce70a8e14"
    ],
    "TELUS Business Connect": [
        "e601bd6e-0476-4d66-bd57-a9d13c207f0b"
    ],
    "Contatta": [
        "e76a3e8a-57dd-40b8-ac73-58899d8c5994"
    ],
    "COR": [
        "e73458d3-c732-4460-bfb2-9da9086fc714"
    ],
    "AI Producer": [
        "e7fb100c-8c81-4e3f-9c78-bb1407080cdc"
    ],
    "Abi": [
        "e7c09c44-c705-4d05-89cb-3582dfccd89b"
    ],
    "Image Chooser": [
        "e8bea835-c6b0-45aa-9c39-889d3c77d5a3"
    ],
    "Classified Listing": [
        "e8a37d29-e4be-4ce1-ae06-bbd1ad1968e3"
    ],
    "Adobe Acrobat Sign for Microsoft 365": [
        "ea36b867-ca67-45fd-a61b-d2be86273167"
    ],
    "Standuply": [
        "e9f5cb58-89eb-4f80-9a6c-b73823b62176"
    ],
    "myRH4ALL": [
        "eaa1cce1-b956-4bc0-8fe6-b8b961e61e75"
    ],
    "Rezolve.ai": [
        "eb628055-f790-4ef0-9fce-ac95b4c61466"
    ],
    "Switchvox": [
        "eb668aa5-abb2-445c-81b4-3c174db84fe2"
    ],
    "Agile Task Board for SharePoint Online": [
        "ed6cb2ac-21e8-4e9c-a917-6a2d5f03e3a5"
    ],
    "Adobe Acrobat": [
        "ecff17cf-5629-49ba-a629-7f575496aeac"
    ],
    "Content Chooser": [
        "edb24f8f-38af-4b3e-9475-0da243678d5a"
    ],
    "Klarytee": [
        "eed96ca4-e9b6-4573-a559-bf009f428999"
    ],
    "Klaxoon": [
        "ef685106-cba6-4374-a250-a89d51df6e34"
    ],
    "Alvao Service Desk": [
        "ef5fa233-c0bb-424e-b9dc-0466d46bade2"
    ],
    "Comms Planner": [
        "f29ce025-8c25-437b-9d7e-9d38e8fcf4dc"
    ],
    "PandaDoc": [
        "f2d4eec7-3d3f-46b1-a094-9f7c733d260b"
    ],
    "PlayQuiz - Aprende & Juega": [
        "f3277edf-4f66-4e94-853b-cc1f1e2914f8"
    ],
    "Desk365": [
        "f2faee17-4aa9-44ba-bc06-122ab36b8c3f"
    ],
    "WorkJam Time Clock": [
        "f3388437-b373-4ea7-bcbd-58ec773e0ecf"
    ],
    "Confluence Connector by MWF": [
        "f3943662-e828-40ed-9c6e-369680fe421f"
    ],
    "Heedify": [
        "f3ad2154-7e10-4730-a055-8852ced42d47"
    ],
    "Umbiko": [
        "f55846a9-644f-4914-af55-4ddc115a1817"
    ],
    "Uploader": [
        "f5c9f179-b9a5-4364-8f99-18d203b902ad"
    ],
    "timeghost - Time tracking": [
        "f6f894ce-5b44-4c9b-aff4-253d2fbe8a99"
    ],
    "Fellow": [
        "f6671df0-1909-428c-91f7-1c42df04d3e4"
    ],
    "TagMyFav": [
        "f5f2921e-bfb3-4d75-b84f-0b2cc13096f7"
    ],
    "itslearning Course Overview": [
        "f85cd0ac-957e-4116-8309-9af69ebdec97"
    ],
    "Zendesk": [
        "fbec26ad-da44-4a5d-8e6d-30df5435c84e"
    ],
    "DoctorOnline": [
        "f9555238-64f3-4ec2-a8fc-3787baa157aa"
    ],
    "uWebChat": [
        "fbc29d83-1fe3-48ad-b0a4-2785adf25984"
    ],
    "Microsoft Partner Center": [
        "fa3d9a0c-3fb0-42cc-9193-47c7ecd2edbd"
    ],
    "eformity - Template Management": [
        "ff50870f-b19b-489c-9766-4bcee4e843eb"
    ],
    "Scormium": [
        "ffdbe361-6168-42f7-beef-d1931b7922da"
    ],
    "Intune Provisioning Client": [
        "f1346770-5b25-470b-88bd-d5744ab7952c"
    ],
    "WorkInSync": [
        "fdabfc71-2cf8-42f0-bcdd-83e5f4acfdcc"
    ],
    "Sign in OIDC": [
        "3b511579-5e00-46e1-a89e-a6f0870e2f5a"
    ],
    "Compromised Account Service": [
        "433895fb-4ec7-45c3-a53c-c44d10f80d5b"
    ],
    "Nearpod": [
        "7b77b3a2-8490-49e1-8842-207cd0899af9"
    ],
    "Microsoft Profile Service Platform Service": [
        "087a2c70-c89e-463f-8dd3-e3959eabb1a9"
    ],
    "Tutum": [
        "e6acb561-0d94-4287-bd3a-3169f421b112"
    ],
    "NovoEd": [
        "b10686fd-6ba8-49f2-a3cd-67e4d2f52ac8"
    ],
    "Power BI Tiles": [
        "aaf214cc-8013-4b95-975f-13203ae36039"
    ],
    "Evercontact": [
        "569e8598-685b-4ba2-8bff-5bced483ac46"
    ],
    "DocuSign": [
        "dff9b531-6290-4620-afce-26826a62a4e7"
    ],
    "BillingExtension": [
        "0c8139b5-d545-4448-8d2b-2121bb242680"
    ],
    "TeamImprover - Team Organization Chart": [
        "75018fbe-21fe-4a57-b63c-83252b5eaf16"
    ],
    "Microsoft Education": [
        "fe217466-5583-431c-9531-14ff7268b7b3"
    ],
    "Wunderlist": [
        "4b4b1d56-1f03-47d9-a0a3-87d4afc913c9"
    ],
    "Office Personal Assistant at Work Service": [
        "28ec9756-deaf-48b2-84d5-a623b99af263"
    ],
    "Office Agent Service": [
        "5225545c-3ebd-400f-b668-c8d78550d776"
    ],
    "Apiary for Power BI": [
        "ad230543-afbe-4bb4-ac4f-d94d101704f8"
    ],
    "Boomerang": [
        "e691bce4-6612-4025-b94c-81372a99f77e"
    ],
    "PowerApps Runtime Service": [
        "82f77645-8a66-4745-bcdf-9706824f9ad0"
    ],
    "PowerApps and Flow": [
        "0004c632-673b-4105-9bb6-f3bbd2a927fe"
    ],
    "calendly": [
        "c2f89f53-3971-4e09-8656-18eed74aee10"
    ],
    "Meetup": [
        "a1cf9e0a-fe14-487c-beb9-dd3360921173"
    ],
    "Amazon Alexa": [
        "9f505dbd-a32c-4685-b1c6-72e4ef704cb0"
    ],
    "Cloudsponge": [
        "a43e5392-f48b-46a4-a0f1-098b5eeb4757"
    ],
    "Glip Contacts": [
        "da109bdd-abda-4c06-8808-4655199420f8"
    ],
    "RITS Dev": [
        "5c2ffddc-f1d7-4dc3-926e-3c1bd98e32bd"
    ],
    "Tasks in a Box": [
        "82b293b2-d54d-4d59-9a95-39c1c97954a7"
    ],
    "FedExPackageTracking": [
        "fdc83783-b652-4258-a622-66bc85f1a871"
    ],
    "Alignable": [
        "44eb7794-0e11-42b6-800b-dc31874f9f60"
    ],
    "LinkedIn Microsoft Graph Connector": [
        "744e50be-c4ff-4e90-8061-cd7f1fabac0b"
    ],
    "Attach OneDrive files to Asana": [
        "f217ad13-46b8-4c5b-b661-876ccdf37302"
    ],
    "SurveyMonkey": [
        "07978fee-621a-42df-82bb-3eabc6511c26"
    ],
    "OxBlue Interface Single Sign On": [
        "46dc8a63-d44f-48c5-8cb2-1ffe4d3fbacb"
    ],
    "cloudHQ Office365 OneDrive": [
        "fdde1e98-e665-4260-a642-9b51c983f156"
    ],
    "Programmer's-Admin": [
        "2e280d21-3433-4b54-a9ee-03ac8a0f5b7b"
    ],
    "CamCard for Outlook": [
        "60c86dd2-b3cf-4f89-9af6-ab1144465ac0"
    ],
    "MS Tech Comm": [
        "09213cdc-9f30-4e82-aa6f-9b6e8d82dab3"
    ]
}

ALL_APP_REQ_SECRET_IDS = set()
for secret_ids in REQUIRE_SECRET_APPS.values():
    ALL_APP_REQ_SECRET_IDS.update(secret_ids)

# Apps that are flagged as FOCI apps
FOCI_APPS = [
    "1950a258-227b-4e31-a9cf-717495945fc2",
    "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
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


INVALID_APPS = {}
VALID_APPS = {}
FOCI_APPS = []

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
    res = requests.post(f"{authority_url}/oauth2/token", data=data, timeout=30)
    
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
        elif error_code == 50034:
            error_summary = "Unknown user, not going to continue"
            print(f"{Fore.RED}{error_summary}{Style.RESET_ALL}")
            exit(1)
        elif error_code == 50126:
            error_summary = "Invalid credentials, not going to continue"
            print(f"{Fore.RED}{error_summary}{Style.RESET_ALL}")
            exit(1)
        else:
            error_summary = "Unknown error"
            #print(error_code)
            #print(error_msg)
    
        return {"error_description": error_msg, "error_summary": error_summary, "login_error": True}
    
    token_info = res.json()
    token_info["is_foci"] = client_id in FOCI_APPS
    return token_info


def process_app_client(name, client_id, username, password, outfile_path, file_lock, valid_lock, print_errors, print_validate):
    """
    Process a single app and client ID combination.
    Iterates through all resource URIs and attempts authentication.
    Writes the token to the temporary file if successfully created.
    """

    global INVALID_APPS, VALID_APPS, FOCI_APPS
    last_error = None

    for res_uri in RESOURCE_URIS:
        token = authenticate_username_password_native(username, password, client_id, res_uri)
        
        if token.get("login_error"):
            last_error = token.get("error_summary", "Unknown error")
            # If this is the last resource URI, print the error details.
            if res_uri == RESOURCE_URIS[-1]:
                print(f"{Fore.RED}Failed to create token for app {name} ({client_id}) with {res_uri}. Reason: {last_error}{Style.RESET_ALL}")
                if print_errors:
                    print(f"{Fore.YELLOW}Error details: {token.get('error_description', 'No details provided')}{Style.RESET_ALL}")
            
            if last_error == "Need client_secret" and print_validate:
                with valid_lock:
                    if name in INVALID_APPS:
                        if client_id not in INVALID_APPS[name]:
                            INVALID_APPS[name].append(client_id)
                    else:
                        INVALID_APPS[name] = [client_id]
            continue
        
        # Successful token creation
        msg = f"{Fore.GREEN}Token created for app {name} ({client_id}) with {res_uri}{Style.RESET_ALL}"

        if token.get("is_foci"):
            print(f"{Fore.YELLOW}FOCI {Fore.GREEN}{msg}")
        else:
            print(msg)
        
        # Write token information to the temporary file in a thread-safe manner
        with file_lock:
            with open(outfile_path, "w") as f:
                f.write(f"App: {name}, Client: {client_id}, Resource: {res_uri}, Token: {token}\n\n\n")
    
    # Update the global VALID_APPS or INVALID_APPS dictionaries safely
    if print_validate:
        with valid_lock:
            if name in VALID_APPS:
                if client_id not in VALID_APPS[name]:
                    VALID_APPS[name].append(client_id)
            else:
                VALID_APPS[name] = [client_id]

def process_if_foci_app(client_id, foci_refresh_token, tenant, valid_lock):
    """
    Check if the given client ID is a FOCI app using the provided refresh token.
    If it is, add it to the global FOCI_APPS list in a thread-safe manner.
    """

    global FOCI_APPS
    for res_uri in REQUIRE_SECRET_RESOURCE_URIS:
        scopes = [f"{res_uri}.default"] # res_uri already ends with "/"
        if check_if_foci_app(client_id, foci_refresh_token, scopes, tenant):
            with valid_lock:
                print(f"{Fore.YELLOW}FOCI app found: {client_id} with resource {res_uri}{Style.RESET_ALL}")
                FOCI_APPS.append(client_id)
                break


def check_if_foci_app(client_id, foci_refresh_token, scopes, tenant_id):
    """
    Check if the given client ID is a FOCI app using the provided refresh token.
    """

    app = msal.PublicClientApplication(
            client_id=client_id, authority=f"https://login.microsoftonline.com/{tenant_id}"
        )

    tokens = app.acquire_token_by_refresh_token(foci_refresh_token, scopes=scopes)
    if "access_token" in tokens:
        return True
    else:
        return False


def main():
    """
    Main function to authenticate with apps and resource URIs using threading.
    Sets up the argument parser, starts the threads, and prints the results.
    """
    global INVALID_APPS, VALID_APPS, FOCI_APPS

    parser = argparse.ArgumentParser(description='Authenticate to apps and resources.')
    parser.add_argument('--username', required=True, type=str, help='Username to login')
    parser.add_argument('--password', required=True, type=str, help='Password to login')
    parser.add_argument('--outfile', required=True, type=str, help='File path to write tokens')
    parser.add_argument('--print-errors', action='store_true', help='Print the whole error description.')
    parser.add_argument('--threads', type=int, default=5, help='Number of threads (default 5)')
    parser.add_argument('--print-validate', default=False, action='store_true', help='Print jsons of valid and invalid (secret required) apps')
    parser.add_argument('--get-foci-apps', default=False, action='store_true', help="If true, AppSweep won't be performed but just apps will be checkd if they are FOCI. The given credentials must be able to generate a refresh token on the Azure CLI app.")
    args = parser.parse_args()

    username = args.username
    password = args.password
    outfile_path = args.outfile
    print_errors = args.print_errors
    n_threads = args.threads
    print_validate = args.print_validate
    get_foci_apps = args.get_foci_apps
    tenant = username.split("@")[1]

    foci_refresh_token = ""
    if get_foci_apps:
        tokens = authenticate_username_password_native(username, password, "04b07795-8ddb-461a-bbee-02f9e1bf7b46", "https://management.azure.com/")
        foci_refresh_token = tokens["refresh_token"]

    # Initialize locks for thread-safe file writing and dictionary updates
    file_lock = threading.Lock()
    valid_lock = threading.Lock()

    # Use a ThreadPoolExecutor with 3 threads
    if not get_foci_apps:
        print(f"{Fore.MAGENTA} Starting checking apps...{Style.RESET_ALL}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            for name, client_ids in APPS.items():
                for client_id in client_ids:
                    #print(f"{Fore.CYAN}Logging into app {name} ({client_id}){Style.RESET_ALL}")
                    future = executor.submit(process_app_client, name, client_id, username, password, outfile_path, file_lock, valid_lock, print_errors, print_validate)
                    futures.append(future)
            # Wait for all threads to finish
            concurrent.futures.wait(futures)
    
    else:
        print(f"{Fore.MAGENTA}Starting checking FOCI apps...{Style.RESET_ALL}")
        total_tasks = sum(len(ids) for ids in APPS.values()) + sum(len(ids) for ids in REQUIRE_SECRET_APPS.values())

        with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
            futures = []
            
            # Schedule tasks
            for name, client_ids in APPS.items():
                for client_id in client_ids:
                    futures.append(
                        executor.submit(process_if_foci_app, client_id, foci_refresh_token, tenant, valid_lock)
                    )

            for name, client_ids in REQUIRE_SECRET_APPS.items():
                for client_id in client_ids:
                    futures.append(
                        executor.submit(process_if_foci_app, client_id, foci_refresh_token, tenant, valid_lock)
                    )

            # Track completion with tqdm
            for _ in tqdm(concurrent.futures.as_completed(futures), total=total_tasks, desc="Processing Apps"):
                pass  # tqdm automatically updates progress as tasks complete
    
    if FOCI_APPS:
        print(f"{Fore.MAGENTA}=============================={Style.RESET_ALL}")
        print(f"{Fore.RED}FOCI apps:{Style.RESET_ALL}")
        for app in FOCI_APPS:
            if app in ALL_APP_REQ_SECRET_IDS:
                print(f"{Fore.YELLOW}{app}{Style.RESET_ALL} (requires secret)")
            else:
                print(f"{Fore.YELLOW}{app}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}=============================={Style.RESET_ALL}")
    
    if print_validate:
        print(f"{Fore.MAGENTA}=============================={Style.RESET_ALL}")
        print(f"{Fore.RED}Invalid apps:{Style.RESET_ALL}")
        print(json.dumps(INVALID_APPS, indent=4))
        print("===============================")
        print(f"{Fore.GREEN}Valid apps:{Style.RESET_ALL}")
        print(json.dumps(VALID_APPS, indent=4))

if __name__ == "__main__":
    main()


