#!/usr/bin/python 
# -*- coding: utf-8 -*-
from __future__ import division

__author__ = "bryanyuan2",
__email__='bryanyuan2@gmail.com',


import os
from crf_confusion_matrix_class import crf_confusion_matrix_class

class classify_class:
    
    db_table_query_pair = ""
    call_sql = ""

    def __init__(self, db_table_query_pair, call_sql):
        self.db_table_query_pair = db_table_query_pair
        self.call_sql = call_sql
    
    def libsvm_train_data(self, folder, filename, n_fold, bool_balance):
        for i in range(0, n_fold):
            if (bool_balance == True):
                query = "./svm-train " + str(folder) + "/" + filename + "_balance_" + str(i) + ".train" + " " + str(folder) + "/" + filename + "_balance_" + str(i) + ".train.model"
                #print query
                os.system(query)
            else:
                query = "./svm-train " + str(folder) + "/" + filename + "_unbalance_" + str(i) + ".train" + " " + str(folder) + "/" + filename + "_unbalance_" + str(i) + ".train.model"
                #print query
                os.system(query)

    def trans_to_bio(self, test):
        
        #test = [1,0,0,0,1,0]
        bio_ary = []

        for i in range(0, len(test)):
            if (i==0):
                if (test[i] == "1"):
                    bio_ary.append("data_B")
                else:
                    bio_ary.append("data_B")
            else:
                if (test[i] == "1"):
                    bio_ary.append("data_B")
                else:
                    bio_ary.append("data_I")

        return bio_ary

    def libsvm_predict_data(self, folder, filename, n_fold, goal_or_mission, bool_balance):

        true_svm_recall = 0
        true_svm_precision = 0
        false_svm_recall = 0
        false_svm_precision = 0
        
        tp = 0
        fn = 0
        fp = 0
        tn = 0

        svm_mapping_ary_answer = []
        svm_mapping_ary_predict = []


        #
        check_data_filename = "check" + ".libsvm"

        f_check_ary = []
        f_check_intent_ary = []
        
        f_check_read = open(str(folder) + "/" + check_data_filename + "_unbalance" , "r")
        
        f_check_correct = file(str(folder) + "/" + check_data_filename + "_unbalance_correct" , "w")
        f_check_wrong = file(str(folder) + "/" + check_data_filename + "_unbalance_wrong" , "w")

        f_check_intent = open(str(folder) + "/test.libsvm_intent" , "r")

        while 1:
            line = f_check_read.readline()
            intent_line = f_check_intent.readline()

            if not line:
                break
            else:
                f_check_ary.append(line.replace("\n",""))
                f_check_intent_ary.append(intent_line.replace("\n", ""))



        for i in range(0, n_fold):
            if (bool_balance == True):
                query = "./svm-predict " + str(folder) + "/" + filename + "_balance_" + str(i) + ".test" + " " + str(folder) + "/" + filename + "_balance_" + str(i) + ".train.model" + " " + str(folder) + "/" + filename + "_balance_" + str(i) + ".train.output"
                #print query
                os.system(query)
            else:
                query = "./svm-predict " + str(folder) + "/" + filename + "_unbalance_" + str(i) + ".test" + " " + str(folder) + "/" + filename + "_unbalance_" + str(i) + ".train.model" + " " + str(folder) + "/" + filename + "_unbalance_" + str(i) + ".train.output"
                #print query
                os.system(query)


        for i in range(0, n_fold):
            
            f_answer_url = str(folder) + "/" + filename + "_unbalance_" + str(i) + ".test"
            f_predict_url = str(folder) + "/" + filename + "_unbalance_" + str(i) + ".train.output"

            f_answer = file(f_answer_url, "r")
            f_predict = file(f_predict_url, "r")

            while 1:
                f_answer_line = f_answer.readline()
                f_answer_line = f_answer_line.replace("\n", "")

                f_predict_line = f_predict.readline()
                f_predict_line = f_predict_line.replace("\n", "")
                
                if not f_answer_line:
                    break
                else:
                    f_answer_ary = f_answer_line.split(" ")
                    svm_mapping_ary_answer.append(f_answer_ary[0])
                    svm_mapping_ary_predict.append(f_predict_line[0])
        


        answer_ary = self.trans_to_bio(svm_mapping_ary_answer)
        predict_ary = self.trans_to_bio(svm_mapping_ary_predict)

        f_bio = file(str(folder) + "/" + check_data_filename + "_bio" , "w")
        
        for i in range(0, len(answer_ary)):

            if (f_check_intent_ary[i] == "0"):
                f_bio.write(answer_ary[i] + "\t" + predict_ary[i] + "\n" + "\n")
            else:
                f_bio.write(answer_ary[i] + "\t" + predict_ary[i] + "\n")

        f_bio.close()

        ###
        
        for i in range(0, len(svm_mapping_ary_answer)):
            if (svm_mapping_ary_predict[i] == '1'):
                if (svm_mapping_ary_answer[i] == '1'):
                    tp = tp + 1
                    f_check_correct.write(f_check_ary[i] + "\n")

            if (svm_mapping_ary_predict[i] == '0'):
                if (svm_mapping_ary_answer[i] == '1'):
                    fn = fn + 1
                    f_check_wrong.write(f_check_ary[i] + "\n")
            
            if (svm_mapping_ary_predict[i] == '0'):
                if (svm_mapping_ary_answer[i] == '0'):
                    tn = tn + 1
                    f_check_correct.write(f_check_ary[i] + "\n")
            
            if (svm_mapping_ary_predict[i] == '1'):
                if (svm_mapping_ary_answer[i] == '0'):
                    fp = fp + 1
                    f_check_wrong.write(f_check_ary[i] + "\n")

        if (tp+fn == 0):
            true_svm_recall = 0
        else:
            true_svm_recall = tp/(tp+fn)
        
        if (tp+fp == 0):
            true_svm_precision = 0
        else:
            true_svm_precision = tp/(tp+fp)

        print "==="
        print str(goal_or_mission) + " 1 Precision = " + str(true_svm_precision)
        print str(goal_or_mission) + " 1 Recall = " + str(true_svm_recall)
        print str(goal_or_mission) + " 1 F1 = " + str((2*true_svm_precision*true_svm_recall)/(true_svm_precision + true_svm_recall))
        
        print "(tp, fp, tn, fn) = " + "(" + str(tp) + "," + str(fp) + "," + str(tn) + "," + str(fn) + ")"
        

        f_check_correct.close()
        f_check_wrong.close()
        
        ###


    # svm_training_data_generator
    def svm_training_data_generator(self, folder, feature_list, prediction_type, bool_balance, same_session):

        crf_state_change = ["NONE", "SAME", "NEW", "INSERT", "DELETE", "MODIFY"]

        print "start svm train data generation"

        feature_list_data= ",".join(feature_list)
        feature_list_data = "same_" + prediction_type + "," + feature_list_data
        
        #data_filename = str(self.db_table_query_pair) + "." + str(feature_list_data) + ".libsvm"
        data_filename = "test" + ".libsvm"
        check_data_filename = "check" + ".libsvm"

        if (bool_balance == True):

            f = file(str(folder) + "/" + data_filename + "_balance" , "w")

            std_count = 0

            data_true_count = self.call_sql.sql_only_function("SELECT COUNT(*) AS count FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 0")
            data_false_count = self.call_sql.sql_only_function("SELECT COUNT(*) AS count FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 1")
            
            if (data_true_count[0][0] > data_false_count[0][0]):
                std_count = data_false_count[0][0]
            else:
                std_count = data_true_count[0][0]

            if (same_session == True):
                data_true = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 0 AND anonid1=anonid2 LIMIT " + str(std_count))
            else:
                data_true = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 0 LIMIT " + str(std_count))

            if (same_session == True):
                data_false = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 1 AND anonid1=anonid2 LIMIT " + str(std_count))
            else:
                data_false = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair) + " WHERE " + str("same_" + prediction_type) + " = 1 LIMIT " + str(std_count))
        
            
            for i in range(0,len(data_true)):
                f.write(str(int(round(data_true[i][0]))) + " ")
                for j in range(1,len(data_true[i])):
                    #
                    feature_val = data_true[i][j]
                    for k in range(0, len(crf_state_change)):
                        if (feature_val == crf_state_change[k]):
                            feature_val = k
                    f.write(str(j) + ":" + str(feature_val) + " ")
                f.write("\n")

            for i in range(0,len(data_false)):
                f.write(str(int(round(data_false[i][0]))) + " ")
                for j in range(1,len(data_false[i])):
                    #
                    feature_val = data_false[i][j]
                    for k in range(0, len(crf_state_change)):
                        if (feature_val == crf_state_change[k]):
                            feature_val = k
                    f.write(str(j) + ":" + str(feature_val) + " ")
                f.write("\n")

        else:

            f = file(str(folder) + "/" + data_filename + "_unbalance" , "w")

            f_intent = file(str(folder) + "/" + data_filename + "_intent" , "w")
            f_check = file(str(folder) + "/" + check_data_filename + "_unbalance" , "w")

            if (same_session == True):
                data = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair) + " WHERE anonid1=anonid2")
                label  = self.call_sql.sql_only_function("SELECT id, q1, q2, gold_ih, crf_ih_state, gold_iml, crf_iml_state, gold_imt, crf_imt_state, " + "same_" + str(prediction_type) + " FROM " + str(self.db_table_query_pair) + " WHERE anonid1=anonid2")
                intent  = self.call_sql.sql_only_function("SELECT same_intent FROM " + str(self.db_table_query_pair) + " WHERE anonid1=anonid2")
            else:
                data = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair))
                label  = self.call_sql.sql_only_function("SELECT id, q1, q2, gold_ih, crf_ih_state, gold_iml, crf_iml_state, gold_imt, crf_imt_state FROM " + str(self.db_table_query_pair))
                intent  = self.call_sql.sql_only_function("SELECT same_intent FROM " + str(self.db_table_query_pair))
            
            for i in range(0,len(data)):
                f.write(str(int(round(data[i][0]))) + " ")

                f_intent.write(str(intent[i][0]) + "\n")
                f_check.write(str(label[i][0]) + "\t" + str(label[i][1]) + "\t | \t" + str(label[i][2]) + "\t" + str(label[i][3]) + ":" + str(label[i][4]) + "\t" + str(label[i][5]) + ":" + str(label[i][6]) + "\t" + str(label[i][7]) + ":" + str(label[i][8]) + "\t " + str(label[i][9]) + "\n")

                for j in range(1,len(data[i])):
                    #
                    feature_val = data[i][j]
                    for k in range(0, len(crf_state_change)):
                        if (feature_val == crf_state_change[k]):
                            feature_val = k
                    f.write(str(j) + ":" + str(feature_val) + " ")
                f.write("\n")

        f.close()
        f_intent.close()
        f_check.close()
        
        return data_filename

    # svm svm_train_with_v_output
    def svm_train_with_v_output(self, n_fold, libsvm_filename, bool_balance):
        
        print "start svm train with " + str(n_fold) + "-fold validation"

        if (bool_balance == True):
            query = "./svm-train -v " + n_fold + " " + "result/" + libsvm_filename + "_balance" + " > " + "result/" + libsvm_filename + "_balance.output"
            print query
            os.system(query)
        else:
            query = "./svm-train -v " + n_fold + " " + "result/" + libsvm_filename + "_unbalance" + " > " + "result/" + libsvm_filename + "_unbalance.output"
            print query
            os.system(query)


    # crf_generate_templete
    def crf_generate_templete(self, feature_list, filename):

        feat_count = len(feature_list)
        single_count = 0
        f = file(filename + ".templete", "w")

        f.write("# Unigram\n")
        
        for i in range(0, feat_count):
            if (i < 10):
                f.write("U0" + str(i) + ":%x[0," + str(i) + "]\n")
            else:
                f.write("U" + str(i) + ":%x[0," + str(i) + "]\n")
            single_count = single_count + 1

        f.write("\n")

        for i in range(0, feat_count):
            if (single_count < 10):
                f.write("U0" + str(single_count) + ":%x[-1," + str(i) + "]/%x[0," + str(i) + "]\n")
            else:
                f.write("U" + str(single_count) + ":%x[-1," + str(i) + "]/%x[0," + str(i) + "]\n")

            single_count = single_count + 1

        f.write("\n")
        f.write("# Bigram\n")
        f.write("B\n")

    # crf_train_and_test_seperate_n_fold
    def crf_train_and_test_seperate_n_fold(self, filename, n_fold):

        data_ary = []
        check_counter = 0
        check_seperate_space = False

        f_scan = file(filename, "r")
        f_sep = file(filename, "r")
        
        w_train = open(filename + ".train", "w")
        w_test = open(filename + ".test", "w")

        while 1:
            line = f_scan.readline()
            if not line:
                break
            else:
                data_ary.append(line.replace("\n",""))

        total_num = len(data_ary)
        test_num = len(data_ary)/n_fold

        
        while 1:
            line = f_sep.readline()
            if not line:
                break
            else:
                if (check_counter > test_num):
                    
                    if (line == "\n"):
                        check_seperate_space = True
                    if (check_seperate_space == False):
                        w_test.write(line)
                    else:
                        w_train.write(line)
                else:
                    w_test.write(line)

                check_counter = check_counter + 1

    # crf_train_and_test_output
    def crf_train_and_test_output(self, crf_filename):
        os.system("crf_learn " + str(crf_filename) + ".templete" + " " + str(crf_filename) + ".train" + " " + str(crf_filename) + ".model")
        os.system("crf_test -m " + str(crf_filename) + ".model" + " " + str(crf_filename) + ".test" + " > " + str(crf_filename) + ".output")    

    # crf_confusion_matrix_output
    def crf_confusion_matrix_output(self, crf_test_result_filename = "crf.data", correct_label_pool = ["B","I","O"]):

        crf_confusion = crf_confusion_matrix_class(correct_label_pool, crf_test_result_filename)
            
        crf_confusion.confusion_matrix_print_func()

    def crf_training_data_generator(self, feature_list, prediction_type):

        feature_list_data = ",".join(feature_list)
        feature_list_data = "same_" + prediction_type + "," + feature_list_data
        
        data_filename = str(self.db_table_query_pair) + "." + str(feature_list_data) + ".crf"
        
        f = file(data_filename, "w")

        data = self.call_sql.sql_only_function("SELECT " + str(feature_list_data) + " FROM " + str(self.db_table_query_pair))
        day_check = self.call_sql.sql_only_function("SELECT last_query_q2 FROM " + str(self.db_table_query_pair))

        curr = False

        for i in range(0,len(data)):
            if (i == 0):
                curr = data[i][0]
            for j in range(1,len(data[i])):
                if (j == len(data[i])-1):
                    if (i != 0):
                        if (curr == 1):
                            if (data[i][0] == 1):
                                f.write(str(data[i][j]) + " " + "I" + "\n")
                            else:
                                f.write(str(data[i][j]) + " " + "O" + "\n")
                        else:
                            if (data[i][0] == 1):
                                f.write(str(data[i][j]) + " " + "B" + "\n")
                            else:
                                f.write(str(data[i][j]) + " " + "O" + "\n")
                    else:
                        if (data[i][0] == 1):
                            f.write(str(data[i][j]) + " " + "B" + "\n")
                        else:
                            f.write(str(data[i][j]) + " " + "O" + "\n")
                    curr = data[i][0]
                    if (day_check[i][0] == 1):
                        f.write("\n")
                else:
                    f.write(str(data[i][j]) + " ")
                
        f.close()
        
        return data_filename


