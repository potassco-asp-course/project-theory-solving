import sys
from subprocess import run, PIPE, TimeoutExpired
import os
import tempfile
import json
import time


CLINGO = "/usr/share/miniconda/bin/clingo"
PYTHON = "/usr/share/miniconda/bin/python"
INSTANCES = "instances/"
REF_ENC = "checker.lp"
DUMMY = "dummy.lp"
SOLUS = "925"
SOLUTIONS = "solutions/"


def call_python(input_names, timeout):
    cmd = [PYTHON, "app.py",  "job2task.lp",  "dl/fsE.lp", "--minimize-variable",  "bound", "--warn=no-atom-undefined", "--warn=no-file-included", "--warn=no-operation-undefined", "--warn=no-global-variable" ] + input_names
    start = time.time()
    output = run(cmd, stdout=PIPE, stderr=PIPE, timeout=timeout)
    end = time.time()
    if output.stderr:
        raise RuntimeError("Clingo: %s" % output.stderr)
    return output.stdout, end-start

def test(inst, timeout):
    try:
        stdout, time = call_python([INSTANCES+inst], timeout)
    except RuntimeError as e:
        raise e
    print(33*"*")
    stdout = stdout.decode('utf-8')
    i=stdout.rfind("Answer")
    beginning=stdout.find("\n", i)+1
    end=stdout.find("\n", beginning)
    solution = stdout[beginning:end].split(" ")
    solution.sort()

    # check optimal solution
    inst_sol = inst[:-2]+"sol"
    ref_solutions=[]
    with open(SOLUTIONS+inst_sol,"r") as infile:
        #ref_solutions = infile.read()
        while(infile):
            line = infile.readline()
            if line == "":
               break
            line = infile.readline()
            line=line[1:-1]
            sol = list(line.split(" "))
            sol.sort()
            ref_solutions.append(sol)
    for s in ref_solutions:
        s.sort()
    ref_solutions.sort()
    return solution in ref_solutions, time

def main():
    # check input
    if len(sys.argv) < 1:
        raise RuntimeError("not enough arguments (%d instead of 3)" % (len(sys.argv) - 1))
    timeout = sys.argv[1]
    timeout = int(timeout)

    dir = os.listdir(INSTANCES)
    dir.sort()
    success = True

    message = ""
    #loop over all instances
    for inst in dir:
        result = 0
        error = False
        try:
            res, time = test(inst, timeout)
            if not res:
                success = False
        except Exception as e:
            success = False
            if isinstance(e, TimeoutExpired):
                result = "timeout\n"
            else:
                result = "error\n"
                error = e
        message += "$"+inst+ ": "
        if result:
            message += result
            if error:
                message += str(error)+"\n"
        else:
            message += "success" if res else "failure"
            message += " in "+str(1000*time)[:7]+" ms\n"
    return success, message

if __name__ == '__main__':
    try:
        success, message = main()
        if success:
            message += "SUCCESS\n"
        else:
            message += "FAILURE\n"
        sys.stdout.write(message)
    except Exception as e:
        sys.stderr.write("ERROR: %s\n" % str(e))
        exit(1)
