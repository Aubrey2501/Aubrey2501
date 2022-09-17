import re
import requests
import json

url = "https://hotels4.p.rapidapi.com/locations/v2/search"
headers = {
	"X-RapidAPI-Key": "29f8962efbmsh0f278201ff9420ap16232fjsne20e6b9d4564",
	"X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# my_city = input('Введите регион поиска в латинской транскрипции: ')
my_city = 'Paris France'
querystring = {"query": my_city, "locale": "en_US", "currency": "USD"}


def request_to_api(url, headers, querystring):
	try:
		response = requests.get(url, headers=headers, params=querystring, timeout=10)
		if response.status_code == requests.codes.ok:
			return response
	except TimeoutError:
		print('Сервер не отвечает, попробуйте позднее')
		return dict()


def city_founding(response, city):
	pattern = r'(?<="CITY_GROUP",).+?[\]]'
	find = re.search(pattern, response.text)

	if find:
		suggestions = json.loads(f"{{{find[0]}}}")

		for dest_id in suggestions['entities']:  # Обрабатываем результат
			clear_destination = re.sub("<span class='highlighted'>", "", dest_id['caption'])
			clear_destination = re.sub("</span>", "", clear_destination)
			cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
	return cities


response = request_to_api(url, headers, querystring)
cities = list()
cities = city_founding(response, my_city)
for i_city in cities:
	print(i_city)



#
