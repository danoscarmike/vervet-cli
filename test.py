import requests

response = requests.get('https://api-v2v3search-0.nuget.org/query?q=google-cloud&prerelease=true&take=1000')

print(len(response.json()['data']))