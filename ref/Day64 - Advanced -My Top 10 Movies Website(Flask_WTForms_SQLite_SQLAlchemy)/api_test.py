import requests

TMDB_api_key = "f30a88b5594b6a15422a1fa2041f4d7a"
url = "https://api.themoviedb.org/3/search/movie"
para = {
    "api_key": TMDB_api_key,
    "query": "葉問",
}
response = requests.get(url,params=para)
response.raise_for_status()
data = response.json()

for i in data["results"]:
    print(i)