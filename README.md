# How to install SSCOPWeb and Cobbler


# How to reuse sscobbler app
1. You need to prepare a sscop_config.py file that contains these variables described below when you want to reuse sscobbler.
```
COBBLERD_DOMAIN: domain name or IP address of cobblerd server
COBBLER_API_URL: cobbler api url 
INTERFACE_LANG: interface language
COBBLER_USERNAME: your username to login cobblerd server
COBBLER_PASSWORD: your password to login cobblerd server
ZH_INTERFACE: language dictory in chinese
EN_INTERFACE: language dictory in english
```

2. Add this line to urls.py file of ssdeploy app
```
url(r'^sscobbler/', include('sscobbler.urls'))
```

3. Add sscobbler app to INSTALLED_APPS of ssdeploy app
```
'sscobbler'
```