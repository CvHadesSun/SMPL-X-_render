'''
Author: your name
Date: 2021-11-11 15:07:54
LastEditTime: 2021-11-11 15:07:54
LastEditors: Please set LastEditors
Description: 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
FilePath: /PG-engine/src/tools/file_op.py
'''

import os
import sys


# disable render output
def disable_output_start():
    logfile = "/dev/null"
    open(logfile, "a").close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)
    return old


def disable_output_end(old):
    os.close(1)
    os.dup(old)
    os.close(old)


def mkdir_safe(directory):
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass