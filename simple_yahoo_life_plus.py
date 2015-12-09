#encoding=utf-8

# http://tw.ipeen.lifestyle.yahoo.net/index.php/search/?p=2&c=1&t=1

#!/usr/bin/python 
# -*- coding: utf-8 -*-

# author:             bryanyuan2
# description:        yahoo_life_plus


from BeautifulSoup import BeautifulSoup
import urllib2
import re
from mysql_class import mysql
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

#
# mysql setting        
#
db_host = "127.0.0.1"
db_user = "bryanyuan2"
db_pass = "iisr"
db_name = "iisr"

call_sql = mysql(db_host,db_user,db_pass,db_name)

yahoo_const_page = "http://tw.ipeen.lifestyle.yahoo.net/shop/"
yahoo_const_page_navi = "http://tw.ipeen.lifestyle.yahoo.net"

db_table_yahoo_life_plus_shop = "yahoo_life_plus_shop"
	
for i in range(1,6600):
	try:
		page = "http://tw.ipeen.lifestyle.yahoo.net/index.php/search/?p=" + str(i) + "&c=1&t=1"
		u = urllib2.urlopen(page)
		soup = BeautifulSoup(u)
		tt = soup.findAll("h2", {"class": "name"})
		for i in tt:
			shop_title = i.find("a").contents[0].replace("\t","").replace("\n","")
			print shop_title
			# sql
			sql = "INSERT INTO " + str(db_table_yahoo_life_plus_shop) + " (name, url) VALUES ('" + str(shop_title) +  "','" + str(page) + "')"
			call_sql.sql_only_function(sql.encode('utf-8'))
	except:
		continue
		