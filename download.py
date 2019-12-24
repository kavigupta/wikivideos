
import json
import requests

API_CALL = 'https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&&titles={}'
def get_page(title):
    response = requests.get(API_CALL.format(title))
    data = response.content.decode('utf-8')
    values = json.loads(data)['query']['pages'].values()
    [latest] = list(values)[0]['revisions']
    return latest['*']
