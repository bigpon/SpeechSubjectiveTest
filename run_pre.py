#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Wu Yi-Chiao (Nagoya University)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""VCSS subjective evaluation pre processing

Usage: run_pre.py [-h] EVALNAME

Options:
    -h, --help     Show the help
    EVALNAME       The name of the evaluation

"""
import os
import sys
import yaml
import numpy as np
from docopt import docopt
from src.user.info_class import ParserConf

# MAIN
if __name__ == "__main__":
    args = docopt(__doc__)
    # print(args)
    # PATH INITIALIZATION
    eval_name     = args['EVALNAME']
    yml_path      = "yml/%s/" % eval_name
    data_path     = "data/%s/" % eval_name
    template_path = "yml/template/"
    #LOAD CONSTANT TEXT
    c_textf = '%stext.yml'%(yml_path)
    if not os.path.exists(c_textf):
        print("%s doesn't exist!" % c_textf)
        sys.exit(0)
    with open(c_textf, 'r', encoding='utf-8') as yf:
        constant_text = yaml.safe_load(yf)
    text     = constant_text['text']
    c_text   = constant_text['c_text']
    # PARSE SUBSET .yml
    t_parser = ParserConf(data_path, template_path, yml_path, c_text)
    t_parser.subset_gen()
    
    
        
    