# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>


class BaseScheduler:
    def __init__(self):
        pass

    def get_host(self, jobid):
        """
        Get host name of the host where the current job located
        """
        pass

    def list_all_jobs(self):
        """
        List all jobs that was submitted to current cluster.
        """
        pass

    def show_job_info(self, jobid):
        pass

    def kill_job(self, jobid):
        pass

    def force_kill_job(self, jobid):
        pass
