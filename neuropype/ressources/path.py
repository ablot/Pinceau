# -*- coding: utf-8 -*-

import os

def toPath(path):
    """Translate a path to the absolute path, replacing ~"""
    path = os.path.normpath(path)
    if path.startswith('~'):
        home = os.path.expanduser('~')
        path = os.path.join(home, path.lstrip('~/'))
    else:
        path = os.path.join(os.getcwd(), path)
    return os.path.realpath(path)

def readConfig(path2file):
    PATH_DICT = {}
    config = file(path2file, 'r')
    for line in config:
        if not line.strip():
            continue
        name, path = [i.strip() for i in line.split('=')]
        PATH_DICT[name] = toPath(path)
    config.close()
    return PATH_DICT

# def cutPath(path, path_dict = None):
#     """Return a list with [racine_name, end] if there is a racine in path_dict
#     else return path (a string)"""
#     if path_dict is None:
#         from __main__ import PATH_DICT as path_dict
#     path = os.path.realpath(path)
#     out = []
#     found = ''
#     for name, p in path_dict.iteritems():
#         if path.startswith(p):
#             if not found or len(found) < len(p):
#                 out = [name, path.lstrip(p)]
#                 found = p
#     if not found:
#         out = path
#     return out

# def toSaveString(path, path_dict = None):
#     if path_dict is None:
#         from __main__ import PATH_DICT as path_dict
#     cutted = cutPath(toPath(path), path_dict)
#     if isinstance(cutted, list):
#         return "PATH_DICT['%s'] +  '%s'"%(cutted[0], cutted[1])
#     return "'%s'"%cutted
    
    
