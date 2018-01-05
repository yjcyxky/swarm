# 功能模块说明
1. swarm
    前端和后端数据库管理等，同时负责组合其它组件
2. ssansible
    绑定ansible(https://github.com/ansible)，用于系统软件与服务配置
3. sscobbler
    系统自动安装
4. sshostmgt
    主机管理，包括主机信息收集、开关机、重启等
5. ssfalcon
    主机、服务、运行状态等监控
6. ssganglia
    主机、软件等性能监控
6. ssnagios
    通知
7. sscobweb
    软件安装管理服务，单机版/集群版软件安装，支援advisor模块，类似于APP Store
8. sscluster
    集群任务统计监控
9. report_enging
    报告查询、管理等
10. ssadvisor
    医学数据挖掘APP运算
11. ssspider
    封装snakemake(https://bitbucket.org/snakemake/snakemake)，用于Pipeline分析

# 平台依赖环境(大部分软件均与Swarm一同安装在Swarm服务器上，若需要集群中管理节点与计算节点部署软件则会明确声明)
1. Cobbler
    必须安装在Swarm服务器
2. Ansible
    必须安装在Swarm服务器，且集群所有节点的主机IP等需要写入ansible配置文件中，ansible所用账户需提前声明
3. Ganglia
    Swarm平台所在服务器必须安装配置Ganglia-gmetad
4. Nagios
    Swarm平台所在服务器必须安装配置nagios，而集群中所有节点需配置NRPE
5. Redis
6. MySQL
7. Falcon
8. sscluster
    当前版本仅支持Torque
9. sshostmgt
    电源管理模块，仅支持Dell系列服务器
10. uberftp
    The uberftp command needs to be available for GridFTP support

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

2. Add this line to urls.py file of swarm app
```
url(r'^sscobbler/', include('sscobbler.urls'))
```

3. Add sscobbler app to INSTALLED_APPS of swarm app
```
'sscobbler'
```

# Package
1. output_templ
{
    "result_files": [
        'a',
        'ab',
        'abc',
        'abcd'
    ]
}

# 备注：
1. XRootD不支持python3，因此将其移除
