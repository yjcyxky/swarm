<!--
格式：
标题：时间
列表：TODO项目

备注：完成的TODO项则采用删除线标识，一旦当前标识版本所有TODO项均完成，则git提交后标识相应TAG
-->

# 2017年08月19日
~~1. 移除所有html文件，所有数据传输均采用JSON格式~~

~~2. swarm提供Tree API，用于前端渲染侧边栏~~

# 2018年1月2日
1. 完善User模块，使账户系统可以与单机版或集群版系统保持同步
2. 增加Custom User，使不同用户可以被配置成终端登录和Web端登录
3. 增加数据库初始化代码
4. 增加系统配置代码，使用户可以一键安装配置Swarm系统

# 2018年1月5日
1. sscobbler仅支持Python2.7，需要移植到Python3
2. 增加scheduler_api，封装slurm、Torque等集群调度软件提供Job相关的更多的操作
3. 增加ansible_api，封装ansible API 2.0提供自动化playbook Runner.
