# 功能模块说明
1. opsweb提供前端和后端数据库管理等，同时负责组合其它组件
2. ssansible提供ansible插件封装，用于软件安装与服务配置
3. sscobbler提供系统自动安装模块
4. sshostmgt提供主机管理模块，包括主机信息收集、开关机、重启等
5. ssmonitor提供主机、服务、运行状态等监控信息
6. ssnagios提供通知服务

# How to install SwarmOpsWeb
1. 安装配置Cobbler
2. 安装Ansible
3. 安装配置Ganglia
4. 安装配置Nagios
5. 部署SwarmOpsWeb

# How to reuse sscobbler app
1. You need to prepare a config.py file that contains these variables described below when you want to reuse sscobbler.
```
COBBLERD_DOMAIN: domain name or IP address of cobblerd server
COBBLER_API_URL: cobbler api url 
INTERFACE_LANG: interface language
COBBLER_USERNAME: your username to login cobblerd server
COBBLER_PASSWORD: your password to login cobblerd server
ZH_INTERFACE: language dictory in chinese
EN_INTERFACE: language dictory in english
```

2. Add this line to urls.py file of opsweb app
```
url(r'^sscobbler/', include('sscobbler.urls'))
```

3. Add sscobbler app to INSTALLED_APPS of opsweb app
```
'sscobbler'
```