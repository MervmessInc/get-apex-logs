# getApexLog.py

Simple Python script to download Salesforce Apex Logs. The script will download all log files created TODAY larger than a set size in bytes (LOG_LENGTH).

## Setup

Create a .env file

```
$> touch .env
```

Edit .env file add 3 lines

```
SALESFORCE_INSTANCE=<Salesforce instance>
SALESFORCE_TOKEN=<Bearer Token>
LOG_LENGTH=10000
```

To get the Salesforce Instance & Bearer Token run the following command

```
$> sf org display user
```

```
Warning: This command exposes sensitive information that allows for subsequent activity using your current authenticated session.
Sharing this information is equivalent to logging someone in under the current credential, resulting in unintended
access and escalation of privilege.
For additional information, review the authorization section of
the https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_auth_web_flow.htm

User Description
┌──────────────┬──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ Key          │ Label                                                                                                            │
├──────────────┼──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Username     │ <Salesforce Username>                                                                                            │
│ Profile Name │ System Administrator                                                                                             │
│ Id           │ 005UE0000041ZJBYA2                                                                                               │
│ Org Id       │ 00DUE000000gp2x2AA                                                                                               │
│ Access Token │ <Bearer Token>                                                                                                   │
│ Instance Url │ <Salesforce instance>                                                                                            │
│ Login Url    │ <Login Url>                                                                                                      │
│ Alias        │ <Target Org Alias>                                                                                               │
└──────────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

-   Copy the Access Token into the .env file **_SALESFORCE_TOKEN_**
-   Copy the Instance Url everything after https:// into the .env file **_SALESFORCE_INSTANCE_**

Note, the Bearer Token will expire after about 1 hour of inactivity and will have to be renewed.
