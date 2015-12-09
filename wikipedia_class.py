#!/usr/bin/python 
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
from BeautifulSoup import BeautifulSoup
import re
import string

class wikipedia_class:

	db_table_query_log = ""
	call_sql = ""

	def __init__(self, db_table_query_log, call_sql):
		self.db_table_query_log = db_table_query_log
		self.call_sql = call_sql

	def extract_string_zh_part(self, query = "台北鼎泰豐DANCE CLUB", ngram=2):

		query = query.replace(" ", "。")

		query_ary = []
		chinese_word = re.findall('[^A-Za-z0-9\ ]', query)
		chinese_word_ary = "".join(chinese_word)
		chinese_word_ary = chinese_word_ary.decode("utf8")

		for i in range(0,len(chinese_word_ary)-ngram+1):
			term = chinese_word_ary[i:i+ngram]
			if (self.zh_wiki_query_search_exist(term,"xml")):
				if (term != ''):
					query_ary.append(term)
		return query_ary

	# zh_wiki_query_search_category_exist
	def zh_wiki_query_search_category_exist(self, wiki_query = "鼎泰豐", wiki_cate_format_type = "xml"):
		result_data = []
		wiki_cate_search_api = "http://zh.wikipedia.org/w/api.php?action=query&prop=categories&format=" + str(wiki_cate_format_type) + "&titles=" + str(wiki_query) 
		#print wiki_cate_search_api
		u = urllib2.urlopen(wiki_cate_search_api)
		soup = BeautifulSoup(u)
		#print soup
		for message in soup.findAll('cl'):
			result_data.append(message['title'][9:])
		
		if (result_data):
			return True
		else:
			return False

	# en_wiki_query_search_exist
	def en_wiki_query_search_exist(self, wiki_query = "Albert%20Einstein", wiki_cate_format_type = "xml"):
		wiki_query_search_api = "http://en.wikipedia.org/w/api.php?action=opensearch&format=" + str(wiki_cate_format_type) + "&search=" + str(wiki_query)
		u = urllib2.urlopen(wiki_query_search_api)
		soup = BeautifulSoup(u)
		#print soup
		for message in soup.findAll('text'):
			if (message.contents[0].lower() == wiki_query.replace("%20"," ").lower()):
				return True
		return False

	# en_ngram_seg_func
	def en_ngram_seg_func(self, query, max_ngram):
		data = []
		query_ary = query.split(" ")
		for ngram in range(1, max_ngram+1):
			for i in range(0,len(query_ary)-ngram+1):
				term = query_ary[i:i+ngram]
				data.append(" ".join(term))
		return data

	# en_ngram_to_wiki
	def en_ngram_to_wiki(self, data):
		find_data = []
		for i in range(0, len(data)):
			if (self.en_wiki_query_search_exist(data[i].replace(" ","%20"),"xml")):
				find_data.append(data[i])
		return find_data

	# zh_wiki_query_search_exist
	def zh_wiki_query_search_exist(self, wiki_query = "鼎泰豐", wiki_cate_format_type = "xml"):
		wiki_query_search_api = "http://zh.wikipedia.org/w/api.php?action=opensearch&format=" + str(wiki_cate_format_type) + "&search=" + str(wiki_query)
		u = urllib2.urlopen(wiki_query_search_api)
		soup = BeautifulSoup(u)
		for message in soup.findAll('text'):
			if (message.contents[0]!=''):
				return True
		return False

	# zh_ngram_seg_func
	def zh_ngram_seg_func(self, query, ngram):
		query_ary = []
		query = query.replace(" ","")
		query = re.sub('[%s]' % re.escape(string.punctuation), '', query)
		query = query.decode('utf-8')
		
		for i in range(0,len(query)-ngram+1):
			term = query[i:i+ngram]
			#print term
			term_quote = urllib.quote(str(term.encode('utf-8')))
			#print term_quote
			if (self.zh_wiki_query_search_exist(term_quote,"xml")):
				if (term != ''):
					query_ary.append(term)
		return query_ary

	# wiki_query_maximum_matching
	def wiki_query_maximum_matching(self, query_candidate):

		query_array_map = []
		query_array_clean = []

	  	for i in range(0, len(query_candidate)):
			query_array_map.append(0)

		for i in range(0, len(query_candidate)):
			for j in range(0, len(query_candidate)):
				if (i != j):
					if (query_candidate[i] != 0):
						if (query_candidate[j] != 0):
							if (query_candidate[i].find(query_candidate[j])!= -1):
								query_array_map[j] = 1
		
		for i in range(0, len(query_array_map)):
			if (query_array_map[i] == 0):
				if (query_candidate[i].find("。")==-1):
					query_array_clean.append(query_candidate[i])
		return query_array_clean

	# wiki_zh_ngram_seg_long_term_select
	def wiki_zh_ngram_seg_long_term_select(self, query, ngram_less):
		query_array = []
		for i in range(2, ngram_less+1):
			#curr_query = self.zh_ngram_seg_func(query, i)
			curr_query = self.extract_string_zh_part(query, i)
			for j in range(0, len(curr_query)):
				query_array.append(curr_query[j])
		return query_array

	# test
	def test(self, query="好吃港式飲茶", max_query_length=8):
		print "query = " + str(query)
		print "max_query_length = " + str(max_query_length)
		print "start wikipedia_class test"

		if (len(query) < max_query_length):
				max_query_length = len(query)
			
		wiki_query_cand = self.wiki_zh_ngram_seg_long_term_select(query.decode("UTF-8"), max_query_length)
		wiki_maximum_matching_ary = self.wiki_query_maximum_matching(wiki_query_cand)
		wiki_tagging = ",".join(wiki_maximum_matching_ary)
			
	# generate
	def generate(self, max_query_length=8):
		data = self.call_sql.sql_only_function("SELECT id, hash, query FROM " + str(self.db_table_query_log) + " WHERE crf_wiki_tag IS NULL OR crf_wiki_tag=''")
		for i in range(0, len(data)):
			print i
			curr_query = data[i][2]
			if (len(curr_query) < max_query_length):
				max_query_length = len(curr_query)
			wiki_query_cand = self.wiki_zh_ngram_seg_long_term_select(curr_query.decode("UTF-8"), max_query_length)
			wiki_maximum_matching_ary = self.wiki_query_maximum_matching(wiki_query_cand)

			wiki_tagging = ",".join(wiki_maximum_matching_ary)
			wiki_tagging = wiki_tagging.replace("。","")

			wiki_data = wiki_tagging.split(",")
			wiki_data_array = []

			for j in range(0, len(wiki_data)):
				if (wiki_data[j]!=''):
					wiki_data_array.append(wiki_data[j])

			wiki_tagging_done = ",".join(wiki_data_array)
			

			if (wiki_tagging_done == ""):
				self.call_sql.sql_only_function("UPDATE " + str(self.db_table_query_log) + " SET crf_wiki_tag='O' WHERE hash='" + str(data[i][1]) + "'")
			else:
				self.call_sql.sql_only_function("UPDATE " + str(self.db_table_query_log) + " SET crf_wiki_tag='" + str(wiki_tagging_done) + "' WHERE hash='" + str(data[i][1]) + "'")

