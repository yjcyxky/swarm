import sys, os
from os import path

sys.path.append(path.dirname(path.dirname(os.getcwd())))

import unittest
from cobweb.models.tasks import CeleryTask
from cobweb import app

class TestCeleryTask(unittest.TestCase):
    '''
    Test CeleryTask Class
    '''
    def test_add_task(self):
        task = CeleryTask('install_samtools_0.1.16', 'install-package', 'logs',
                          task_templ = None,
                          task_summary = "测试")
        task_kwargs = {'pkg_name': 'samtools', 'version': '0.1.16'}
        error, msg, response = task.add_task(**task_kwargs)
        app.logger.error("%s: %s" % (msg, str(response)))
        self.assertEqual(True, error)

    def test_get_status(self):
        pass

if __name__ == '__main__':
    unittest.main()
