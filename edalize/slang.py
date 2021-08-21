# Copyright edalize contributors
# Licensed under the 2-Clause BSD License, see LICENSE for details.
# SPDX-License-Identifier: BSD-2-Clause

import os
import re
import logging

from edalize.edatool import Edatool

logger = logging.getLogger(__name__)


class Slang(Edatool):

    _description = """Slang System Verilog Frontend
slang is a software library that provides various
components for lexing, parsing, type checking, and elaborating SystemVerilog code.

Example snippet of a CAPI2 description file for Slang:

.. code:: yaml

    slang:
      mode:
        - lint # this will lint all the files
        - preprocess # this will preprocess all the files and output a single file
      extra_options:
        user defined options

    """

    tool_options = {
        'lists' : {
            'mode': 'String',
            'extra_options': 'String'
        }
    }

    argtypes = ['vlogdefine']

    flags = []

    def __init(self, edam=None, work_root=None, eda_api=None):
        # call the super method here
        super(Slang, self).__init__(edam, work_root, eda_api)
        
        self.rtl_paths = None
        self.incdirs = None

        # path for final rtl generation
        self.gen_rtl_name = None

        # contain the command line arguments
        self.flags = []
        return 0

    @staticmethod
    def get_doc(api_ver):
        if api_ver == 0:
            return {
                'description':
                'slang is a software library that provides various components for lexing, parsing, type checking, and elaborating SystemVerilog code.',
                'lists': [
                    {
                        'name': 'mode',
                        'type': 'String',
                        'desc': ("choose slang to run in either lint mode or preprocess mode")
                    },
                    {
                        'name': 'extra_options',
                        'type': 'String',
                        'desc': ("extra options for slang")
                    }
                ]
            }

    # we only need to get the list of files
    def _get_file_names(self):
        '''
        get all the file names
        '''
        src_files, self.incdirs = self._get_fileset_files()

        ft_re = re.compile(r'(:?systemV|v)erilogSource')
        for file_obj in src_files:
            if ft_re.match(file_obj.file_type):
                self.flags.append(file_obj.name)

    def _get_run_mode_flags(self):
        '''
        get the current running mode: whether run to preprocess or lint
        '''
        run_mode = self.tool_options.get('mode', '')
        if run_mode == "lint":
            self.flags += ["--lint-only"]
        elif run_mode == "preprocess" :
            self.flags += ["--preprocess"]


    def _get_define_flags(self) -> str:
        '''
        understand flags necessary for various defines
        '''
        for key, value in self.vlogdefine.items():
            self.flags.append(' -D {}={} '.format(key, self._param_value_str(value)))

    def _get_extra_options(self):
        '''
        get extra options from user
        '''
        extra_options = self.tool_options.get('extra_options', "")
        self.flags += extra_options.split()

    def _get_top_flags(self):
        '''
        generate flags for top level module
        '''
        if self.toplevel != "":
            self.flags.append(" --top {} ".format(self.toplevel))
    
    def build_main(self):
        return

    def configure_main(self):
        return

    def run_main(self):
        self._get_top_flags()
        self._get_define_flags()
        self._get_run_mode_flags()
        self._get_file_names()
        self._get_extra_options()
        self._run_tool("slang" ,self.flags)
        