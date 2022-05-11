#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author: Benjamin Chen
"""
Find duplicate files inside a directory tree.
dedup -root <paths to directory to be dedub> [-move] [-priority ftLn] [-exclude <regex>s ]

"""

from os import walk, remove, stat, rename
import os
from os.path import join as joinpath
from hashlib import md5
import re

def find_duplicates( rootdirs, priority, excludes ):
    """Find duplicate files in directory tree."""
    filesizes = {}
    # Build up dict with key as filesize and value is list of filenames.
    for f_order in range(len(rootdirs)):
        rootdir = rootdirs[f_order]
        for path, dirs, files in walk( rootdir ):
            if jump_or_not(excludes, path) :
                continue
            for filename in files:
                filepath = joinpath( path, filename )
                if jump_or_not(excludes, filepath):
                    continue
                filesize = stat( filepath ).st_size
                filesizes.setdefault( filesize, [] ).append( [filepath, f_order] )
    unique_group = dict()
    duplicates = [] 
    # We are only interested in lists with more than one entry.
    for files in [ flist for flist in filesizes.values() if len(flist)>1 ]:
        for (filepath, f_order) in files:
            with open( filepath, "rb" ) as openfile:
                filehash = md5( openfile.read() ).hexdigest()
            ctime =  stat( filepath ).st_ctime
            nlen = len( os.path.basename(filepath))  # length of filename 
            plen = len (os.path.dirname(filepath))   # length of folderpath
            if filehash not in unique_group.keys():
                unique_group[filehash] = [filepath, f_order, ctime, plen, nlen]
            else:
                unique_group[filehash], dup = compare(priority,  unique_group[filehash],  [filepath, f_order, ctime, plen, nlen])
                duplicates.append((dup[0],f_order))
    return duplicates

def jump_or_not(excludes, string):
    if excludes:
        for ex in excludes:
            if re.search(ex, string):
                print("Excluded ", string )
                return True
    return False

def compare(priority, x, y):
    p_dict = {"f": 1, "F": -1,
             "t": 2, "T": -2,
              "l":3, "L":-3,
             "n": 4, "N": -4 }
    for p in priority:
        if p not in p_dict:
            continue
        res = compare_n(p_dict[p], x, y)
        if res == None:
            continue
        else:
            return res
    return x, y

def compare_n(n, x ,y ):
    sign = True
    if n < 0:
        n= -n
        sign = False
    if x[n] == y[n]:
        return None
    elif (x[n] <  y[n]) == sign:
        return x, y
    else:
        return y, x 

if __name__ == '__main__':
    from argparse import ArgumentParser    
    PARSER = ArgumentParser( description='Finds duplicate files and optional move to "_duplicate-files".' )
    PARSER.add_argument( '-root', metavar='<path>', help='Dir(s) to search.', nargs='*' )
    PARSER.add_argument( '-move', action='store_true', help='Move dulicate files to "_duplicate-files" directory')
    PARSER.add_argument( '-priority', metavar='<ftLn>', default='ftLn', help='Set priotiry of files keeping. "t" - creation time earlier; "f" - folder sequence in the argument; "l" - path shorter; "n" - name shorter. T F L N mean reversed priority.')
    PARSER.add_argument( '-exclude', metavar='<regex>', default=['_duplicate_files'], nargs='*', help='filename/path which contains the <regex> will be ignored.')             
    ARGS = PARSER.parse_args()
    if not ARGS.root :
        PARSER.print_help()
    else:
        root = [os.path.abspath(x) for x in  ARGS.root ]
        father_path = [os.path.abspath(joinpath(x,'..')) for x in root ]
        move_dest = [os.path.abspath(joinpath(x, '_duplicate_files')) for x in father_path]
        DUPS = find_duplicates( root, ARGS.priority, ARGS.exclude )
        print ('%d Duplicate files found.' % len(DUPS))
        for (f, f_order) in sorted(DUPS):
            if ARGS.move == True:
                dest_f = f.replace(father_path[f_order], move_dest[f_order],1)
                try:
                    if not os.path.exists(os.path.dirname(dest_f)):
                        os.makedirs(os.path.dirname(dest_f))
                    rename(f, dest_f)
                except Exception as e:
                    print( e, dest_f)
                else:
                    print( '\tMoved '+ f)
            else:
                print ('\t'+ f)
