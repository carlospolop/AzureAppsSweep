# AzureAppsSweep

**Enumerate Azure AD application permissions and identify MFA bypass opportunities.**

AzureAppsSweep tests user credentials against a comprehensive list of Azure AD applications to discover which apps can be accessed without Multi-Factor Authentication (MFA). This is crucial for identifying potential privilege escalation paths and security gaps in Azure AD environments.


For more information check:

https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-basic-information/az-tokens-and-public-applications
https://cloud.hacktricks.xyz/pentesting-cloud/azure-security/az-azuread/az-conditional-access-policies-mfa-bypass

## 🎯 Key Features

- ✅ **Dual Authentication Modes**: Username/Password and PRT (Primary Refresh Token)
- ✅ **MFA Bypass Detection**: Identifies applications accessible without MFA
- ✅ **FOCI Detection**: Discovers Family of Client IDs applications
- ✅ **Multi-threaded Scanning**: Fast concurrent processing (default 5 threads)
- ✅ **Beautiful Output**: Rich terminal UI with progress bars and color-coded results
- ✅ **Comprehensive Coverage**: Tests 400+ Azure applications across 7 resource URIs

## 📋 Table of Contents

- [Installation](#installation)
- [Authentication Methods](#authentication-methods)
  - [Username/Password](#usernamepassword-authentication)
  - [PRT (Primary Refresh Token)](#prt-authentication)
- [Usage Examples](#usage-examples)
- [Command-Line Options](#command-line-options)


## 🚀 Installation

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/yourusername/AzureAppsSweep.git
cd AzureAppsSweep

# Install required packages
pip install -r requirements.txt
```

## 🔐 Authentication Methods

AzureAppsSweep supports two authentication methods:

### Username/Password Authentication

Traditional credential-based authentication using the Resource Owner Password Credentials (ROPC) flow.

**When to use:**
- You have valid username and password credentials
- Testing password-based authentication flows
- Standard penetration testing scenarios

**Example:**
```bash
python AzureAppsSweep.py --username user@company.com --password P@ssw0rd! --outfile tokens.txt
```

### PRT Authentication

Primary Refresh Token authentication for advanced scenarios where you've extracted a PRT from a compromised device.

**When to use:**
- You've extracted a PRT from a Windows 10/11 Azure AD-joined device
- Testing device-based authentication flows
- Red team operations with device compromise
- Passwordless authentication scenarios

**PRT Format Support:**
- Raw PRT string
- Base64-encoded PRT
- JSON format with PRT and session key (roadtx).
- PRT file input

## 📖 Usage Examples

### Basic App Sweep (Username/Password)

Scan all applications with username and password:

```bash
python AzureAppsSweep.py --username user@company.com --password P@ssw0rd! --outfile tokens.txt
```

### Basic App Sweep (PRT)

Scan all applications with PRT:

```bash
python AzureAppsSweep.py --prt "eyJ0eXAiOiJKV1Qi..." --tenant company.com --outfile tokens.txt
```

### Multi-threaded Fast Scan

Use more threads for faster scanning:

```bash
python AzureAppsSweep.py --username user@company.com --password P@ssw0rd! --outfile tokens.txt --threads 10
```

### Show Detailed Errors

Display full error descriptions for troubleshooting:

```bash
python AzureAppsSweep.py --prt-file prt.json --tenant company.com --outfile tokens.txt --print-errors
```

### FOCI Apps Detection

Discover which applications support Family of Client IDs (useful for token reuse):

```bash
# With username/password
python AzureAppsSweep.py --get-foci-apps --username user@company.com --password P@ssw0rd! --outfile foci.txt

# With PRT
python AzureAppsSweep.py --get-foci-apps --prt-file prt.json --tenant company.com --outfile foci.txt
```

## ⚙️ Command-Line Options

### Required Arguments

| Argument | Description |
|----------|-------------|
| `--outfile FILE` | Output file path to write acquired tokens |

### Authentication Arguments (Choose One)

**Username/Password:**
| Argument | Description |
|----------|-------------|
| `--username EMAIL` | Username/email for authentication |
| `--password PASS` | Password for authentication |

**PRT:**
| Argument | Description |
|----------|-------------|
| `--prt TOKEN` | Primary Refresh Token (base64, JSON, or raw) |
| `--prt-file FILE` | File containing PRT |
| `--session-key KEY` | Optional session key for PRT authentication |
| `--tenant DOMAIN` | Tenant domain or ID (required for PRT) |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--threads N` | Number of concurrent threads | 5 |
| `--print-errors` | Print detailed error descriptions | False |
| `--get-foci-apps` | FOCI detection mode (no app sweep) | False |
| `--verbose` | Enable verbose roadtx output | False |
