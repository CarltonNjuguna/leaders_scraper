import re
import json
import requests
from bs4 import BeautifulSoup

cache = {}
def hashable_cache(f):
    def inner(url, session):
        if url not in cache:
            cache[url] = f(url, session)
        return cache[url]
    return inner

@hashable_cache
def get_first_paragraph(wikipedia_url,s):
   print(wikipedia_url)
   soup = BeautifulSoup(s.get(wikipedia_url).text, 'html.parser')
   soup.prettify()
   for paragraph in soup.find_all('p'):
      if paragraph.find('b') :
        return re.sub("\[(.*?)\]", "", paragraph.text).replace("\n", "")

def get_leaders():
    leaders_dict = {}
    url = "https://country-leaders.herokuapp.com"
    countries_u, cookies_u, leaders_u  = url + "/countries", url + "/cookie", url + "/leaders" 
    s = requests.session()
    cookie = s.get(cookies_u).cookies
    countries = s.get(countries_u, cookies=cookie).json()
    for country in countries :
        param_country = "country=" + country
        leaders = s.get(leaders_u,cookies=cookie,params=param_country)
        i = 0
        while leaders.status_code == 403:
            #cookie = s.get(cookies_u).cookies
            leaders = s.get(leaders_u,cookies=cookie,params=param_country)
            i += 1
            if i > 5 :
                return {}
        for leader in leaders.json():
            leader["paragraph"] = get_first_paragraph(leader['wikipedia_url'],s)
            leaders_dict.setdefault(country, []).append(leader)
    return leaders_dict

with open('data.json', 'x') as fh:
    json.dump(get_leaders(), fh)
fh.close()