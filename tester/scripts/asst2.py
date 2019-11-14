#!/usr/bin/python3
#
# helper functions for assignment 2
#

import tester
import pickle

# may need to tweak rel_tol and abs_tol
def isclose(a, b, rel_tol=1e-09, abs_tol=1e-15):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)  

def similarity(ans, ref, verbose):
    if ans.xlabels != ref[1]:
        print("ERROR: xlabels mismatch")
        return 0.
    if sorted(ans.ylabels) != sorted(ref[0].keys()):
        print("ERROR: ylabels mismatch")
        return 0.
    count = 0
    good = 0 
    for x in ans.xlabels:
        for y in ans.ylabels:
            count += 1
            try:
                refval = ref[0][y][ref[1].index(x)]
            except (IndexError, KeyError):
                print("({},{}) does not exist on instructor's solution".format(
                    y, x))
                continue
            if ans[y,x] is None:
                if verbose:
                    print("empty cell on ({},{})".format(y, x))
            elif ans.celltype is float and isclose(ans[y,x], float(refval)):
                good += 1
            elif ans.celltype is str and ans[y,x] == str(refval):
                good += 1    
            elif verbose:
                print("mismatch on ({},{}): {} vs {}".format(
                    y, x, ans[y,x], refval))
    return good/count

def load_result(name):
    mark = 5
    tester.includepath()
    import easybj
    result = easybj.calculate()[name]
    path = tester.datapath(name + '.p', 'asst2')
    f = open(path, 'rb')
    refobj = pickle.load(f)
    f.close()
    return result, refobj

