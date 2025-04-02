# AzureAppsSweep

This script get some user credentials and check if it can login in some applications.

This is useful to see if you **aren't required MFA to login in some applications** that you might later abuse to **escalate pvivileges**.

For more information check:

- https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-basic-information/az-tokens-and-public-applications
- https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-azuread/az-conditional-access-policies-mfa-bypass

## Usage

```bash
# Do an app sweep
python3 AzureAppsSweep.py --username <email> --password <password> [--threads 5] [--print-errors]

# Use --get-foci-apps to get a list of applications that are FOCI (but not do an app sweep).
## Useful to improve the FOCI list from time to time (use it if you know what you are doing).
python3 AzureAppsSweep.py --get-foci-apps --username <email> --password <password> [--threads 5]
```