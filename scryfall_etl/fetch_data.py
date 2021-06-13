import requests

resp = requests.get('https://api.scryfall.com/catalog/card-names')

if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))

target_file = open("card_names_API"

#for todo_item in resp.json():
#    print('{} {}'.format(todo_item['id'], todo_item['summary']))
