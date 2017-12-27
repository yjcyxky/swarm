#!/usr/bin/env python3

import subprocess
import re
import json
import uuid

class JobInfo:
    """
    Get, Parse Job Stat Information
    """
    def __init__(self, jobid, timeout = 10, format = 'json', cluster_uuid = None):
        self.jobid = jobid
        self._job_stat_dict = {}
        self._job_stat_str = ''
        self._command = ['tracejob', '-n', '360', '-f', 'system', '-f', 'job',
                         '-f', 'job_usage', '-f', 'admin', '-q', '-s', '-l',
                         str(jobid)]
        self._timeout = timeout
        self._format = format
        self._cluster_uuid = cluster_uuid

    @property
    def job_info(self):
        if self._format == 'json':
            return self.parse(format = 'json')
        elif self._format == 'xml':
            return self.parse(format = 'xml')
        elif self._format == 'raw':
            return self.parse(format = 'raw')
        else:
            return self.parse(format = 'raw')

    def get_stat_info(self):
        try:
            output_bytes = subprocess.check_output(self._command,
                                                     timeout = self._timeout)
            self._job_stat_str = str(output_bytes, encoding = "utf-8")
            print("get_stat_info:%s" % self._job_stat_str)
        except subprocess.CalledProcessError as e:
            output = e.output
            code = e.returncode
        except subprocess.TimeoutExpired as e:
            output = e.output
            code = e.returncode

    def parse(self, format = 'json'):
        replace_str_pairs = [('Resource_List.nodect', 'resource_list_nodect'),
                             ('Resource_List.walltime', 'resource_list_walltime'),
                             ('Resource_List.neednodes', 'resource_list_neednodes'),
                             ('Resource_List.nodes', 'resource_list_nodes'),
                             ('Exit_status', 'exit_status'),
                             ('resources_used.cput', 'resources_used_cput'),
                             ('resources_used.mem', 'resources_used_mem'),
                             ('resources_used.vmem', 'resources_used_vmem'),
                             ('resources_used.walltime', 'resources_used_walltime'),
                             (':ppn=', ' cpus_num=')]

        def get_cpus_num(job_stat_dict):
            pass

        def nodes_num():
            pass

        def replace_str(text, replace_str_pairs):
            for item in replace_str_pairs:
                print(item)
                text = text.replace(item[0], item[1])
            return text

        if format is None:
            format = 'raw'

        def filter_empty(text):
            if text != '':
                return True
            else:
                return False

        def filter_str(text):
            RE = re.compile('^[a-zA-Z0-9\-_:/.+@]+=[a-zA-Z0-9\-_:/.+@]+$', flags=re.IGNORECASE)
            match = re.match(RE, text)
            if match is None:
                return False
            else:
                return True

        def gen_dict(job_stat, job_stat_dict):
            for item in job_stat:
                key_value_pair = item.split('=')
                # print("parse@gen_dict@key_value_pair@%s" % key_value_pair)
                if not job_stat_dict.get(key_value_pair[0]):
                    job_stat_dict.update({
                        key_value_pair[0]: key_value_pair[1]
                    })
            return job_stat_dict

        if self._job_stat_str != '' and isinstance(self._job_stat_str, str):
            job_stat_str = replace_str(self._job_stat_str, replace_str_pairs)
            print("parse@job_stat_str%s" % job_stat_str)
            job_items = tuple(filter(filter_empty, job_stat_str.split('\n')))
            job_stat_dict = {}
            # 4行：任务已结束时
            if len(job_items) == 4:
                # 第一行[Job: 70776.management_node_15]
                jobid = job_items[0].split(' ')[1]

                # 第二行[12/07/2017 11:52:02  A    queue=batch]

                # 第三行[12/07/2017 11:52:03  A    user=zhangjiyang group=zhangjiyang jobname=TNBC queue=batch ctime=1512618722 qtime=1512618722 etime=1512618722 start=1512618723 owner=zhangjiyang@management_node_15 exec_host=compute_node_1/30+compute_node_1/31+compute_node_1/32+compute_node_1/33+compute_node_1/34+compute_node_1/35+compute_node_1/36+compute_node_1/37+compute_node_1/38+compute_node_1/39 Resource_List.neednodes=compute_node_1:ppn=10 Resource_List.nodect=1 Resource_List.nodes=compute_node_1:ppn=10 Resource_List.walltime=80:00:00 ]
                # 匹配等号
                job_stat = filter(filter_str, job_items[2].split(' '))
                job_stat_dict = gen_dict(job_stat, job_stat_dict)
                job_stat_dict.update({
                    'jobid': jobid,
                    'job_uuid': str(uuid.uuid4()),
                    'cluster_uuid': self._cluster_uuid
                })

                job_stat = filter(filter_str, job_items[3].split(' '))
                job_stat_dict = gen_dict(job_stat, job_stat_dict)

            elif len(job_items) == 3:
                # 3行：刚提交的任务
                # 第一行[Job: 70776.management_node_15]
                jobid = job_items[0].split(' ')[1]

                # 第二行[12/07/2017 11:52:02  A    queue=batch]

                # 第三行[12/07/2017 11:52:03  A    user=zhangjiyang group=zhangjiyang jobname=TNBC queue=batch ctime=1512618722 qtime=1512618722 etime=1512618722 start=1512618723 owner=zhangjiyang@management_node_15 exec_host=compute_node_1/30+compute_node_1/31+compute_node_1/32+compute_node_1/33+compute_node_1/34+compute_node_1/35+compute_node_1/36+compute_node_1/37+compute_node_1/38+compute_node_1/39 Resource_List.neednodes=compute_node_1:ppn=10 Resource_List.nodect=1 Resource_List.nodes=compute_node_1:ppn=10 Resource_List.walltime=80:00:00 ]
                # 匹配等号
                job_stat = filter(filter_str, job_items[2].split(' '))
                job_stat_dict = gen_dict(job_stat, job_stat_dict)
                job_stat_dict.update({
                    'jobid': jobid,
                    'job_uuid': str(uuid.uuid4()),
                    'cluster_uuid': self._cluster_uuid
                })
            self._job_stat_dict = job_stat_dict


        if format == 'json':
            return json.dumps(self._job_stat_dict)
        elif format == 'xml':
            pass
        elif format == 'raw':
            return self._job_stat_str

def main():
    joblogs = []
    for num in range(37520, 71128):
        job = JobInfo(num)
        job.get_stat_info()
        joblogs.append(json.loads(job.parse()))

    with open('jobs.txt', 'w') as f:
        f.write(json.dumps(joblogs))

if __name__ == '__main__':
    main()
