#===============================================================================
# tools/parser.py
#===============================================================================
'''
Thomas Rennie 27/07/2020
Module to parse input files into an outputted dictionary for use in general
purpose programs.
'''

import re

def parse_file(param_file_name):

    param_file = open(param_file_name, 'r')

    params = {}
    obj, obj2, var, val = None, None, None, None

    for line in param_file:

        if (line[0]!='#') and (line.strip() != ''):
            line = line[:-1].strip()

            if line[0] == '[':
                obj = line[1:].split(']')[0]
                params[obj] = {}
                obj2, var, val = None, None, None

            elif line[0] == '{':
                obj2 = line[1:].split('}')[0]
                params[obj][obj2] = {}
                var, val = None, None

            else:
                var, val = line.split('|')
                var = var.strip()

                # split val into list of values (or keep as one if "...")
                if val.strip()[0] == '"':
                    val = [val.strip()[1:-1]]
                else:
                    val = val.split()

                # get and apply datatype (int, float, frac, string)
                for i in range(len(val)):
                    alpha_flag, div_flag, dp_flag = False, False, False
                    for j in val[i]:
                        if j.isalpha():
                            alpha_flag = True
                        if j == "/":
                            div_flag = True
                        if j == ".":
                            dp_flag = True
                    if alpha_flag == True and div_flag == False and dp_flag == False:
                        if val[i].strip() == 'False':
                            val[i] = False
                        if val[i].strip() == 'True':
                            val[i] = True

                    if alpha_flag == False:
                        if div_flag == True:
                            temp = val[i].split('/')
                            val[i] = float(temp[0]) / float(temp[1])
                        else:
                            if dp_flag == True:
                                val[i] = float(val[i])
                            else:
                                val[i] = int(val[i])
                if len(val) == 1:
                    val = val[0]

                # write out to dictionary
                if obj2 != None:
                    params[obj][obj2][var] = val
                else:
                    params[obj][var] = val
    return params
