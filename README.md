# Swarm平台简介
Swarm平台包含三个大的子系统：Spider(Pipeline分析系统)、vHPC(集群监控运维系统)、Gemstone(服务器配置管理系统)、Advisor(报告生成、数据挖掘APP)
## 公用模块
- swarm模块
    前端和后端数据库管理等，同时负责组合其它组件
- account模块
    用户管理与权限认证

## Spider子系统
- sspider
    Pipeline分析系统，支援DAG定义与运算

## Gemstone子系统
- ssansible(此模块已经独立开发，参考**Gemstone系统**)
    自定义方案：绑定ansible(https://github.com/ansible)，用于系统软件与服务配置
- gemstone
    集成ansible

## vHPC子系统
- sscobbler
    系统自动安装
- sshostmgt
    主机管理，包括主机信息收集、开关机、重启等
- ssfalcon(暂未集成，列入TODO列表)
    主机、服务、运行状态等监控
- ssganglia
    主机、软件等性能监控
- ssnagios
    主机与服务告警通知
- sscobweb
    软件安装管理服务，单机版/集群版软件安装，支援advisor模块，类似于APP Store
- sscluster
    集群任务统计监控

## Advisor子系统
- report_enging
    报告查询、管理等
- ssadvisor
    医学数据挖掘APP运算


# 平台依赖环境
(大部分软件均与Swarm一同安装在Swarm服务器上，若需要集群中管理节点与计算节点部署软件则会明确声明)
支持Python3.5，暂不支持Python3.6、2.7、2.6等
## 服务器架构说明
- Swarm服务器(用于部署Swarm服务，若需要部署Spider模块，则Swarm服务器应该具备任务提交功能，即应该安装集群调度软件但其本身不参与计算)
- HPC集群(最好包括存储节点、计算节点、登录节点)

## 依赖软件
- Cobbler
    必须安装在Swarm服务器，用于支持操作系统自动安装
- Ansible
    必须安装在Swarm服务器
- Ganglia
    Swarm平台所在服务器必须安装配置Ganglia-gmetad，且所有需要监控的HPC节点均需正确配置Ganglia；
    Swarm通过解析指定位置的rrd文件获取监控信息；
- Nagios
    Swarm服务器上必须安装配置nagios，而集群中所有节点需配置NRPE和相关通知项；
    Swarm服务器上必须安装NDOUtils
- Redis
- MySQL
    Swarm平台采用MySQL作为后端存储
- Falcon
    暂时不需要安装
- Torque+Maui(用于sscluster)
    集群调度软件，同时为sscluster提供调度日志信息，当前版本sscluster仅支持Torque
- IPMITool与相关库
    用于支援sshostmgt，当前sshostmgt仅支持Dell系列服务器(包含DELL DRAC模块的服务器)
    使用sshostmgt控制服务器前需要配置IPMI，包括IP地址、账号与密码
- uberftp
    若需要Spider支援GridFTP，则需要安装GridFTP客户端
- rrdtool和rrdtool-devel
    支持RRD解析，为ssganglia模块提供数据解析支持

## 依赖Python库
详见requirements.txt文件


# Swarm配置
1. 所有终端程序支持配置文件+命令行参数两种配置方式(命令行参数优先于配置文件)
    配置文件的配置经由cli.py<from configuration import conf as settings>导入
2. 所有webserver模块支持配置文件+数据库两种配置方式(数据库配置优先于配置文件、**数据库配置为动态生效**)
    - 配置文件的配置经由cli.py<from configuration import conf as settings>导入
    - 数据库配置则通过相应APP的Setting Model来获取


# ssspider
1. 提交的所有spider workflow，均记录相应pid至数据库中(即使重启Web服务之后，仍可追踪提交的任务是否已经完成)
2. 提交的spider workflow实例均维护在队列中，方便随时查询操作workflow
备注：队列是非永久存储，因此swarm进程退出后队列则被销毁且提交的Job亦中断，因此需要保存足够多的信息在数据库，方便重启Workflow
3. 将spider开发成一个独立的基于RPC的Daemon，Swarm通过ssspider与Spider Daemon连接将DAG Pipeline发送给Spider Daemon


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

# DEBUG
- XRootD不支持python3，因此将其移除
