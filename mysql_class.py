#encoding=utf-8

#!/usr/bin/python 
# -*- coding: utf-8 -*-

# author:             bryanyuan2
# description:        mysql_class
# note:                  

#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import MySQLdb
import re
import string

#
# class mysql
#
class mysql: 
    def __init__(self,db_host,db_user,db_pass,db_name):
        # mysql connect
        db = MySQLdb.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name, use_unicode=True, charset="utf8")
        self.cursor = db.cursor()
    
    # sql_only_function
    def sql_only_function(self,sql_text):
        self.cursor.execute(sql_text)
        result = self.cursor.fetchall()
        return result