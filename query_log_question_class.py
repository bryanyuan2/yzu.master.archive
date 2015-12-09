#encoding=utf-8

#!/usr/bin/python 
# -*- coding: utf-8 -*-

import random

from BeautifulSoup import BeautifulSoup
import urllib2
import re
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

#
# query_log_questions
#
class query_log_questions:

	ipeen_top_shops_url = "corpus/ipeen_top_shops"
	ipeen_url_rank_shop_const = "http://tw.ipeen.lifestyle.yahoo.net/rank/food/1?food="

	location = ["台北市", "台北東區", "內湖", "南港", "忠孝復興", "忠孝新生", "台北車站", "大直", "士林", "師大商圈", "內湖_737_商圈", "松山火車站", "永康街", "永康商圈", "古亭捷運站", "新店", "淡水", "萬華", "公館商圈", "台大", "師大", "文化大學", "政大", "景美", "木柵", "國父紀念館", "大安捷運站", "南京東路", "西門町", "板橋火車站", "板橋", "松山機場", "東門捷運站", "世新大學", "台北轉運站", "大安森林公園", "中和", "永和", "中和四號公園", "三重", "汐止", "科技大樓捷運站", "小南門捷運站", "東吳大學", "台南成功大學", "高雄中山大學", "東海大學", "新竹", "竹北", "中壢", "桃園火車站", "高雄火車站", "左營", "瑞豐夜市", "宜蘭", "新竹火車站", "南港", "忠孝東路", "台北捷運板南線沿線", "台北捷運木柵線沿線", "台北捷運新店線沿線", "台北捷運內湖沿線", "台北捷運中和線沿線", "輔仁大學", "內湖科學園區", "南港科學園區", "台北新光山越站前", "台大後門", "萬芳醫院", "台大醫院", "台北_101", "信義商圈", "中山捷運站", "天母", "中山北路", "八條通", "晴光市場", "華山藝文中心", "台北國際會議中心", "永春"]
	food_type = ["中式料理", "日式料理", "粵菜", "港式飲茶", "熱炒", "四川菜", "湘菜", "客家菜", "海鮮餐廳", "居酒屋", "日式拉麵", "生魚片", "壽司", "日式豬排", "大阪燒", "懷石料理", "韓式料理", "泰式料理", "越南料理", "星馬料理", "印度料理", "法式料理", "美式料理", "義式料理", "德式料理", "墨西哥料理", "西班牙料理", "炭烤串燒", "鐵板燒", "蒙古烤肉", "日式燒肉", "韓式燒肉", "火烤兩吃", "麻辣火鍋", "涮涮鍋", "羊肉爐", "薑母鴨", "石頭火鍋", "壽喜燒", "酒吧", "Lounge_Bar", "啤酒屋", "現場演奏餐廳", "食補藥膳餐廳", "景觀餐廳", "寵物餐廳", "懷舊主題", "運動主題餐廳", "冰淇淋餐廳", "剉冰店", "豆花專賣", "烘焙麵包店", "巧克力專賣", "無線網路咖啡廳", "中式早餐", "西式早餐", "中式_buffet", "日式_buffet", "西式_buffet", "自助餐", "漢堡", "炸雞", "披薩", "石鍋拌飯"]
	info = ["地址", "營業時間", "週六、週日有沒有開", "招牌菜", "有沒有負評", "有沒有好評", "幾篇網友的食評", "大概瀏覽一下就好", "聯絡電話"]
	opp = ["要多找點資訊", "附近其他商家資訊", "還要一個類似的備案", "附近可以續攤", "交通要方便", "可能會待很晚", "環境不要太吵雜", "氣氛裝潢不錯"]
	count = ["1 個", "2 個"]

	# generate_questions_navi_templete
	def generate_questions_navi_templete(self, n_sequences):
		
		for i in range(0, n_sequences):

			navi_templete = "找「location」附近的「count」「food_type」，條件是「opp」，我想知道「info」，如果沒有我也需要其他備案"

			location_rand = random.randrange(0, len(self.location))
			food_type_rand = random.randrange(0, len(self.food_type))
			info_rand = random.randrange(0, len(self.info))
			opp_rand = random.randrange(0, len(self.opp))
			count_rand = random.randrange(0, len(self.count))
			
			navi_templete = navi_templete.replace("location", self.location[location_rand-1])
			navi_templete = navi_templete.replace("food_type", self.food_type[food_type_rand-1])
			navi_templete = navi_templete.replace("info", self.info[info_rand-1])
			navi_templete = navi_templete.replace("opp", self.opp[opp_rand-1])
			navi_templete = navi_templete.replace("count", self.count[count_rand-1])
			navi_templete = navi_templete.replace(",", "")

			# question, location, food, type
			print navi_templete + "," + self.location[location_rand-1] + "," + self.food_type[food_type_rand-1] + ",0"

	# get_top_n_shops
	def get_top_n_shops(self, n_pages):
		
		for i in range(1,11):
			for j in range(1, n_pages):
				page = str(self.ipeen_url_rank_shop_const) + str(i) + "&city=0&p=" + str(j)
				u = urllib2.urlopen(page)
				soup = BeautifulSoup(u)
				get_titles = soup.findAll("a", {"class": "rankItem_store"})
				
				for title in get_titles:
					print title.contents[0]

	# generate_questions_target_templete
	def generate_questions_target_templete(self, n_sequences):
		
		data = []
		
		f_ipeen = file(self.ipeen_top_shops_url, "r")

		while 1:
			line = f_ipeen.readline()
			if not line:
				break
			else:
				data.append(line.replace("\n",""))

		for i in range(0, n_sequences):

			target_templete = "我想找「shop」，我想知道「info」，條件是「opp」，不然需要備案"

			info_rand = random.randrange(0, len(self.info))
			opp_rand = random.randrange(0, len(self.opp)) 
			data_rand = random.randrange(0, len(data))

			target_templete = target_templete.replace("info", self.info[info_rand-1])
			target_templete = target_templete.replace("opp", self.opp[opp_rand-1])
			target_templete = target_templete.replace("shop", data[data_rand-1])
			target_templete = target_templete.replace(",", "")

			# question, shop, type
			print target_templete + "," + data[data_rand-1] + ",1"


query_log_qs = query_log_questions()
	
query_log_qs.generate_questions_navi_templete(5000)
#query_log_qs.generate_questions_target_templete(5000)
