# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import sys, os
# for import dracclinet
SSHOSTMGT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SSHOSTMGT_DIR)

# stores configuration and provides introspection
default_app_config = 'sshostmgt.apps.SshostmgtConfig'
