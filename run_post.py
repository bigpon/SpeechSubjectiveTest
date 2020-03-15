#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Wu Yi-Chiao (Nagoya University)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""VCSS subjective evaluation

Usage: run_post.py [-h] [-o MODE] EVALNAME

Options:
    -h, --help  Show the help
    -o, MODE    The output mode choice:["vc", "as", and others]
    EVALNAME    The name of the evaluation

"""
import os
import sys
import numpy as np
import yaml
from docopt import docopt
from src.user.info_class import UserResult
from src.bin.eval_statistic import xlsx_fSCORE, StatisticResult
from src.utils.dict_filter import tpair_filter

CONFIDENCE = 0.95

# FINAL OUTPUT TEMPLATE CLASS
class final_output(object):
    
    def __init__(self, test_systems, 
                 test_type, test_pairs, 
                 fxlsx, conf_user,
                 yml_path, c_text,
                 confidence=0.95):
        """CLASS TO OUTPUT THE FINAL RESULT INTO XLSX
        Args:
            test_systems (list): the list of test systems
            test_type (str): the type of the subjective test
                ['MOS', 'XAB', 'SIM', 'PK']
            test_pairs (list): the list of test pair
                ['summary', 'female', 'male', 'xgender', 'sgender', 
                 'F-F', 'F-M', 'M-F', 'M-M']
            fxlsx (str): the file name of the xslx file
            conf_user (dict): the config file of the information of all users
            yml_path (str): the path of the .yml files
            c_text (dixt): the dict of config text
            confidence (float): the confidence value of the confidence interval
        """
        self.c_xlsx        = xlsx_fSCORE(fxlsx, test_pairs, test_systems, c_text)
        self.t_systems     = test_systems
        self.t_pairs       = test_pairs
        self.t_type        = test_type
        self.yml_path      = yml_path
        self.c_text        = c_text
        self.confidence    = confidence
        self.user_results  = []
        self._load_user_result(conf_user[c_text['user_name']], 
                               conf_user[c_text['t_subset']])
        self.stat = {}
        for t_pair in self.t_pairs:
            self.stat = {**self.stat, t_pair:StatisticResult(self.c_xlsx, t_pair)}
    
    def output_result(self):
        """OUTPUT FINAL SUBJECTIVE RESULTS:
                Output each user's result and the total result
        """
        self.total_results = []
        # output result of each user
        for user_result in self.user_results:
            if user_result.finished:
                t_name = user_result.name
                for t_pair in self.t_pairs:
                    t_dict = tpair_filter(t_pair, user_result.recordf_user)
                    self.c_xlsx.output_result(t_name, t_pair, t_dict)
            else:
                print("%s didn't finish all tests." % user_result.name)
        # output total result
        if self.t_type == 'MOS': # utterance-based score
            scores = self.c_xlsx.utt_score
        elif self.t_systems == 'SIM':
            raise NotImplementedError()
        else: # user-based score
            scores = self.c_xlsx.user_score
        for t_system in self.t_systems:
            for t_pair in self.t_pairs:
                self.stat[t_pair].push_result(scores[t_pair][t_system], self.confidence)
        for t_pair in self.t_pairs:
            self.stat[t_pair].output_result()
    
    def _load_user_result(self, user_names, user_sets):
        for user_name, user_set in zip(user_names, user_sets):
            self.user_results.append(UserResult(user_name, user_set, 
                                                self.t_type, self.yml_path, 
                                                self.c_text))

def main(eval_name, yml_path, results_path, test_pair, confidence):
    #LOAD CONSTANT TEXT
    c_textf = '%stext.yml'%(yml_path)
    if not os.path.exists(c_textf):
        print("%s doesn't exist!" % c_textf)
        sys.exit(0)
    with open(c_textf, 'r', encoding='utf-8') as yf:
        constant_text = yaml.safe_load(yf)
    c_text   = constant_text['c_text']
    #LOAD EXPERIMENTAL INFO
    # fconf_user: the config file of the information of all users
    # conf_user (dict): 
    #     MAX_count: the total number of the testing subsets
    #     Subject_name: the list of users
    #     Subject_set: the corresponding subset index of each user
    #     count: the index of the current subset
    #     time: last updated time
    fconf_user = "%s%s.yml" % (yml_path, c_text['recordf'])
    if not os.path.exists(fconf_user):
        print("%s doesn't exist!"%fconf_user)
        sys.exit(0)
    with open(fconf_user, "r", encoding='utf-8') as yf:
        conf_user = yaml.safe_load(yf)
    # fconf: the config file of all evaluations information
    # conf (list of dict):
    #     method: evaluated methods
    #     set: the name of each subset
    #     type: the type of the test (MOS, SIM, XAB, PK)
    fconf = "%s%s.yml"%(yml_path, c_text['configf'])
    if not os.path.exists(fconf):
        print("%s doesn't exist!"%fconf)
        sys.exit(0)
    with open(fconf, "r", encoding='utf-8') as yf:
        conf = yaml.safe_load(yf)
    
    for tconf in conf:
        if tconf[c_text['t_type']] == 'MOS':
            mos_systems = tconf[c_text['system']]
            mos_fxlsx = "%s%s_final_MOS.xlsx" % (results_path, eval_name)
            f_output = final_output(mos_systems, 
                                    'MOS', test_pair, 
                                    mos_fxlsx, conf_user,
                                    yml_path, c_text,
                                    confidence)
        elif tconf[c_text['t_type']] == 'XAB':
            xab_systems = tconf[c_text['system']]
            xab_fxlsx = "%s%s_final_XAB.xlsx" % (results_path, eval_name)
            f_output = final_output(xab_systems, 
                                    'XAB', test_pair, 
                                    xab_fxlsx, conf_user,
                                    yml_path, c_text,
                                    confidence)
        elif tconf[c_text['t_type']] == 'SIM':
            sim_systems = tconf[c_text['system']]
            sim_fxlsx = "%s%s_final_SIM.xlsx" % (results_path, eval_name)
            f_output = final_output(sim_systems, 
                                    'SIM', test_pair, 
                                    sim_fxlsx, conf_user,
                                    yml_path, c_text,
                                    confidence)
        elif tconf[c_text['t_type']] == 'PK':
            pk_systems = tconf[c_text['system']]
            pk_fxlsx = "%s%s_final_PK.xlsx" % (results_path, eval_name)
            f_output = final_output(pk_systems, 
                                    'PK', test_pair, 
                                    pk_fxlsx, conf_user,
                                    yml_path, c_text,
                                    confidence)
        else:
            print("type %s is not defined!" % tconf[c_text['t_type']])
            return 0

        f_output.output_result()

# MAIN
if __name__ == "__main__":
    args = docopt(__doc__)  # pylint: disable=invalid-name
    eval_name   = args['EVALNAME']
    yml_path    = "yml/%s/" % eval_name
    result_path = "results/"
    if args['-o'] == 'vc':
        test_pair = ['summary', 'xgender', 'sgender', 'F-F', 'F-M', 'M-F', 'M-M']
    elif args['-o'] == 'as':
        test_pair = ['summary', 'female', 'male']
    else:
        test_pair = ['summary']
    main(eval_name, yml_path, result_path, test_pair, CONFIDENCE)

    
    



