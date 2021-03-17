# -------------------------------------------------------------------------------
# replace.py
#
# Replacing DFUndefined and None with DFTerminal
#
# Copyright (C) 2013, Shinya Takamaeda-Yamazaki
# License: Apache 2.0
# -------------------------------------------------------------------------------
from __future__ import absolute_import
from __future__ import print_function
import sys
import os

from pyverilog.dataflow.dataflow import *


def replaceUndefined(tree, termname):
    if tree is None:
        term = DFTerminal(termname)
        term.fixed = True
        return term
    if isinstance(tree, DFUndefined):
        term = DFTerminal(termname)
        term.forceWidth = tree.width
        term.fixed = True
        return term
    # if isinstance(tree, DFHighImpedance): return DFTerminal(termname)
    if isinstance(tree, DFConstant):
        return tree
    if isinstance(tree, DFEvalValue):
        return tree
    if isinstance(tree, DFTerminal):
        return tree
    if isinstance(tree, DFBranch):
        condnode = replaceUndefined(tree.condnode, termname)
        truenode = replaceUndefined(tree.truenode, termname)
        falsenode = replaceUndefined(tree.falsenode, termname)
        term = DFBranch(condnode, truenode, falsenode)
        if tree.truenode == None:
            assert(term.truenode.fixed == True)
            assert(tree.falsenode != None)
            term.truenode.forceWidth = tree.falsenode
        elif tree.falsenode == None:
            assert(term.falsenode.fixed == True)
            assert(tree.truenode != None)
            term.falsenode.forceWidth = tree.truenode
        return term
    if isinstance(tree, DFOperator):
        nextnodes = []
        for n in tree.nextnodes:
            nextnodes.append(replaceUndefined(n, termname))
        return DFOperator(tuple(nextnodes), tree.operator)
    if isinstance(tree, DFPartselect):
        msb = replaceUndefined(tree.msb, termname)
        lsb = replaceUndefined(tree.lsb, termname)
        var = replaceUndefined(tree.var, termname)
        return DFPartselect(var, msb, lsb)
    if isinstance(tree, DFPointer):
        ptr = replaceUndefined(tree.ptr, termname)
        var = replaceUndefined(tree.var, termname)
        return DFPointer(var, ptr)
    if isinstance(tree, DFConcat):
        nextnodes = []
        for n in tree.nextnodes:
            nextnodes.append(replaceUndefined(n, termname))
        return DFConcat(tuple(nextnodes))
    raise DefinitionError('Undefined DFNode type: %s %s' % (str(type(tree)), str(tree)))
