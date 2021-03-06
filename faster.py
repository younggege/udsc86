#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time

from functools import wraps
from subprocess import Popen


def fn_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("Total time running %s: %s seconds" %
               (function.func_name, str(t1 - t0))
               )
        return result

    return function_timer


# todo : create a tmp file to store binary code
def openfile(trace_file, dir):
    tmp = "tmp.txt"
    inst = 1
    sub_str = "Inst[1]:"

    file_name = os.path.join(dir, trace_file)
    tmp_file = os.path.join(dir, tmp)

    if os.path.isfile('tmp.txt'):
        os.remove(tmp_file)

    ptr = open(tmp_file, "a")
    with open(file_name, 'r') as f:
        trace_lines = f.readlines()
    flen = len(trace_lines)
    for line in range(flen):
        if sub_str in trace_lines[line]:
            list_obj = []
            binary = trace_lines[line + 1].strip('\n').split(',')[1]
            hex_code = binary.split('x')
            obj = hex_code[1]
            length = len(obj)
            for i in range(0, length, 2):
                list_obj.append(obj[i:i + 2])
            shell_obj = " ".join(list_obj)
            ptr.write(shell_obj + '| ' + str(inst) + '\n')
            inst = inst + 1

    f.close()
    ptr.close()

    print "open trace.log success!\n"
    return tmp_file


@fn_timer
def analysis(tmp_file, dir):
    counter_dict = {}
    tmp2 = "pipe.txt"
    num = 1
    tmp2_file = os.path.join(dir, tmp2)
    if os.path.isfile(tmp2):
        os.remove(tmp2_file)

    op_line = open(tmp_file,'r').readlines()
    pipe = open(tmp2_file, 'a')
    flen = len(op_line)
    for line in range(flen):
        opcode, inst = op_line[line].split('| ')
        n = inst.strip('\n')
        ud_insn_asm(opcode, pipe)

    pipe.close()
    doc = open(tmp2_file,'r')
    instructions = doc.readlines()
    ilen = len(instructions)
    for l in range(ilen):
        if instructions[l][16] == '\n':
            continue
        else:
            b = instructions[l][17:42].find(' ')
            instruct = instructions[l][17:17+b]
            if instruct not in counter_dict:
                counter_dict.setdefault(instruct, [num])
            else:
                counter_dict[instruct].append(num)
            num += 1

    return counter_dict


def ud_insn_asm(ud_obj, pipe):
    set_mode = " -64 "
    command = "echo " + ud_obj + "|udcli" + set_mode + "-x -att -noff"
    p = Popen(command, bufsize=42, shell=True, stdout=pipe)
    #if p.wait() != 0:
    #    print "There were some errors"


def gen_file(result_file, counter):
    dir = os.path.abspath('.')
    file_name = os.path.join(dir, result_file)
    if os.path.isfile("result.txt"):
        os.remove(file_name)
    writer_ptr = open(file_name, "w")
    for key,value in counter.iteritems():
        writer_ptr.write(str(key) + " : " + str(len(value)) + "\n" + str(value) + "\n\n")
    print "write done!\n"
    writer_ptr.close()


if __name__ == "__main__":
    trace_file = "trace.log"
    result_file = 'result.txt'
    dir = os.path.abspath('.')

    tmp = openfile(trace_file, dir)
    count_dict = analysis(tmp, dir)
    gen_file(result_file, count_dict)

