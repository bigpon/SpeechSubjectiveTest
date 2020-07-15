#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2020 Wu Yi-Chiao (Nagoya University)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import os
import sys
import yaml
import copy
import fnmatch
import datetime
import numpy as np

class ConfigInfo(object):
    def __init__(self, yml_path, c_text):
        self.flag      = True
        self.yml_path  = yml_path # file path of yml format config file
        self.c_text    = c_text # dictionary of text
        conf_user, self.fconf_user = self._load_record()
        self.conf, self.fconf = self._load_config()
        # check the number of sub set
        n_subset = conf_user[c_text['n_subset']]
        for t_idx in range(len(self.conf)):
            n_setlist = len(self.conf[t_idx][c_text['t_set']])
            if n_setlist != n_subset:
                print('The number of sub set lists of "%s(%d)" is not same as %s in %s.yml(%d) !!' \
                      % (self.conf[t_idx][c_text['t_type']], n_setlist, 
                         c_text['n_subset'], c_text['recordf'], n_subset))
                sys.exit(0)
        self.n_subset = n_subset
        
    def _check_file_exist(self, filename):
        if not os.path.exists(filename):
            print("%s doesn't exist!"%filename)
            return False
        return True
    
    def _yaml_dump(self, filename, data, encoding='utf-8'):
        with open(filename, "w", encoding=encoding) as yf:
            yaml.safe_dump(data, yf)
    
    def _yaml_load(self, filename, encoding='utf-8'):
        if not os.path.exists(filename):
            print("%s doesn't exist!" % filename)
            sys.exit(0)
        with open(filename, "r", encoding=encoding) as yf:
            return yaml.safe_load(yf)
    
    def _load_record(self):
        # fconf_user: the config file of the information of all users
        # conf_user (dict): 
        #     MAX_count: the total number of the testing subsets
        #     Subject_name: the list of users
        #     Subject_set: the corresponding subset index of each user
        #     count: the index of the current subset
        #     time: last updated time
        fconf_user = "%s%s.yml" % (self.yml_path, self.c_text['recordf'])
        if not self._check_file_exist(fconf_user):
            sys.exit(0)
        conf_user = self._yaml_load(fconf_user)
        return conf_user, fconf_user

    def _load_config(self):
        # fconf: the config file of all evaluations information
        # conf (list of dict):
        #     method: evaluated methods
        #     set: the name of each subset
        #     type: the type of the test (MOS, SIM, XAB, PK)
        fconf = "%s%s.yml"%(self.yml_path, self.c_text['configf'])
        if not self._check_file_exist(fconf):
            sys.exit(0)
        conf = self._yaml_load(fconf)
        return conf, fconf

class ParserConf(ConfigInfo):
    """
        Class to parse config files
    """
    def __init__(self, data_path, template_path, yml_path, c_text):
        super().__init__(yml_path, c_text)
        self.data_path = data_path
        self.template_path = template_path
        self.t_info = self._load_sysinfo()
    
    def _get_spkidx(self, t_path, spk):
        for idx, item in enumerate(t_path):
            if spk == item:
                break
        if idx == 0:
            print('The path format of %s or %s is wrong! It should be "/spk/"!')
            sys.exit(0)
        return idx

    def _get_pairidx(self, t_path, srcspk, tarspk):
        for idx, item in enumerate(t_path):
            if fnmatch.fnmatch(item, '%s*%s' % (srcspk, tarspk)):
                break
        if idx == 0:
            print('The path format of %s and %s is wrong! It should be "/spk/spk/" or "/spk-spk/"!')
            sys.exit(0)
        return idx

    def _check_idx(self, item, name, idx):
        if idx >= len(item):
            msg = "idx '%s' (%d) is out of the length of %s\n" % (name, idx, str(item))
            msg += "The template path cannot be correctly splitted by slash.\n"
            msg += "Please check the template path in 'test_system.yml'."
            raise ValueError(msg)

    def _load_sysinfo(self):
        sysinfof = "%s%s.yml"%(self.yml_path, self.c_text['systemf'])
        if not self._check_file_exist(sysinfof):
            sys.exit(0)
        sysinfo = self._yaml_load(sysinfof)
        t_paths = sysinfo[self.c_text['templatedir']]
        srcspk  = self.c_text['srcspk']
        tarspk  = self.c_text['tarspk']
        for system in list(t_paths.keys()):
            t_paths[system] = t_paths[system].replace('\\', '/')
            t_path = t_paths[system].split('/')
            if srcspk in t_paths[system]:
                if tarspk in t_paths[system]: # voice conversion
                    if tarspk in t_path and srcspk in t_path: 
                        # path format: /srcspk/tarspk/ or /tarspk/srcspk/
                        srcidx = t_path.index(srcspk)
                        taridx = t_path.index(tarspk)
                        t_paths[system] = {'src':srcidx, 'tar':taridx, 'split':None,
                                           'src_sub':None, 'tar_sub':None }
                    else: 
                        # path format /srcspk-tarspk/ or /tarspk-srcspk/
                        pairidx = self._get_pairidx(t_path, srcspk, tarspk)
                        symbol = t_path[pairidx].replace(srcspk, "").replace(tarspk, "")
                        subsrc = t_path[pairidx].split(symbol).index(srcspk)
                        subtar = t_path[pairidx].split(symbol).index(tarspk)
                        t_paths[system] = {'src':pairidx, 'tar':pairidx, 'split':symbol,
                                           'src_sub':subsrc, 'tar_sub':subtar }
                else: # source speaker only
                    spkidx = self._get_spkidx(t_path, srcspk)
                    t_paths[system] = {'src':spkidx, 'tar':None, 'split':None,
                                       'src_sub':None, 'tar_sub':None }
            elif tarspk in t_paths[system]: # target speaker only
                spkidx = self._get_spkidx(t_path, tarspk)
                t_paths[system] = {'src':None, 'tar':spkidx, 'split':None,
                                   'src_sub':None, 'tar_sub':None }
            else:
                print('%s or %s is not in the template path of %s of %s!'\
                      % (srcspk, tarspk, system, sysinfof))
                sys.exit(0)   
        return sysinfo
    
    def _load_divide_list(self, flistf, ref=None, reflen=0):
        # load file list and divide it into sub set lists
        if not self._check_file_exist(flistf):
            sys.exit(0)
        with open(flistf, "r") as f:
            file_list = f.readlines()
        flen = len(file_list)
        if ref != None:
            if reflen != flen:
                print('The list lengths of %s(%d) and %s(%d) should be the same!' \
                      % (ref, reflen, flistf, flen))
                sys.exit(0)
        file_list= [file.strip() for file in file_list]
        file_lists = np.reshape(file_list, (-1, self.n_subset))
        file_lists = [file_lists[:,i].tolist() for i in range(self.n_subset)]
        return file_lists, flen
    
    def _parse_spkinfo(self, pathinfo, genderinfo, t_dict, filename):
        filename = filename.replace('\\', '/')
        item = filename.split('/')
        if pathinfo['tar'] == None: # only source speaker
            self._check_idx(item, 'src', pathinfo['src'])
            t_dict['srcspk'] = item[pathinfo['src']]
            t_dict['gender'] = genderinfo[t_dict['srcspk']]
        elif pathinfo['src'] == None: # only target speaker
            self._check_idx(item, 'tar', pathinfo['tar'])
            t_dict['tarspk'] = item[pathinfo['tar']]
            t_dict['gender'] = genderinfo[t_dict['tarspk']]
        else: # voice conversion
            if pathinfo['src'] == pathinfo['tar']: # format /srcspk/tarspk/ or /tarspk/srcspk/
                self._check_idx(item, 'src', pathinfo['src'])
                spkpair = item[pathinfo['src']].split(pathinfo['split'])
                t_dict['srcspk'] = spkpair[pathinfo['src_sub']]
                t_dict['tarspk'] = spkpair[pathinfo['tar_sub']]
            else: # format /srcspk-tarspk/ or /tarspk-srcspk/
                self._check_idx(item, 'src', pathinfo['src'])
                self._check_idx(item, 'tar', pathinfo['tar'])
                t_dict['srcspk'] = item[pathinfo['src']]
                t_dict['tarspk'] = item[pathinfo['tar']]
            t_dict['conversion'] = True
            srcgender = genderinfo[t_dict['srcspk']]
            targender = genderinfo[t_dict['tarspk']]
            if srcgender != targender:
                t_dict['xgender'] = True
            t_dict['gender'] = genderinfo[t_dict['tarspk']]
            t_dict['pair'] = '%s-%s' % (srcgender, targender)

    def _parse_mos(self, sysinfo, template, t_system, file_lists, conf):
        for set_idx, file_list in enumerate(file_lists): # for each sub set
            for filename in file_list: # for each file        
                t_dict = copy.deepcopy(template)
                t_dict['File'] = filename
                t_dict[self.c_text['system']] = t_system
                self._parse_spkinfo(sysinfo[self.c_text['templatedir']][t_system], 
                                    sysinfo[self.c_text['spk']], 
                                    t_dict, filename)
                conf[set_idx].append(t_dict)

    def _parse_sim(self, sysinfo, template, t_system, file_lists, ref_lists, conf):
        for set_idx, file_list in enumerate(file_lists): # for each sub set
            for filename, refname in zip(file_list, ref_lists[set_idx]): # for each file        
                t_dict = copy.deepcopy(template)
                t_dict['File'] = filename
                t_dict['File_ans'] = refname
                t_dict[self.c_text['system']] = t_system
                self._parse_spkinfo(sysinfo[self.c_text['templatedir']][t_system], 
                                    sysinfo[self.c_text['spk']], 
                                    t_dict, filename)
                conf[set_idx].append(t_dict)
    
    def _parse_xab(self, sysinfo, template, t_system,
                   systemA, systemB, systemX,
                   fileA_lists, fileB_lists, fileX_lists, conf):
        for set_idx in range(len(fileA_lists)): # for each sub set
            listA = fileA_lists[set_idx]
            listB = fileB_lists[set_idx]
            listX = fileX_lists[set_idx]
            assert len(listA)==len(listB)==len(listX)
            for file_idx in range(len(listA)): # for each file        
                t_dict = copy.deepcopy(template)
                t_dict['FileA'] = listA[file_idx]
                t_dict['FileB'] = listB[file_idx]
                t_dict['FileX'] = listX[file_idx]
                t_dict[self.c_text['system']] = t_system
                t_dict[self.c_text['system']+'A'] = systemA
                t_dict[self.c_text['system']+'B'] = systemB
                t_dict[self.c_text['system']+'X'] = systemX
                self._parse_spkinfo(sysinfo[self.c_text['templatedir']][systemA], 
                                    sysinfo[self.c_text['spk']], 
                                    t_dict, listA[file_idx])
                conf[set_idx].append(t_dict)
    
    def _parse_pk(self, sysinfo, template, t_system,
                  systemA, systemB, 
                  fileA_lists, fileB_lists, conf):
        for set_idx in range(len(fileA_lists)): # for each sub set
            listA = fileA_lists[set_idx]
            listB = fileB_lists[set_idx]
            assert len(listA)==len(listB)
            for file_idx in range(len(listA)): # for each file        
                t_dict = copy.deepcopy(template)
                t_dict['FileA'] = listA[file_idx]
                t_dict['FileB'] = listB[file_idx]
                t_dict[self.c_text['system']] = t_system
                t_dict[self.c_text['system']+'A'] = systemA
                t_dict[self.c_text['system']+'B'] = systemB
                self._parse_spkinfo(sysinfo[self.c_text['templatedir']][systemA], 
                                    sysinfo[self.c_text['spk']], 
                                    t_dict, listA[file_idx])
                conf[set_idx].append(t_dict)

    def subset_gen(self):
        print('Test files will be divided into %d sub-sets.' % self.n_subset)
        for t_idx in range(len(self.conf)): # for each evaluation type
            t_type    = self.conf[t_idx][self.c_text['t_type']]
            t_systems = self.conf[t_idx][self.c_text['system']]
            t_sets    = self.conf[t_idx][self.c_text['t_set']]
            assert len(t_sets) == self.n_subset
            tempf = '%s/%s.yml' % (self.template_path, t_type)
            template = self._yaml_load(tempf)
            conf = [[] for i in range(self.n_subset)]
            for t_system in t_systems: # for each test method
                if t_type == 'MOS' or t_type == 'SIM':
                    # load divied file list
                    flistf = '%s%s.list' % (self.data_path, t_system)
                    file_lists, flen = self._load_divide_list(flistf)
                    if t_type == 'MOS':
                        self._parse_mos(self.t_info, template, t_system, file_lists, conf)
                    elif t_type == 'SIM':
                        t_reference = self.conf[t_idx][self.c_text['reference']]
                        reflistf     = '%s%s.list' % (self.data_path, t_reference)
                        ref_lists, _ = self._load_divide_list(reflistf, flistf, flen)
                        self._parse_sim(self.t_info, template, t_system, file_lists, ref_lists, conf)
                elif t_type == 'XAB' or t_type == 'PK':
                    # prase sytemA, systemB
                    items = t_system.split('-')
                    systemA = items[0].strip('*')
                    systemB = items[1]
                    # load divied file list
                    listAf  = '%s%s.list' % (self.data_path, systemA)
                    fileA_lists, flen = self._load_divide_list(listAf)
                    listBf  = '%s%s.list' % (self.data_path, systemB)
                    fileB_lists, _    = self._load_divide_list(listBf, listAf, flen)
                    if t_type == 'PK':
                        self._parse_pk(self.t_info, template, t_system,
                                       systemA, systemB, 
                                       fileA_lists, fileB_lists, conf)
                    elif t_type == 'XAB':
                        systemX = items[2]
                        listXf  = '%s%s.list' % (self.data_path, systemX)
                        fileX_lists, _    = self._load_divide_list(listXf, listAf, flen)
                        self._parse_xab(self.t_info, template, t_system,
                                        systemA, systemB, systemX,
                                        fileA_lists, fileB_lists, fileX_lists, conf)
                else:
                    print('Type %s is not supported! Please check %s!!' % (t_type, self.fconf))     
            for set_idx, t_set in enumerate(t_sets):  # for each sub set
                subsetf = '%s%s' % (self.yml_path, t_set)
                self._yaml_dump(subsetf, conf[set_idx])
    
class UserInfo(ConfigInfo):
    """
        Class of all information of each user
    """
    def __init__(self, yml_path, c_text):
        super().__init__(yml_path, c_text)
        self.t_idxs = range(len(self.conf))

    def _conf_user_save(self, conf_user, fconf_user, name, t_set):
        conf_user[self.c_text['user_name']].append(name)
        conf_user[self.c_text['t_subset']].append(t_set)
        conf_user[self.c_text['date']] = datetime.datetime.now()
        self._yaml_dump(fconf_user, conf_user)
    
    def _check_progress(self, recordf_user):
        return list(filter(lambda item: item[self.c_text['t_finish']] == False, recordf_user))
    
    def _load_test_data(self, conf, fconf, name, t_set):
        test_type = [] # the list of test type
        test_set = [] # the list of user yml corresponding to each test type
        test_system = [] # the list of methods corresponding to each test type
        total_dict = [] # the result list of dicts of all tests
        eval_dict = [] # the result list of dicts of the uncompleted tests

        for t_idx in range(len(conf)):
            test_type.append(conf[t_idx][self.c_text['t_type']])
            test_system.append(conf[t_idx][self.c_text['system']])
            # load template record yml file
            if not self._check_file_exist(self.yml_path + conf[t_idx][self.c_text['t_set']][t_set]):
                print('Please check the "set" setting in %s' % fconf)
                sys.exit(0)
            recordf_user = self._yaml_load(self.yml_path + conf[t_idx][self.c_text['t_set']][t_set])
            # create user record yml file
            user_set = conf[t_idx][self.c_text['t_set']][t_set].replace(
                ".yml", "_%s.yml" % name)
            test_set.append(self.yml_path + user_set)
            if not self._check_file_exist(os.path.dirname(test_set[t_idx])):
                print('Please check the "set" setting in %s' % fconf)
                sys.exit(0)
            self._yaml_dump(test_set[t_idx], recordf_user)

            total_dict.append(recordf_user)
            eval_dict.append(recordf_user)

        self.test_type = test_type
        self.test_system = test_system
        self.test_set = test_set
        self.eval_dict = eval_dict
        self.total_dict = total_dict

    def _reload_test_data(self, conf, fconf_user, name, t_set):
        test_type = [] # the list of test type
        test_set = [] # the list of user yml corresponding to each test type
        test_system = [] # the list of methods corresponding to each test type
        total_dict = [] # the result list of dicts of all tests
        eval_dict = [] # the result list of dicts of the uncompleted tests

        for t_idx in range(len(conf)):
            test_type.append(conf[t_idx][self.c_text['t_type']])
            test_system.append(conf[t_idx][self.c_text['system']])
            # load user record yml file (record_user)
            user_set = conf[t_idx][self.c_text['t_set']][t_set].replace(
                ".yml", "_%s.yml"%name)
            test_set.append(self.yml_path + user_set)
            if not self._check_file_exist(test_set[t_idx]):
                print('User %s data lost!! Please check %s' % (name, fconf_user))
                sys.exit(0)
            recordf_user = self._yaml_load(test_set[t_idx])
            total_dict.append(recordf_user)
            #CHECK PROGRESS
            # remaining unfinished parts
            r_recordf_user = self._check_progress(recordf_user)
            eval_dict.append(r_recordf_user)
            if len(r_recordf_user) == 0:
                self.finished[t_idx] = True
            if len(r_recordf_user) < len(recordf_user):
                self.initial[t_idx] = False

        self.test_type = test_type
        self.test_system = test_system
        self.test_set = test_set
        self.eval_dict = eval_dict
        self.total_dict = total_dict

    def check_user(self, name):
        """LOAD AND CHECK USER PROGRESS
        Args:
            name (str): the name of the user
        Return:
            flag (bool): True: all tests of the user have been completed 
                         False: new user or the tests are not completed
        """
        #LOAD RECORD
        conf_user, _ = self._load_record()        
        #LOAD USER INFO
        self.finished = [False]*len(self.conf)
        self.initial  = [True]*len(self.conf)
        if name in conf_user[self.c_text['user_name']]:
            # load user (conf_user)
            t_set = conf_user[self.c_text['t_subset']][conf_user[self.c_text['user_name']].index(name)]
            # reload testing data
            self._reload_test_data(self.conf, self.fconf_user, name, t_set)
        else:
            # create new user (conf_user)
            conf_user[self.c_text['subset_idx']] += 1
            if conf_user[self.c_text['subset_idx']] >= conf_user[self.c_text['n_subset']]:
                conf_user[self.c_text['subset_idx']] = 0
            t_set = conf_user[self.c_text['subset_idx']]
            # load testing data
            self._load_test_data(self.conf, self.fconf, name, t_set)
            self._conf_user_save(conf_user, self.fconf_user, name, t_set)

        self.flag = (sum(self.finished)==len(self.conf))
        return self.flag
 
    def save_result(self, t_idx):
        """SAVE RESULTS
        Args:
            t_idx (int): the index of test
        """
        self._yaml_dump(self.test_set[t_idx], self.total_dict[t_idx])
        #CHECK PROGRESS
        if len(self._check_progress(self.total_dict[t_idx])) == 0:
            self.finished[t_idx] = True

# USER RESULT CLASS
class UserResult(UserInfo):
    """
        Class of results of each user
    """
    def __init__(self, user_name, user_set, test_type, yml_path, c_text):
        super().__init__(yml_path, c_text)
        self.name   = user_name
        self.t_set  = user_set
        self.t_type = test_type
        self._load_result()
        # remaining unfinished parts
        r_recordf_user = self._check_progress(self.recordf_user)
        if len(r_recordf_user) == 0:
            self.finished = True
        else:
            self.finished = False

    def _load_result(self):
        # load user yml
        frecordf_user = "%s%s_%d_%s.yml" % (self.yml_path,
                                            self.t_type,
                                            self.t_set,
                                            self.name)
        if not self._check_file_exist(frecordf_user):
            sys.exit(0)
        self.recordf_user = self._yaml_load(frecordf_user)        