#!/usr/bin/python3
#
# split ev table test for assignment 2
#

import tester
import asst2

total = 25
partial = 5

def check_split(conn, verbose):    
    result, refobj = asst2.load_result('split')
    val = asst2.similarity(result, refobj, verbose)
    if val < 1.:
        if verbose:
            print("INFO: attempting to load resplit tables")
        try:
            result, refobj = asst2.load_result('resplit')
            num_partials = len(refobj)
            marks = (total - partial*num_partials)*val**2

            for i, refelem in enumerate(refobj):
                try:
                    table = result[i]
                except IndexError:
                    print("ERROR: student does not have resplit[%d]"%i)
                    continue
                val = asst2.similarity(table, refelem, verbose)
                marks += partial*val**2
            
            conn.send(marks)        
            return
        except KeyError:
            print("WARNING: could not load resplit table from student")
    conn.send(total*val**2)
    

def main():
    test = tester.Proc('split test', total)
    mark = test.run_process(check_split)
    test.add_mark(mark)

if __name__ == '__main__':
    main()

    
