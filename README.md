# dedup
move depulicate files found in given folder trees to _duplicated_file folder.
written in python 3

## usage: 
`dedup.py [-h] [-root [<path> ...]] [-move] [-priority <ftLn>] [-exclude [<regex> ...]]`
```
optional arguments:
  -h, --help            show this help message and exit
  -root [<path> ...]    Dir(s) to search.
  -move                 Move dulicate files to "_duplicate-files" directory
  -priority <ftLn>      Set priotiry of files keeping. "t" - creation time earlier; "f" - folder sequence in the argument; "l" - path shorter; "n" - name shorter. T F L N mean reversed priority.
  -exclude [<regex> ...]
                        filename/path which contains the <regex> will be ignored.
```
