#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Wu Yi-Chiao (Nagoya University)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

"""VC subjective evaluation

Usage: run_test.py [-h] [-o MODE] EVALNAME

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
from src.user.info_class import UserInfo
from src.bin.eval_io import main_XAB, main_PK, main_MOS, main_SIM
from src.bin.eval_io import playspeech, introduction, xlsx_SCORE, xlsx_SIM
from src.utils.dict_filter import tpair_filter

def evaluation(eval_dict, test_type, text):
    """RUN EVALUATIONS
    Args:
        eval_dict (list of dict): the result list of dicts of the test
        test_type (str): the type of the test
        text (dict): the dictionary of constant text
    Return:
        ans : 'q' for quit, float or int values for scores
    """
    ans = 'initial'
    r_idx = -len(eval_dict)
    for d_idx in np.random.permutation(len(eval_dict)):
        if test_type == 'PK':
            ans = main_PK(eval_dict[d_idx], r_idx, text)
        elif test_type == 'SIM':
            ans = main_SIM(eval_dict[d_idx], r_idx, text)
        elif test_type == 'MOS':
            ans = main_MOS(eval_dict[d_idx], r_idx, text)
        elif test_type == 'XAB':
            ans = main_XAB(eval_dict[d_idx], r_idx, text)
        else:
            print("test type %s is not in (MOS, SIM, PK, XAB)!"%(test_type))
            sys.exit(0)
        r_idx += 1
        if ans == 'q':
            print("Quit evaluation...")
            return ans
    return ans

# OUTPUT RESULTS
def output_results(total_dict, test_type, test_system, 
                   user_name, eval_name, result_path, 
                   text, test_pairs):
    """OUTPUT SUBJECTIVE RESULTS to a EXCEL FILE
    Args:
        total_dict (list of dict): the result dicts
        test_type (str): the type of the test [SIM, XAB, PK, MOS]
        test_system (list): the list of systems corresponding to the test type
        user_name (str): the name of the listener
        eval_name (str): the name of the evaluation
        result_path (str): the path to output result .xlsx file
        text (dict): the dictionary of constant text
        test_pairs (list): the list of the output conditions 
    """
    
    fxlsx = "%s%s_%s.xlsx" % (result_path, eval_name, test_type)
    if test_type == 'PK' or test_type == 'MOS' or test_type == 'XAB':
        c_xlsx = xlsx_SCORE(user_name, fxlsx, test_pairs, test_system)
    elif test_type == 'SIM':
        c_xlsx = xlsx_SIM(user_name, fxlsx, test_pairs, test_system, text)        
    else:
        print("test type %s is not in (MOS, SIM, PK, XAB)!" % (test_type))
        sys.exit(0)
    # output results
    for t_pair in test_pairs:
        t_dict = tpair_filter(t_pair, total_dict)
        c_xlsx.output_xlsx(t_pair, t_dict)

def main(eval_name, yml_path, results_path, test_pair):
    print("\n##############################################################\n" +
          "#"+("%s Subjective Test" % eval_name).center(60) + "#\n" +
          "##############################################################\n")
    #LOAD CONSTANT TEXT
    c_textf = '%stext.yml'%(yml_path)
    if not os.path.exists(c_textf):
        print("%s doesn't exist!" % c_textf)
        sys.exit(0)
    with open(c_textf, 'r', encoding='utf-8') as yf:
        constant_text = yaml.safe_load(yf)
    text     = constant_text['text']
    c_text   = constant_text['c_text']
    examples = constant_text['examples']
    #GET USER INFORMATION
    user = UserInfo(yml_path, c_text)
    while user.flag:
        user_name = input("Please enter your name or 'q' to quit: ")
        while user_name == "": # empty input, ask user inputs again
            user_name = input("Please enter your name or 'q' to quit: ")
        if user_name == 'q': # quit
            print('Quit evaluation.')
            return
        # progess check
        if user.check_user(user_name): # load and check the progress of the user
            action = input("The user name already exists !!" +
                           "please enter any key to change the name, " +
                           "or enter 'q' to quit")
            if action == 'q':
                print('Quit evaluation.')
                return
    #EVALUATION
    for t_idx in user.t_idxs:
        if user.finished[t_idx]:
            print("PART %d is already finished!\n" % (t_idx))
        else:
            print("\n--------------------------------------------------------------")
            print("-" + ("PART %d: %s Test" %
                         (t_idx, user.test_type[t_idx])).center(60) + "-")
            print("--------------------------------------------------------------")
            print("PART %d Progress: %d/%d\n" %
                  (t_idx, len(user.total_dict[t_idx]) - len(user.eval_dict[t_idx]),
                   len(user.total_dict[t_idx])))
            if user.initial[t_idx]:
                introduction(user.test_type[t_idx], text, examples)
            input("Press any key to start the evaluations!\n")
            action = evaluation(user.eval_dict[t_idx], user.test_type[t_idx], text)
            user.save_result(t_idx)
            if user.finished[t_idx]:
                output_results(user.total_dict[t_idx], user.test_type[t_idx],
                               user.test_system[t_idx], user_name, 
                               eval_name, results_path,
                               text, test_pair)
            if action == 'q':
                return
        if t_idx != user.t_idxs[-1]:
            action = input("Press any key to start the next PART or 'q' to quit!")
            if action == 'q':
                return
    print("All PARTs are completed. Thank you!!")

# MAIN
if __name__ == "__main__":
    args = docopt(__doc__)  # pylint: disable=invalid-name
    eval_name   = args['EVALNAME']
    yml_path    = "yml/%s/" % eval_name
    result_path = "results/"
    if args['-o'] == 'vc': # voice conversion mode
        test_pair = ['summary', 'xgender', 'sgender', 'F-F', 'F-M', 'M-F', 'M-M']
        vc_flag = True
    elif args['-o'] == 'as': # anasis-synthesis mode
        test_pair = ['summary', 'female', 'male']
    else: # basic mode
        test_pair = ['summary']
    main(eval_name, yml_path, result_path, test_pair)

    
    



