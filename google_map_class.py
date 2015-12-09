#!/usr/bin/python 
# -*- coding: utf-8 -*-

import urllib
import urllib2
import json
from math import radians, cos, sin, asin, sqrt

class google_map_class:

	db_table_query_log = ""
	db_table_query_pair = ""
	call_sql = ""

	def __init__(self, db_table_query_log, db_table_query_pair, call_sql):
		self.db_table_query_log = db_table_query_log
		self.db_table_query_pair = db_table_query_pair
		self.call_sql = call_sql

	def get_geocoding_via_google_map(self, google_map_address = "師大"):
		
		google_map_api = "http://maps.googleapis.com/maps/api/geocode/json?address=" + urllib.quote(google_map_address) + "&sensor=false"
		u = urllib2.urlopen(google_map_api)
		google_map_data = json.load(u)
		u.close()

		get_lat = google_map_data['results'][0]['geometry']['location']['lat']
		get_lng = google_map_data['results'][0]['geometry']['location']['lng']
		
		return get_lat, get_lng

	def get_geocoding_haversine_distance(self, lat1, lon1, lat2, lon2):
		
		# http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
		
		# convert decimal degrees to radians 
		lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
		# haversine formula 
		dlon = lon2 - lon1 
		dlat = lat2 - lat1 
		a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
		c = 2 * asin(sqrt(a)) 
		km = 6367 * c
		return km

	def generate(self):
		
		data = self.call_sql.sql_only_function("SELECT id, hash, query, crf_iml_label FROM " + str(self.db_table_query_log) + " WHERE lat IS NULL OR lng IS NULL")
		
		for i in range(0, len(data)):
			if (data[i][3]):
				try:
					curr_query = data[i][3].replace(" ","").replace(","," ") + " 台灣"
					curr_query = curr_query.encode("utf-8")
					curr_lat, curr_lng = self.get_geocoding_via_google_map(curr_query)
					self.call_sql.sql_only_function("UPDATE " + str(self.db_table_query_log) + " SET lat='" + str(curr_lat) + "', lng='" + str(curr_lng) + "' WHERE hash='" + str(data[i][1]) + "'")
					print str(data[i][0]) + " = " + str(curr_lat) + ","  + str(curr_lng)
				except:
					continue