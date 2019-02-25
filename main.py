import requests

url = 'https://www.xkcd.com/info.0.json'

response = requests.get(url=url)
if response.ok:
  print(response.json()['num'])
