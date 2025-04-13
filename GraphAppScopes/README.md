## GraphAppsScopesBruteforcing

This script takes a FOCI refresh token and the tenant ID and bruteforces the scopes that can be requested by each app in each resource.


## getByScope

This will ask for a scope permission and return all the apps that can have that scope in their token.

It'll first print ina readable format all the app IDs and requiresting scopes needed to get a set of scopes that contains the indicated scope. Then, it'll print a dictionary with the scopes as keys and the app IDs that can have that scope in their token.

Example:

```bash
python3 getByScope.py

Enter the scope permission to search for: Mail.Read
- App ID: 1fec8e78-bce4-4aaf-ab1b-5451cc387264
  - Requesting: AppCatalog.Read.All
  - Found Scopes: ['AppCatalog.Read.All', 'Channel.ReadBasic.All', 'Contacts.ReadWrite.Shared', 'email', 'Files.ReadWrite.All', 'FileStorageContainer.Selected', 'InformationProtectionPolicy.Read', 'Mail.ReadWrite', 'Mail.Send', 'MailboxSettings.ReadWrite', 'Notes.ReadWrite.All', 'openid', 'Organization.Read.All', 'People.Read', 'Place.Read.All', 'profile', 'Sites.ReadWrite.All', 'Tasks.ReadWrite', 'Team.ReadBasic.All', 'TeamsAppInstallation.ReadForTeam', 'TeamsTab.Create', 'User.ReadBasic.All']


- App ID: 1fec8e78-bce4-4aaf-ab1b-5451cc387264
  - Requesting: Channel.ReadBasic.All
  - Found Scopes: ['AppCatalog.Read.All', 'Channel.ReadBasic.All', 'Contacts.ReadWrite.Shared', 'email', 'Files.ReadWrite.All', 'FileStorageContainer.Selected', 'InformationProtectionPolicy.Read', 'Mail.ReadWrite', 'Mail.Send', 'MailboxSettings.ReadWrite', 'Notes.ReadWrite.All', 'openid', 'Organization.Read.All', 'People.Read', 'Place.Read.All', 'profile', 'Sites.ReadWrite.All', 'Tasks.ReadWrite', 'Team.ReadBasic.All', 'TeamsAppInstallation.ReadForTeam', 'TeamsTab.Create', 'User.ReadBasic.All']
[...]




{
    "AppCatalog.Read.All": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
    ],
    "Channel.ReadBasic.All": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "57336123-6e14-4acc-8dcf-287b6088aa28"
    ],
    "Contacts.ReadWrite.Shared": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264"
    ],
    "email": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "57336123-6e14-4acc-8dcf-287b6088aa28",
        "d7b530a4-7680-4c23-a8bf-c52c121d2e87",
        "00b41c95-dab0-4487-9791-b9d2c32c80f2",
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "EWS.AccessAsUser.All": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "00b41c95-dab0-4487-9791-b9d2c32c80f2",
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "Files.ReadWrite.All": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "57336123-6e14-4acc-8dcf-287b6088aa28",
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "FileStorageContainer.Selected": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "d3590ed6-52b3-4102-aeff-aad2292ab01c",
        "27922004-5251-4030-b22d-91ecd9a37ea4"
    ],
    "InformationProtectionPolicy.Read": [
        "1fec8e78-bce4-4aaf-ab1b-5451cc387264",
        "d3590ed6-52b3-4102-aeff-aad2292ab01c"
    ],
[...]
```

## getByApp

This will ask for an app ID and return all the scopes that can be requested by that app on each Aud the app can access.

Example:


```bash
python3 getByApp.py

Enter the app to search for: 57336123-6e14-4acc-8dcf-287b6088aa28
- Requesting: Calendars.Read
  - Aud: 00000003-0000-0000-c000-000000000000
  - Found Scopes: ['Calendars.Read', 'Channel.ReadBasic.All', 'ChannelMessage.Send', 'Contacts.Read', 'Directory.Read.All', 'EduRoster.ReadBasic', 'email', 'Files.ReadWrite.All', 'Group.Read.All', 'Mail.ReadWrite', 'Mail.Send', 'Notes.Create', 'Notes.Read', 'Notes.ReadWrite', 'openid', 'People.Read', 'profile', 'User.Read', 'User.Read.All', 'User.ReadBasic.All']


- Requesting: Channel.ReadBasic.All
  - Aud: 00000003-0000-0000-c000-000000000000
  - Found Scopes: ['Calendars.Read', 'Channel.ReadBasic.All', 'ChannelMessage.Send', 'Contacts.Read', 'Directory.Read.All', 'EduRoster.ReadBasic', 'email', 'Files.ReadWrite.All', 'Group.Read.All', 'Mail.ReadWrite', 'Mail.Send', 'Notes.Create', 'Notes.Read', 'Notes.ReadWrite', 'openid', 'People.Read', 'profile', 'User.Read', 'User.Read.All', 'User.ReadBasic.All']


- Requesting: ChannelMessage.Send
  - Aud: 00000003-0000-0000-c000-000000000000
  - Found Scopes: ['Calendars.Read', 'Channel.ReadBasic.All', 'ChannelMessage.Send', 'Contacts.Read', 'Directory.Read.All', 'EduRoster.ReadBasic', 'email', 'Files.ReadWrite.All', 'Group.Read.All', 'Mail.ReadWrite', 'Mail.Send', 'Notes.Create', 'Notes.Read', 'Notes.ReadWrite', 'openid', 'People.Read', 'profile', 'User.Read', 'User.Read.All', 'User.ReadBasic.All']
[...]



{
    "Calendars.Read": {
        "00000003-0000-0000-c000-000000000000": [
            "Calendars.Read",
            "Channel.ReadBasic.All",
            "ChannelMessage.Send",
            "Contacts.Read",
            "Directory.Read.All",
            "EduRoster.ReadBasic",
            "email",
            "Files.ReadWrite.All",
            "Group.Read.All",
            "Mail.ReadWrite",
            "Mail.Send",
            "Notes.Create",
            "Notes.Read",
            "Notes.ReadWrite",
            "openid",
            "People.Read",
            "profile",
            "User.Read",
            "User.Read.All",
            "User.ReadBasic.All"
        ]
    },
    "Channel.ReadBasic.All": {
        "00000003-0000-0000-c000-000000000000": [
            "Calendars.Read",
            "Channel.ReadBasic.All",
            "ChannelMessage.Send",
            "Contacts.Read",
            "Directory.Read.All",
            "EduRoster.ReadBasic",
            "email",
            "Files.ReadWrite.All",
            "Group.Read.All",
            "Mail.ReadWrite",
            "Mail.Send",
            "Notes.Create",
            "Notes.Read",
            "Notes.ReadWrite",
            "openid",
            "People.Read",
            "profile",
            "User.Read",
            "User.Read.All",
            "User.ReadBasic.All"
        ]
    },
    "ChannelMessage.Send": {
        "00000003-0000-0000-c000-000000000000": [
            "Calendars.Read",
            "Channel.ReadBasic.All",
            "ChannelMessage.Send",
            "Contacts.Read",
            "Directory.Read.All",
            "EduRoster.ReadBasic",
            "email",
            "Files.ReadWrite.All",
            "Group.Read.All",
            "Mail.ReadWrite",
            "Mail.Send",
            "Notes.Create",
            "Notes.Read",
            "Notes.ReadWrite",
            "openid",
            "People.Read",
            "profile",
            "User.Read",
            "User.Read.All",
            "User.ReadBasic.All"
        ]
    },
    "Contacts.Read": {
        "00000003-0000-0000-c000-000000000000": [
            "Calendars.Read",
            "Channel.ReadBasic.All",
            "ChannelMessage.Send",
            "Contacts.Read",
            "Directory.Read.All",
            "EduRoster.ReadBasic",
            "email",
            "Files.ReadWrite.All",
            "Group.Read.All",
            "Mail.ReadWrite",
            "Mail.Send",
            "Notes.Create",
            "Notes.Read",
            "Notes.ReadWrite",
            "openid",
            "People.Read",
            "profile",
            "User.Read",
            "User.Read.All",
            "User.ReadBasic.All"
        ]
    },
[...]
```

## getByAud

This will ask for an Aud and return all the apps and the scopes they can request on that Aud.

Example:

```bash
python3 getByAud.py

Enter the aud to search for: https://outlook.office.com
- App: d3590ed6-52b3-4102-aeff-aad2292ab01c
  - Scopes: ['Branford-Internal.ReadWrite', 'Calendars.ReadWrite', 'Calendars.ReadWrite.Shared', 'Contacts.ReadWrite', 'Contacts.ReadWrite.Shared', 'EAS.AccessAsUser.All', 'EopPolicySync.AccessAsUser.All', 'EopPsorWs.AccessAsUser.All', 'EWS.AccessAsUser.All', 'Files.ReadWrite.All', 'Files.ReadWrite.Shared', 'Group.ReadWrite.All', 'Mail.ReadWrite', 'Mail.ReadWrite.Shared', 'Mail.Send', 'Mail.Send.Shared', 'MailboxSettings.ReadWrite', 'MapiHttp.AccessAsUser.All', 'MessageReaction-Internal.Update', 'Notes.Read', 'Notes.ReadWrite', 'Oab.AccessAsUser.All', 'OutlookService.AccessAsUser.All', 'OutlookService.AccessAsUser.Sdp', 'OWA.AccessAsUser.All', 'People.Read', 'People.ReadWrite', 'Place.Read.All', 'Signals.Read', 'Signals.ReadWrite', 'SubstrateSearch-Internal.ReadWrite', 'Tags.ReadWrite', 'Tasks.ReadWrite', 'Tasks.ReadWrite.Shared', 'Todo-Internal.ReadWrite', 'User.ReadBasic', 'User.ReadBasic.All', 'user_impersonation', 'User-Internal.ReadWrite']


- App: 00b41c95-dab0-4487-9791-b9d2c32c80f2
  - Scopes: ['AdminApi.AccessAsUser.All', 'Contacts.Read', 'Contacts.ReadWrite', 'EWS.AccessAsUser.All', 'Mail.ReadWrite', 'Mail.ReadWrite.All', 'People.Read', 'People.ReadWrite', 'User.ReadWrite', 'User.ReadWrite.All']


- App: 1fec8e78-bce4-4aaf-ab1b-5451cc387264
  - Scopes: ['AdminApi.AccessAsApp', 'AdminApi.AccessAsUser.All', 'Calendar.Read.Shared', 'Calendar.ReadWrite.Shared', 'Calendars.ReadWrite', 'Collab-Internal.ReadWrite', 'Contacts.ReadWrite', 'EWS.AccessAsUser.All', 'Files.Read.All', 'Files.ReadWrite.All', 'Files.ReadWrite.Shared', 'Group.ReadWrite.All', 'Mail.ReadWrite', 'Mail.Send', 'OWA.AccessAsUser.All', 'Place.Read.All', 'Place.ReadWrite.All', 'QuietTime.ReadWrite', 'SCIS-Internal.ReadWrite', 'Signals.ReadWrite', 'SubstrateSearch-Internal.ReadWrite', 'TailoredExperiences-Internal.ReadWrite', 'TenantFeedback.Write', 'User.Read', 'User.ReadBasic.All']
[...]


{
    "d3590ed6-52b3-4102-aeff-aad2292ab01c": [
        "Branford-Internal.ReadWrite",
        "Calendars.ReadWrite",
        "Calendars.ReadWrite.Shared",
        "Contacts.ReadWrite",
        "Contacts.ReadWrite.Shared",
        "EAS.AccessAsUser.All",
        "EopPolicySync.AccessAsUser.All",
        "EopPsorWs.AccessAsUser.All",
        "EWS.AccessAsUser.All",
        "Files.ReadWrite.All",
        "Files.ReadWrite.Shared",
        "Group.ReadWrite.All",
        "Mail.ReadWrite",
        "Mail.ReadWrite.Shared",
        "Mail.Send",
        "Mail.Send.Shared",
        "MailboxSettings.ReadWrite",
        "MapiHttp.AccessAsUser.All",
        "MessageReaction-Internal.Update",
        "Notes.Read",
        "Notes.ReadWrite",
        "Oab.AccessAsUser.All",
        "OutlookService.AccessAsUser.All",
        "OutlookService.AccessAsUser.Sdp",
        "OWA.AccessAsUser.All",
        "People.Read",
        "People.ReadWrite",
        "Place.Read.All",
        "Signals.Read",
        "Signals.ReadWrite",
        "SubstrateSearch-Internal.ReadWrite",
        "Tags.ReadWrite",
        "Tasks.ReadWrite",
        "Tasks.ReadWrite.Shared",
        "Todo-Internal.ReadWrite",
        "User.ReadBasic",
        "User.ReadBasic.All",
        "user_impersonation",
        "User-Internal.ReadWrite"
    ],
    "00b41c95-dab0-4487-9791-b9d2c32c80f2": [
        "AdminApi.AccessAsUser.All",
        "Contacts.Read",
        "Contacts.ReadWrite",
        "EWS.AccessAsUser.All",
        "Mail.ReadWrite",
        "Mail.ReadWrite.All",
        "People.Read",
        "People.ReadWrite",
        "User.ReadWrite",
        "User.ReadWrite.All"
    ],
    "1fec8e78-bce4-4aaf-ab1b-5451cc387264": [
        "AdminApi.AccessAsApp",
        "AdminApi.AccessAsUser.All",
        "Calendar.Read.Shared",
        "Calendar.ReadWrite.Shared",
        "Calendars.ReadWrite",
        "Collab-Internal.ReadWrite",
        "Contacts.ReadWrite",
        "EWS.AccessAsUser.All",
        "Files.Read.All",
        "Files.ReadWrite.All",
        "Files.ReadWrite.Shared",
        "Group.ReadWrite.All",
        "Mail.ReadWrite",
        "Mail.Send",
        "OWA.AccessAsUser.All",
        "Place.Read.All",
        "Place.ReadWrite.All",
        "QuietTime.ReadWrite",
        "SCIS-Internal.ReadWrite",
        "Signals.ReadWrite",
        "SubstrateSearch-Internal.ReadWrite",
        "TailoredExperiences-Internal.ReadWrite",
        "TenantFeedback.Write",
        "User.Read",
        "User.ReadBasic.All"
    ],
[...]
```


## getByAppAndAud

This will ask for an Aud and a scope and return all the apps that can request the indicated scope on that Aud.

It'll just return a list of app IDs that can request the indicated scope on the indicated Aud as text and as json.

Example:

```bash
python3 ./getByAudAndScope.py
Enter the aud to search for: https://management.core.windows.net
Enter the scope permission to search for: user_impersonation
- 04b07795-8ddb-461a-bbee-02f9e1bf7b46
- 1950a258-227b-4e31-a9cf-717495945fc2
- d3590ed6-52b3-4102-aeff-aad2292ab01c
- c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12
- 00b41c95-dab0-4487-9791-b9d2c32c80f2
- ab9b8c07-8f02-4f72-87fa-80105867a763
- 27922004-5251-4030-b22d-91ecd9a37ea4
- 26a7ee05-5602-4d76-a7ba-eae8b7b67941
[...]



[
    "04b07795-8ddb-461a-bbee-02f9e1bf7b46",
    "1950a258-227b-4e31-a9cf-717495945fc2",
    "d3590ed6-52b3-4102-aeff-aad2292ab01c",
    "c0d2a505-13b8-4ae0-aa9e-cddd5eab0b12",
    "00b41c95-dab0-4487-9791-b9d2c32c80f2",
    "ab9b8c07-8f02-4f72-87fa-80105867a763",
    "27922004-5251-4030-b22d-91ecd9a37ea4",
    "26a7ee05-5602-4d76-a7ba-eae8b7b67941",
    "22098786-6e16-43cc-a27d-191a01a1e3b5",
[...]
```