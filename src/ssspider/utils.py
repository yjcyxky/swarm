# -*- coding: utf-8 -*-

# -----------------------------------------------------------
#  Copyright (C) 2017 Nordata.
#  Website: nordata.com.cn
#
#  Swarm platform is developed by the Nordata company.
#  See the license for more details.
#  Author: Jingcheng Yang <yjcyxky@163.com>

import jinja2
import os
from configparser import (ConfigParser, NoSectionError)
from jinja2 import (TemplateSyntaxError, TemplateAssertionError, meta)
from ssspider.exceptions import (SpiderVarsConfigError, SpiderTemplateNotFound)
from ssspider.exceptions import (SpiderVarsFileNotFound, SpiderDirError)


class Template:
    def __init__(self, templ_path):
        self._templ_path = templ_path
        path = os.path.dirname(os.path.abspath(templ_path))
        self._env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(path or './')
        )

    def render_template(self, **kwargs):
        path, filename = os.path.split(self._templ_path)
        return self._env.get_template(filename).render(**kwargs)

    def get_undeclared_variables(self):
        templ_source = self._env.loader.get_source(self._env, self._templ_path)
        ast = self._env.parse(templ_source)
        undeclared_vars = meta.find_undeclared_variables(ast)
        return undeclared_vars

class Config:
    def __init__(self, config_path):
        self._config_path = config_path
        self._cf = ConfigParser()
        self._cf.read(self._config_path)

    def get_section(self, section_name):
        try:
            return self._cf.items(section_name)
        except NoSectionError:
            raise SpiderVarsConfigError("The Config file %s doesn't contain %s section" % (self._config_path, section_name))

    def get_variables(self, undeclared_vars):
        vars = dict()
        for var_section in undeclared_vars:
            vars[var_section] = dict(self.get_section(var_section))
        return vars

def gen_spider_file(templ_path, vars_file_path, output_dir = '.'):
    if not os.path.isfile(templ_path):
        raise SpiderTemplateNotFound('No Such Template File %s' % templ_path)

    if not os.path.isfile(vars_file_path):
        raise SpiderVarsFileNotFound('No Such Variable File %s' % vars_file_path)

    if not os.path.isdir(output_dir):
        self._mkdir_p(self._output_dir)

    try:
        templ = Template(templ_path)
        undeclared_vars = templ.get_undeclared_variables()

        config = Config(vars_file_path)
        vars = config.get_variables(undeclared_vars)

        # vars以section_name为键，因此必须使用**
        spider_templ = templ.render_template(**vars)

        spider_file_path = os.path.join(output_dir, 'Spiderfile')
        # 不存在Spiderfile
        if os.path.isfile(spider_file_path):
            raise SpiderDirError("A Spiderfile Exists in the %s Directory." % output_dir)

        with open(spider_file_path, 'w') as f:
            f.write(spider_templ)
        os.chmod(spider_file_path, 0o700)
    except (TemplateSyntaxError, TemplateAssertionError) as e:
        self._logger.error('Exist a problem with the template: %s' % str(e))
        raise JobTemplateError('Template Error.')
    return spider_file_path
