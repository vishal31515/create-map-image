import os
import json
import shutil
import random
import requests
import sys, fitz
import numpy as np
import pandas as pd
import matplotlib.cm
import seaborn as sns
from datetime import date
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from matplotlib.patches import Polygon
from matplotlib.colors import Normalize
from mpl_toolkits.basemap import Basemap
from country_boundings import region_boundings
from matplotlib.collections import PatchCollection


class CreateMapPdf:
	headers = {"Authorization": "xxxxxxx-xxxxx"}
	base_url = "xxxxx-xxx"

	"""docstring for CreateMapPdf"""
	def __init__(self):
		super(CreateMapPdf, self).__init__()
		# self.create_image()

	def parse_url(self):
		try:
			params = "?query={%22measures%22:[%22E5Swvl2Alerts.countd%22],%22timeDimensions%22:[{%22dimension%22:%22E5Swvl2Alerts.dates%22,%22dateRange%22:%22Last%20week%22}],%22order%22:{%22E5Swvl2Alerts.countd%22:%22desc%22},%22dimensions%22:[%22E5Swvl2Alerts.level0%22,%22E5Swvl2Alerts.level1%22,%22E5Swvl2Alerts.level2%22]}"

			html = requests.get(self.base_url+params, headers=self.headers)
			result = html.json()
			print(result)
		except Exception as e:
			raise e


	def read_json(self):
		try:
			for root,dirs,files in os.walk('json'):
				for filename in files:
					lng_list = []
					lat_list = []
					if filename.endswith(".json"):
						path = root+'/'+filename
						f = open(path,)
						data = json.load(f)
						for i in data['features']:
							for k,j in enumerate(i['geometry']['coordinates']):
								try:
									if isinstance(j[k][0],list):
										pass
									else:
										lat_list.append(j[k][0])
										lng_list.append(j[k][1])
								except IndexError:
									pass
						f.close()

						""" Get location from first lat/long """
						first_lat = lat_list[0]
						first_lng = lng_list[0]
						geolocator = Nominatim(user_agent="geoapiExercises")
						location = geolocator.reverse(str(first_lng)+","+str(first_lat),language='en')
						address = location.raw['address']
						country = address.get('country', '')
						country_code = address.get('country_code').upper()
						print(country_code,'country_code')
						""" converted list of lat/longs to tuple for passing to coordinates """
						lat_list = tuple(lat_list)
						lng_list = tuple(lng_list)

						region_coordinates = region_boundings(country_code)
						fig, ax = plt.subplots()
						earth = Basemap(ax=ax,llcrnrlat=region_coordinates[1][1],
										urcrnrlat=region_coordinates[1][3],llcrnrlon=region_coordinates[1][0],
		            					urcrnrlon=region_coordinates[1][2])
						earth.bluemarble()
						earth.drawcoastlines(color='#556655', linewidth=0.5)
						coordinates = list(zip(lat_list, lng_list))

						""" save plotted maps into images """
						for i in coordinates:
							x,y = i
							ax.scatter(x, y, 
									c='red', alpha=0.5, zorder=10)
						filename = filename.split(".json",1)[0]
						ax.set_xlabel("Map for "+country)
						fig.savefig('images'+'/'+filename+'.png')
					
					else:
						print("Not a json file",filename)
						pass

		except Exception as e:
			raise e

	""" convert all images into pdf file """
	def convert_to_pdf(self):
		try:
			imglist = []
			date_today = date.today()
			random_number = random.randint(1111,10000)
			for root,dirs,files in os.walk('images'):
				for filename in files:
					if filename.endswith(".png"):
						img_path = root+'/'+filename
						imglist.append(img_path)
					else:
						print("Not a image file",filename)
						pass

			if imglist:
				doc = fitz.open()
				for i, f in enumerate(imglist):
					img = fitz.open(f)
					rect = img[0].rect
					pdfbytes = img.convertToPDF()
					img.close()
					imgPDF = fitz.open("pdf", pdfbytes)
					page = doc.newPage(width = rect.width,
							height = rect.height)
					page.showPDFpage(rect, imgPDF, 0) 
				doc.save("pdfs/final_pdf"+str(date_today)+"-"+str(random_number)+".pdf")

				""" move images after converted to pdf file"""
				for _ in imglist:
					img_name = _.split("/",1)[1]
					shutil.move(os.path.join('images/', img_name), os.path.join('converted_images/', img_name))

			else:
				print('No image found.')

		except Exception as e:
			raise e


if __name__ == '__main__':
	obj = CreateMapPdf()
	obj.read_json()
	obj.convert_to_pdf()
