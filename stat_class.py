#!/usr/bin/python 
# -*- coding: utf-8 -*-

from __future__ import division
import re

class query_statistics_class:
    
    db_table_query_log = ""
    call_sql = ""

    def __init__(self, db_table_query_log, call_sql):
        self.db_table_query_log = db_table_query_log
        self.call_sql = call_sql
    
    # extract_string_zh_part
    def extract_string_zh_part(self, query = "台北鼎泰豐DANCE CLUB"):

        query_ary = []
        chinese_word = re.findall('[^A-Za-z0-9\ ]', query)
        chinese_word_ary = "".join(chinese_word)
        chinese_word_ary = chinese_word_ary.decode("utf8")

        return len(chinese_word_ary)

    # extract_string_en_part
    def extract_string_en_part(self, query = "台北鼎泰豐DANCE CLUB"):
        
        query_ary = []
        english_word = re.findall('[A-Za-z1-9]+', query)

        return len(english_word)

    # static_average_query_counter_of_each_query
    def static_average_query_counter_of_each_query(self):
        
        query_len_counter = 0
        data = self.call_sql.sql_only_function("SELECT id, query FROM " + str(self.db_table_query_log) + " WHERE goal!='0' AND mission!='0'")
        #print len(data)
        for i in range(0,len(data)):
            zh_cur_data = self.extract_string_zh_part(data[i][1])
            en_cur_data = self.extract_string_en_part(data[i][1])

            query_len_counter = query_len_counter + zh_cur_data + en_cur_data
        return query_len_counter/len(data)

    # static_max_length_query_counter_of_query_log
    def static_max_length_query_counter_of_query_log(self):
        query_len_counter = 0
        data = self.call_sql.sql_only_function("SELECT id, query FROM " + str(self.db_table_query_log) + " WHERE goal!='0' AND mission!='0'")
        
        for i in range(0,len(data)):
            zh_cur_data = self.extract_string_zh_part(data[i][1])
            en_cur_data = self.extract_string_en_part(data[i][1])

            curr_length = zh_cur_data + en_cur_data

            if (curr_length > query_len_counter):
                query_len_counter = curr_length
        return query_len_counter

    # static_min_length_query_counter_of_query_log
    def static_min_length_query_counter_of_query_log(self):
        query_len_counter = 999
        data = self.call_sql.sql_only_function("SELECT id, query FROM " + str(self.db_table_query_log) + " WHERE goal!='0' AND mission!='0'")
        
        for i in range(0,len(data)):
            zh_cur_data = self.extract_string_zh_part(data[i][1])
            en_cur_data = self.extract_string_en_part(data[i][1])

            curr_length = zh_cur_data + en_cur_data

            if (curr_length < query_len_counter):
                query_len_counter = curr_length
        return query_len_counter

    # static_en_average_queries_func
    def static_en_average_queries_func(self, target):
        data = self.call_sql.sql_only_function("SELECT COUNT(query) AS query_counter FROM " + str(self.db_table_query_log) + " WHERE " + str(target) + "!='0' GROUP BY " + str(target))
        counter = 0
        for i in range(0,len(data)):
            counter = counter + data[i][0]
        return counter/len(data)

    # static_en_max_queries_func
    def static_en_max_queries_func(self, target):
        data = self.call_sql.sql_only_function("SELECT COUNT(query) AS query_counter FROM " + str(self.db_table_query_log) + " WHERE " + str(target) + "!='0' GROUP BY " + str(target))
        counter = 0
        for i in range(0,len(data)):
            if (data[i][0] > counter):
                counter = data[i][0]
        return counter

    # static_en_min_queries_func
    def static_en_min_queries_func(self, target):
        data = self.call_sql.sql_only_function("SELECT COUNT(query) AS query_counter FROM " + str(self.db_table_query_log) + " WHERE " + str(target) + "!='0' GROUP BY " + str(target))
        counter = 999
        for i in range(0,len(data)):
            if (data[i][0] < counter):
                counter = data[i][0]
        return counter

    def static_all_users_session_count_func(self):
        data = self.call_sql.sql_only_function("SELECT COUNT(*) FROM " + str(self.db_table_query_log) + " GROUP BY anonid")
        return len(data)

    def static_all_search_log_count_func(self):
        data = self.call_sql.sql_only_function("SELECT COUNT(*) FROM " + str(self.db_table_query_log))
        return data[0][0]

    def static_goal_search_log_count_func(self):
        data = self.call_sql.sql_only_function("SELECT COUNT(*) FROM " + str(self.db_table_query_log) + " GROUP BY goal")
        return len(data)
    
    def static_mission_search_log_count_func(self):
        data = self.call_sql.sql_only_function("SELECT COUNT(*) FROM " + str(self.db_table_query_log) + " GROUP BY mission")
        return len(data)

    def static_intent_search_log_count_func(self):
        data = self.call_sql.sql_only_function("SELECT COUNT(*) FROM " + str(self.db_table_query_log) + " GROUP BY intent")
        return len(data)


    def test(self):
    
        print "### static of queries ###"
        print "static_average_query_counter_of_each_query = " + str(self.static_average_query_counter_of_each_query())
        print "static_max_length_query_counter_of_query_log = " + str(self.static_max_length_query_counter_of_query_log())
        print "static_min_length_query_counter_of_query_log = " + str(self.static_min_length_query_counter_of_query_log())
        print ""

        print "### static of goal ###"
        print "avg queries of goal = " + str(self.static_en_average_queries_func('goal'))
        print "max queries of goal = " + str(self.static_en_max_queries_func('goal'))
        print "min queries of goal = " + str(self.static_en_min_queries_func('goal'))
        print ""

        print "### static of mission ###"
        print "avg queries of mission = " + str(self.static_en_average_queries_func('mission'))
        print "max queries of mission = " + str(self.static_en_max_queries_func('mission'))
        print "min queries of mission = " + str(self.static_en_min_queries_func('mission'))
        print ""

        print "### static general ###"
        print "static total user session = " + str(self.static_all_users_session_count_func())
        print "static all search log count = " + str(self.static_all_search_log_count_func())
        print "static goal search log count = " + str(self.static_goal_search_log_count_func())
        print "static mission search log count = " + str(self.static_mission_search_log_count_func())
        print "static intent search log count = " + str(self.static_intent_search_log_count_func())




