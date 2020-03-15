#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Wu Yi-Chiao (Nagoya University)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import sys

def tpair_filter(t_pair, t_dict):
    """FILTER DICTIONARY
        Args:
            t_pair (str): the filter condition
            t_dict (dict): the test dictionary
        """
    if t_pair == 'summary':
        return t_dict
    elif t_pair == 'female':
        return list(filter(lambda item: item['gender'] == 'F', t_dict))
    elif t_pair == 'male':
        return list(filter(lambda item: item['gender'] == 'M', t_dict))
    elif t_pair == 'xgender': # cross gender
        vc_dict = list(filter(lambda item: item['conversion'], t_dict))
        return list(filter(lambda item: item['xgender'], vc_dict))
    elif t_pair == 'sgender': # same gender
        vc_dict = list(filter(lambda item: item['conversion'], t_dict))
        return list(filter(lambda item: item['xgender'] == False, vc_dict))
    elif t_pair in ['F-F', 'F-M', 'M-F', 'M-M']: # gender pair
        vc_dict = list(filter(lambda item: item['conversion'], t_dict))
        return list(filter(lambda item: item['pair'] == t_pair, vc_dict))
    else:
        print("(tpair_filter) pair %s is not defined!" % t_pair)
        sys.exit(0)