#!/usr/bin/python 
# -*- coding: utf-8 -*-

__author__ = "bryanyuan2",
__email__='bryanyuan2@gmail.com',

import sys
import os
from mysql_class import mysql
from query_class import edit_distance_feat_query_class
from query_class import llr_feat_query_class
from query_class import query_preprocessing
from query_class import ckip_tagging_class
from query_class import yahoo_life_plus_class
from stat_class import query_statistics_class
from classify_class import classify_class
from query_class import intent_tagging_class
from wikipedia_class import wikipedia_class
from google_map_class import google_map_class
from query_class import yahoo_boss_api_class
from query_class import taiwan_road_class

from datetime import datetime
import time
import random

from svm_confusion_matrix_class import svm_confusion_matrix_class

import constant

reload(sys)
sys.setdefaultencoding('utf-8')

# setting 
balance_bool = False
crf_correct_label = ["B", "I", "O"]
sample_query = "台北鼎泰豐分店"
max_query_matching_length = 8
n_folding = 10
crf_correct_label = ["IH_B", "IH_I", "IM:Type_B", "IM:Type_I", "IM:Location_B", "IM:Location_I", "O"]

svm_folder = "result"
test_folder = "test"

# edit + time
#feature_list = ['feat_lev','feat_edlevGT2','feat_char_pov','feat_char_suf','feat_word_pov','feat_word_suf','feat_commonw','feat_wordr','feat_inter_query_time','feat_time_diff']

# time
#feature_list = ['feat_inter_query_time','feat_time_diff']

# en_edit
#feature_list = ['feat_lev','feat_edlevGT2','feat_char_pov','feat_char_suf','feat_word_pov','feat_word_suf','feat_commonw','feat_wordr']

# zh_edit
#feature_list = ['feat_lev','feat_edlevGT2','feat_word_pov','feat_word_suf','feat_commonw','feat_wordr']

# after
#feature_list = ['crf_ih_state','crf_imt_state','crf_iml_state']


# feat_search_result_50
#feature_list = ['feat_search_result_50']

# baseline
#feature_list = ['baseline_time', 'feat_commonw']

# llr
#feature_list = ['feat_nsubst_X_q1', 'feat_nsubst_X_q2', 'feat_nsubst_q2_X', 'feat_pq12', 'feat_peos_q2', 'feat_entropy_X_q1', 'feat_entropy_q1_X', 'feat_p_change']

# state of the art
#feature_list = ['feat_lev', 'feat_wordr', 'feat_peos_q2', 'feat_search_result_50', 'feat_time_diff', 'feat_nsubst_X_q2']

call_sql = mysql(constant.DB_HOST, constant.DB_USER, constant.DB_PASS, constant.DB_NAME)


def shift_time_original():
	data = call_sql.sql_only_function("SELECT id, _query_time, goal, mission FROM query_log_sim_yahoo_life")
	rand_pre = 0
	for i in range(0, len(data)):

		rand_goal = random.randint(0,180)
		rand_mission = random.randint(90,240)

		date_temp = datetime.strptime(str(data[i][1]), '%Y-%m-%d %H:%M:%S')
		
		unix_time = time.mktime(date_temp.timetuple())

		if (i < len(data)-1):
			if (data[i][3] != data[i+1][3]):
				unix_time = unix_time + rand_goal + rand_pre
				rand_pre = rand_pre + rand_goal + rand_mission
			else:
				unix_time = unix_time + rand_goal + rand_pre
				rand_pre = rand_pre + rand_goal

		cur =  datetime.fromtimestamp(unix_time) 

		call_sql.sql_only_function("UPDATE query_log_sim_yahoo_life SET query_time='" + str(cur) + "' WHERE id='" + str(data[i][0]) + "'")

def main_preprocessing():
	
	# query_preprocessing
	q_processing = query_preprocessing(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	q_processing.generate_query_pairs()
	
	# edit_distance_feat_query_class
	ed_query = edit_distance_feat_query_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	ed_query.zh_generate()
	
	# llr_feat_query_class
	llr_query = llr_feat_query_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	llr_query.generate()
	
	# yahoo boss 
	boss_query = yahoo_boss_api_class(constant.OAUTH_CONSUMER_KEY, constant.OAUTH_CONSUMER_SECRET, constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	boss_query.generate_query_pair()

	# taiwan road name
	taiwan_road_query = taiwan_road_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_TAIWAN_ROAD, call_sql)
	taiwan_road_query.generate()

	generate_gold_standard()

def main_func_test():
	
	# edit_distance_feat_query_class
	edit_distance_feat_query_class = edit_distance_feat_query_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	edit_distance_feat_query_class.zh_test("台北 鼎泰豐", "台北鼎泰豐")
	edit_distance_feat_query_class.en_test("this is a book", "this book is mine ha")

	# llr_feat_query_class
	llr_feat_query_class = llr_feat_query_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	llr_feat_query_class.test("guiness","encyclopedia")

def main_statistics():

	# query_statistics_class
	query_statistics= query_statistics_class(constant.DB_TABLE_QUERY_LOG, call_sql)
	query_statistics.test()


def main_libsvm_predict():

	# goal
	print "start libsvm in goal boundray prediction"
	cc_goal = classify_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	cc_goal_filename = cc_goal.svm_training_data_generator(svm_folder, feature_list, "goal", balance_bool)
	cc_goal.svm_train_with_v_output(constant.N_FOLD, cc_goal_filename, balance_bool)

	# mission
	print "start libsvm in mission boundray prediction"
	cc_mission = classify_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	cc_mission_filename = cc_mission.svm_training_data_generator(svm_folder, feature_list, "mission", balance_bool)
	cc_mission.svm_train_with_v_output(constant.N_FOLD, cc_mission_filename, balance_bool)

def main_crf_predict(n_fold):

	# goal
	crf_test = classify_class(constant.DB_TABLE_QUERY_PAIR, call_sql)
	cc_goal_filename = crf_test.crf_training_data_generator(feature_list, "goal")
	crf_test.crf_train_and_test_seperate_n_fold(cc_goal_filename, n_fold)
	crf_test.crf_generate_templete(feature_list, cc_goal_filename)
	crf_test.crf_train_and_test_output(cc_goal_filename)
	crf_test.crf_confusion_matrix_output(cc_goal_filename + ".output", crf_correct_label)

def zh_yahoo_shop_query():
	yahoo_query = yahoo_life_plus_class(constant.DB_TABLE_YAHOO_LIFE_PLUS_SHOP,constant.DB_TABLE_QUERY_LOG, call_sql)
	#yahoo_query.test(u"師大 中式早餐 續攤", 8)
	yahoo_query.generate(max_query_matching_length)

def taiwan_road_query():
	taiwan_road_query = taiwan_road_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_TAIWAN_ROAD, call_sql)
	taiwan_road_query.generate()
	
def zh_wiki_query():
	wiki_query = wikipedia_class(constant.DB_TABLE_QUERY_LOG, call_sql)
	#wiki_query.test()
	wiki_query.generate(max_query_matching_length)
	
def zh_ckip_query():
	ckip_query = ckip_tagging_class(constant.CKIP_USERNAME, constant.CKIP_PASSWORD, constant.DB_TABLE_QUERY_LOG, call_sql)
	ckip_query.generate()
	#print ckip_query.ckip_segmenter("my thai")

def google_map_query():
	# google_map_query
	google_map_query = google_map_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	google_map_query.generate()
	#print google_map_query.get_geocoding_via_google_map()
	#print google_map_query.get_geocoding_haversine_distance(53.3205, -1.7297, 53.3186, -1.6997)

def yahoo_boss_query():
	boss_query = yahoo_boss_api_class(constant.OAUTH_CONSUMER_KEY, constant.OAUTH_CONSUMER_SECRET, constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	boss_query.generate()
	#boss_query.generate_query_pair()

def crf_state_change():
	svm_query = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	svm_query.crf_noun_predict_generate()

def crf_noun_automatically():


	# L + Y + S
	#crf_feature_list = ["crf_pos_tag", "crf_yahoo_tag", "crf_road_tag", "noun"]
	crf_feature_list = ["crf_pos_tag", "crf_yahoo_tag", "noun"]
	
	# L + Y
	#crf_feature_list = ["crf_yahoo_tag", "crf_road_tag", "noun"]
	
	# L + S
	#crf_feature_list = ["crf_pos_tag", "noun"]
	
	# Y + S
	#crf_feature_list = ["crf_yahoo_tag", "crf_pos_tag", "crf_road_tag"]

	all_label = ["IH", "IM:Location", "IM:Type"]

	crf_noun_n_fold = 10
	crf_noun_folder = "crf_noun_result"

	crf_tagging = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	
	crf_noun_filename = crf_tagging.crf_training_noun_generator(crf_noun_folder, crf_feature_list)
	crf_noun_filename = crf_tagging.crf_training_noun_replacer(crf_noun_folder, crf_noun_filename, crf_feature_list)
	
	print crf_noun_filename
	
	crf_tagging.crf_n_fold_sql_select(crf_noun_folder, crf_noun_n_fold, crf_noun_filename)
	crf_tagging.crf_noun_generate_templete(crf_noun_folder, crf_feature_list, crf_noun_filename)
	crf_tagging.crf_n_fold_train_and_test_output(crf_noun_folder, crf_noun_n_fold, crf_noun_filename)
	
	crf_tagging.crf_n_fold_confusion_matrix_output(crf_noun_folder, crf_noun_filename, crf_correct_label, crf_noun_n_fold)
	#crf_tagging.crf_noun_state(crf_noun_folder, "dataset")
	crf_tagging.modify_crf_state_left_right_all_boundray(crf_noun_folder, "dataset", all_label)
	
	crf_tagging.crf_output_correct_wrong_mapping_result()
	
def svm_automatically(folder, feature_list, n_folding, goal_or_mission, balance_bool, same_session):
	
	svm_query = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	svm_classify = classify_class(constant.DB_TABLE_QUERY_PAIR, call_sql)

	svm_filename = svm_classify.svm_training_data_generator(folder, feature_list, goal_or_mission, balance_bool, same_session)
	
	# n fold 
	#svm_query.svm_n_fold_sql_select(folder, n_folding, svm_filename, balance_bool)
	#svm_classify.libsvm_train_data(folder, svm_filename, n_folding, balance_bool)
	#svm_classify.libsvm_predict_data(folder, svm_filename, n_folding, goal_or_mission, balance_bool)

	# n sets
	replacement = False
	svm_query.svm_n_sets_sql_select(folder, n_folding, svm_filename, balance_bool, replacement)
	svm_classify.libsvm_train_data(folder, svm_filename, n_folding, balance_bool)
	svm_classify.libsvm_predict_data(folder, svm_filename, n_folding, goal_or_mission, balance_bool)

	#replacement = True
	#svm_query.svm_n_sets_sql_select(folder, n_folding, svm_filename, balance_bool, replacement)
	#svm_classify.libsvm_train_data(folder, svm_filename, n_folding, balance_bool)
	#svm_classify.libsvm_predict_data(folder, svm_filename, n_folding, goal_or_mission, balance_bool)



def generate_gold_standard():
	crf_tagging = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	crf_tagging.gold_standard()

def check_data_update():
	#yahoo_boss_query()
	zh_yahoo_shop_query()
	#zh_ckip_query()
	#generate_gold_standard()

def yahoo_clean_shop():
	yahoo_shop_query = yahoo_life_plus_class(constant.DB_TABLE_YAHOO_LIFE_PLUS_SHOP,constant.DB_TABLE_QUERY_LOG, call_sql)
	yahoo_shop_query.extract_clean_shop()

def run():
	
	same_session = True

	# all
	#feature_list = ['crf_ih_state','crf_imt_state','crf_iml_state', 'baseline_time', 'feat_commonw', 'feat_search_result_50', 'feat_lev','feat_word_pov','feat_word_suf','feat_wordr', 'feat_nsubst_X_q1', 'feat_nsubst_X_q2', 'feat_nsubst_q2_X', 'feat_pq12', 'feat_peos_q2', 'feat_entropy_X_q1', 'feat_entropy_q1_X', 'feat_p_change', 'feat_inter_query_time','feat_time_diff']

	# gold standard
	#feature_list = ['gold_ih','gold_imt','gold_iml']
	
	# our
	#feature_list = ['crf_ih_state','crf_imt_state','crf_iml_state']

	# baseline 
	#feature_list = ['baseline_time', 'feat_commonw', 'feat_search_result_50']

	# baseline best goal
	#feature_list = ['feat_lev', 'feat_search_result_50', 'feat_wordr', 'feat_word_suf', 'feat_word_pov', 'feat_nsubst_X_q1']
	
	# baseline best mission
	#feature_list = ['feat_lev', 'feat_search_result_50', 'feat_wordr', 'feat_word_suf', 'feat_word_pov', 'feat_nsubst_X_q1']

	# our + fselect
	feature_list = ['feat_lev', 'feat_wordr', 'feat_word_pov', 'feat_commonw', 'feat_search_result_50', 'feat_inter_query_time', 'feat_entropy_q1_X', 'crf_ih_state', 'crf_iml_state', 'crf_imt_state']

	# new our + fselect + mission
	#feature_list = ['feat_wordr', 'feat_commonw', 'feat_lev', 'feat_inter_query_time', 'feat_word_pov', 'feat_search_result_50', 'crf_ih_state', 'crf_iml_state', 'crf_imt_state', 'feat_word_suf']

	# new our + fselect + goal
	#feature_list = ['feat_lev', 'feat_wordr', 'feat_word_pov', 'feat_commonw', 'feat_search_result_50', 'crf_ih_state', 'crf_imt_state', 'crf_iml_state', 'feat_pq12']

	svm_query = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)	
	svm_automatically(test_folder, feature_list, 30, "goal", False, same_session)

	all_label = ["data"]
	crf_tagging = intent_tagging_class(constant.DB_TABLE_QUERY_LOG, constant.DB_TABLE_QUERY_PAIR, call_sql)
	crf_tagging.modify_crf_state_left_right_all_boundray_without_merge("test", "check.libsvm_bio", all_label)
	


#crf_state_change()



#main_preprocessing()
#taiwan_road_query()
#run()
#check_data_update()
crf_noun_automatically()
#main_statistics()
#google_map_query()
#shift_time_original()
