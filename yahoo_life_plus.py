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
db_user = "root"
db_pass = "test1865"
db_name = "query"

call_sql = mysql(db_host,db_user,db_pass,db_name)

yahoo_const_page = "http://tw.ipeen.lifestyle.yahoo.net/shop/"
yahoo_const_page_navi = "http://tw.ipeen.lifestyle.yahoo.net"

db_table_yahoo_life_plus_shop = "yahoo_life_plus_shop"
db_table_yahoo_life_plus_dish = "yahoo_life_plus_dish"
db_table_yahoo_life_plus_tag = "yahoo_life_plus_tag"

def yahoo_life_plus_parser(page,shop_id):

	u = urllib2.urlopen(page)
	soup = BeautifulSoup(u)
	y_title = ""
	y_address = ""

	try:
		y_title = soup.find("div", {"class": "path"}).find("span").contents[0]
	except:
		print "title e"

	try:
		y_address = soup.find("a", {"class": "addr"}).contents[0]
	except:
		print "address e"

	if (y_title!=''):
		
		print y_title
		y_dishes_info = soup.find("div", {"class": "kw"}).findAll(text=True)
		y_tag_info = soup.find("td", {"class": "kw"}).findAll(text=True)
		
		y_title = y_title.replace("'","\"")

		# sql
		#sql = "INSERT INTO " + str(db_table_yahoo_life_plus_shop) + " (name, address, url) VALUES ('" + str(y_title) + "','" + str(y_address) + "','" + str(page) + "')"
		#call_sql.sql_only_function(sql.encode('utf-8'))

		data = call_sql.sql_only_function("SELECT * FROM " + str(db_table_yahoo_life_plus_shop) + " ORDER BY shop_id DESC LIMIT 1")
		get_last_shop_id = data[0][0]

		y_dishes = []
		y_tag = []

		#print y_title
		#print y_dishes_info
		#print y_address
		
		for i in range(0,len(y_dishes_info)):
			if (i%2==0):
				y_dishes_info[i] = re.sub(r"\(.\)", "", y_dishes_info[i])
				found = re.search("\(",y_dishes_info[i])
				if (found):
					y_dishes_info[i] = y_dishes_info[i][0:found.start()]
				y_dishes.append(y_dishes_info[i])

				# sql
				if (y_dishes_info[i]!="暫無資料"):
					print "add " + y_dishes_info[i] + " into database"
					#sql = "INSERT INTO " + str(db_table_yahoo_life_plus_dish) + " (shop_id, dish) VALUES ('" + str(get_last_shop_id) + "','" + str(y_dishes_info[i]) + "')"
					#call_sql.sql_only_function(sql.encode('utf-8'))

		for i in range(1,len(y_tag_info)-1):
			y_tag_info[i] = re.sub(r"\(.\)", "", y_tag_info[i])
			y_tag_info[i] = y_tag_info[i].replace(" ","").replace("\n","")
			found = re.search("\(",y_tag_info[i])
			if (found):
				y_tag_info[i] = y_tag_info[i][0:found.start()]
			y_tag.append(y_tag_info[i])

			print "add " + y_tag_info[i] + " into database"
			# sql
			#sql = "INSERT INTO " + str(db_table_yahoo_life_plus_tag) + " (shop_id, tag) VALUES ('" + str(get_last_shop_id) + "','" + str(y_tag_info[i]) + "')"
			#call_sql.sql_only_function(sql.encode('utf-8'))


		"""
		for i in range(0,len(y_dishes)):
		 	print y_dishes[i]
		for i in range(0,len(y_tag)):
		 	print y_tag[i]
		"""


for i in range(0,6600):
	page = "http://tw.ipeen.lifestyle.yahoo.net/index.php/search/?p=" + str(i) + "&c=1&t=1"
	u = urllib2.urlopen(page)
	soup = BeautifulSoup(u)
	tt = soup.findAll("h2", {"class": "name"})
	for i in tt:
		curr_id = i.find("a")['href'].replace("/shop/","")
		pp = yahoo_const_page_navi + i.find("a")['href']
		yahoo_life_plus_parser(pp,curr_id)
