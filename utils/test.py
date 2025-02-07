import requests
resp = requests.post('https://textbelt.com/text', {
  'phone': '447786872193',
  'message': 'Hello world',
  'key': 'textbelt',
})
print(resp.json())