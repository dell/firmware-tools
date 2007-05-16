#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:

  #############################################################################
  #
  # Copyright (c) 2005 Dell Computer Corporation
  # Dual Licenced under GNU GPL and OSL
  #
  #############################################################################
"""
repository module
"""

from __future__ import generators

import package

class DepParser(object):
    tokens = ( 'ID', 'LT', 'LE', 'EQ', 'GE', 'GT', 'COMMA' )
    t_ID   = r'[\w()]+'
    t_LT   = r'<'
    t_LE   = r'<='
    t_EQ   = r'=='
    t_GE   = r'>='
    t_GT   = r'>'
    t_COMMA = r','
    t_ignore = " \t"

    def t_error(self, t): 
        print "Illegal character '%s'" % t.value[0] 
        t.skip(1)

    def __init__(self, string, inventory, fullInventory, *args, **kargs):
        self.inventory = inventory
        self.fullInventory = fullInventory
        self.depPass = 1

        import ply_lex
        lexer = ply_lex.lex( module=self )

        import ply_yacc 
        parser = ply_yacc.yacc( module=self, write_tables=0, debug=0 )

        parser.parse(string, lexer=lexer, debug=0)

    precedence = (
        ('left', 'COMMA'),
        )

    def p_error(self, t): 
        print "Syntax error at '%s'" % t

    def p_stmt(self, t):
        # statement_list can be 1) empty, 2) single statement, or 3) list
        """statement_list : 
                          | statement  
                          | statement_list COMMA statement
           statement : dep"""
        pass

    def p_package_depencency(self, t):
        """dep : ID LT ID
               | ID LE ID
               | ID EQ ID
               | ID GE ID
               | ID GT ID
        """
        op  = t[2]
        reqPkg = package.Package (name=t[1], version=t[3])
        pkg = self.inventory.get(t[1])
        if pkg:
            r = pkg.compareVersion(reqPkg)
            evalStr = "0 %s %s" % (op, r)
            if not eval(evalStr):
                self.reason = "Failed for rule: requires %s %s %s" % (t[1], t[2], t[3])
                self.depPass = 0
        else:
            self.reason = "Repository package doesn't exist in system inventory."
            self.depPass = 0


    def p_package_exists(self, t):
        """dep : ID"""
        if not self.inventory.get(t[1]):
            self.reason = "Failed for rule: requires %s" % t[1]
            self.depPass = 0

