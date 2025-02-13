# -*- coding: utf-8 -*-
"""
Created on Mon May 6 2019

@author: Seahymn, Daniel Lin
"""
import pickle
import csv
import os
import pandas as pd

# Separate '(', ')', '{', '}', '*', '/', '+', '-', '=', ';', '[', ']' characters.
def SplitCharacters(str_to_split):
    #Character_sets = ['(', ')', '{', '}', '*', '/', '+', '-', '=', ';', ',']
    str_list_str = ''
    
    if '(' in str_to_split:
        str_to_split = str_to_split.replace('(', ' ( ') # Add the space before and after the '(', so that it can be split by space.
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if ')' in str_to_split:
        str_to_split = str_to_split.replace(')', ' ) ') # Add the space before and after the ')', so that it can be split by space.
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '{' in str_to_split:
        str_to_split = str_to_split.replace('{', ' { ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '}' in str_to_split:
        str_to_split = str_to_split.replace('}', ' } ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '*' in str_to_split:
        str_to_split = str_to_split.replace('*', ' * ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '/' in str_to_split:
        str_to_split = str_to_split.replace('/', ' / ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '+' in str_to_split:
        str_to_split = str_to_split.replace('+', ' + ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '-' in str_to_split:
        str_to_split = str_to_split.replace('-', ' - ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '=' in str_to_split:
        str_to_split = str_to_split.replace('=', ' = ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if ';' in str_to_split:
        str_to_split = str_to_split.replace(';', ' ; ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '[' in str_to_split:
        str_to_split = str_to_split.replace('[', ' [ ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if ']' in str_to_split:
        str_to_split = str_to_split.replace(']', ' ] ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '>' in str_to_split:
        str_to_split = str_to_split.replace('>', ' > ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '<' in str_to_split:
        str_to_split = str_to_split.replace('<', ' < ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '"' in str_to_split:
        str_to_split = str_to_split.replace('"', ' " ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if '->' in str_to_split:
        str_to_split = str_to_split.replace('->', ' -> ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '>>' in str_to_split:
        str_to_split = str_to_split.replace('>>', ' >> ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if '<<' in str_to_split:
        str_to_split = str_to_split.replace('<<', ' << ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
    
    if ',' in str_to_split:
        str_to_split = str_to_split.replace(',', ' , ')
        str_list = str_to_split.split(' ')
        str_list_str = ' '.join(str_list)
        
    if str_list_str is not '':
        return str_list_str
    else:
        return str_to_split
        
def SavedPickle(path, file_to_save):
    with open(path, 'wb') as handle:
        pickle.dump(file_to_save, handle)

def Save3DList(save_path, list_to_save):
    with open(save_path, 'w', encoding='latin1') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerows(list_to_save)
        

def Save2DList(save_path, list_to_save):
    with open(save_path, 'w', encoding='latin1') as f:
        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
        wr.writerow(list_to_save)
        
def ListToCSV(list_to_csv, path):
   df = pd.DataFrame(list_to_csv)
   df.to_csv(path, index=False)
   
def LoadPickleData(path):
    with open(path, 'rb') as f:
        loaded_data = pickle.load(f)
    return loaded_data
   
# Remove ';' from the list.
def removeSemicolon(input_list):
    new_list = []
    for line in input_list:
        new_line = []
        for item in line:
            if item != ';' and item != ',':
                new_line.append(item)
        new_list.append(new_line)
    
    return new_list

# Further split the elements such as "const int *" into "const", "int" and "*"
def ProcessList(list_to_process):
    token_list = []
    for sub_list_to_process in list_to_process:
        sub_token_list = []
        if len(sub_list_to_process) != 0:
            for each_word in sub_list_to_process: # Remove the empty row
                each_word = str(each_word)
                sub_word = each_word.split()
                for element in sub_word:
                    sub_token_list.append(element)
            token_list.append(sub_token_list)
    return token_list
 
def getCFilesFromText(path):
    files_list = []
    file_id_list = []
    if os.path.isdir(path):
        for fpath,dirs,fs in os.walk(path):
            for f in fs:
                if (os.path.splitext(f)[1] == '.c'):
                    file_id_list.append(f)  
                if (os.path.splitext(f)[1] == '.c'):
                    with open(fpath + os.sep + f, encoding='latin1') as file: # the encoding can also be utf-8
                        lines = file.readlines()
                        file_list = []
                        for line in lines:
                            if line is not ' ' and line is not '\n': # Remove sapce and line-change characters
                                sub_line = line.split()
                                new_sub_line = []
                                for element in sub_line:
                                    new_element = SplitCharacters(element)
                                    new_sub_line.append(new_element)
                                new_line = ' '.join(new_sub_line)
                                file_list.append(new_line)
                        new_file_list = ' '.join(file_list)
                        split_by_space = new_file_list.split()
                    files_list.append(split_by_space)
        return files_list, file_id_list
    
# Data labels are generated based on the sample IDs. All the vulnerable function samples are named with CVE IDs.    
def GenerateLabels(input_arr):
    temp_arr = []
    for func_id in input_arr:
        temp_sub_arr = []
        if "cve" in func_id or "CVE" in func_id:
            temp_sub_arr.append(1)
        else:
            temp_sub_arr.append(0)
        temp_arr.append(temp_sub_arr)
    return temp_arr

    
    
    
    
    
    
    
    