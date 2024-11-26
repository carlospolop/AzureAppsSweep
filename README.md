# AzureAppsSweep

This script get some user credentials and check if it can login in some applications.

This is useful to see if you **aren't required MFA to login in some applications** that you might later abuse to **escalate pvivileges**.

For more infromation check:

- https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-basic-information/az-tokens-and-public-applications
- https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-azuread/az-conditional-access-policies-mfa-bypass

## Usage

```bash
python3 AzureAppsSweep.py --username <email> --password <password> [--print-errors]
```