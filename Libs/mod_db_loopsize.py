import sqlite3, csv, os, sys, copy
import MyException
import re

import ESA

if __name__ == "__main__":
    esa = ESA.ESA(sys.argv[1])
    esa.prepReadDB()
    esa.getTableName()
    esa.listDB()

    print "BEFORE"
    ppp = esa.getDict()
    for p in ppp:
        oindex = p['o_index']
        isDone = p['isDone']
        if isDone == 0:
            print oindex,p['puckid'],p['pinid'],"loop_size=",p['loopsize']
            esa.updateValueAt(oindex,"loopsize", 200.0)

    ppp = esa.getDict()
    print "AFTER"
    for p in ppp:
        isDone = p['isDone']
        if isDone == 0:
            oindex = p['o_index']
            print oindex,p['puckid'],p['pinid'],"loopsize=",p['loopsize']
