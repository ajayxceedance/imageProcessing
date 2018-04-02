from django.shortcuts import render
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import os,logging,datetime
import base64
import requests
import json
from PIL import Image
from colormap.colors import rgb2hex

# Create your views here.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILENAME = os.path.join(BASE_DIR,"imageApp/errorlog.log")
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)


class ImageComponents(viewsets.ViewSet):

	def create(self, request):
		try:
			# TEXT_DETECTION FROM IMAGE
			encoded_string = (request.data).get('base64')
			data = { "requests": [{"image": {"content":encoded_string},"features": [{"type": "TEXT_DETECTION"}]}]}
			data=json.dumps(data)
			r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCNHAv4uQDW2JJmaERfoCvrGVipxr_moww",data=data)
			response=json.loads(r.text)
			text_of_image = response['responses'][0]['textAnnotations'][0]['description']

			# DETECT LOGO FROM IMAGE
			data = { "requests": [{"image": {"content":encoded_string},"features": [{"type": "LOGO_DETECTION"}]}]}
			data=json.dumps(data)
			r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCNHAv4uQDW2JJmaERfoCvrGVipxr_moww",data=data)

			response=json.loads(r.text)
			vertices = response['responses'][0]['logoAnnotations'][0]['boundingPoly']['vertices']
			first_vertices = vertices[0]
			third_vertices = vertices[2]

			x1 = first_vertices['x']
			y1 = first_vertices['y']

			x2 = third_vertices['x']
			y2 = third_vertices['y']

			b = bytes(encoded_string,'utf-8')
			image_64_decode = base64.decodestring(b)
			image_result = open(BASE_DIR+"croping.png",'wb')
			image_result.write(image_64_decode)

			img = Image.open(BASE_DIR+"croping.png")
			img2 = img.crop((x1, y1, x2, y2))
			img2.save(BASE_DIR+"img2.png")

			# Here convert logo with base64 string       
			with open(BASE_DIR+"img2.png", "rb") as logo_file:
				encoded_logo = base64.b64encode(logo_file.read())
				encoded_logo = encoded_logo.decode('utf-8')


			# DETECT COLOR FROM IMAGE

			data = { "requests": [{"image": {"content":encoded_string},"features": [{"type": "IMAGE_PROPERTIES"}]}]}
			data=json.dumps(data)
			r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=AIzaSyCNHAv4uQDW2JJmaERfoCvrGVipxr_moww",data=data)

			response=json.loads(r.text)

			color_list = response['responses'][0]['imagePropertiesAnnotation']['dominantColors']['colors']
			length = len(color_list)

			modify_dict = {}
			for i in range(0,length):
				obj = color_list[i]
				pixelFraction_value = obj['pixelFraction']
				modify_dict[pixelFraction_value] = {'color':obj['color'],'score':obj['score']}

			pixels = list(modify_dict.keys())
			max_value = max(pixels)

			max_pixel = modify_dict.get(max_value)
			color_dict = max_pixel['color']

			final_value = rgb2hex(color_dict['red'],color_dict['blue'],color_dict['green'])

			final_json={"text":text_of_image,"Logo_with_base64":encoded_logo,"background_color":final_value}
			return Response(final_json,status=status.HTTP_201_CREATED)

		except Exception as error:
			now = datetime.datetime.now()
			error = str(now)+" ====> "+str(error)
			logging.debug(error)
			return Response("Please check your image it does not have text/logo",status=status.HTTP_400_BAD_REQUEST)
			
