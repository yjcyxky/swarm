# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import os
import sys

# 必须将spider添加到sys.path中
SPIDER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SPIDER_DIR)
