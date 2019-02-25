import requests
import random

def get_comics_total_qty():
  url = 'https://www.xkcd.com/info.0.json'
  response = requests.get(url=url)
  if response.ok:
    return response.json()['num']
  else:
    return None


def get_random_comics_number(comics_total_qty):
    if comics_total_qty is not None:
       return random.randint(1, comics_total_qty)
    else:
       return None
	
r = get_comics_total_qty()
print(get_random_comics_number(r))
