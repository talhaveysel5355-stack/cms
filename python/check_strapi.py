import requests

r = requests.get('http://localhost:1337/api/animes',
                 params={'pagination[pageSize]': 5, 'fields[0]': 'title', 'fields[1]': 'rating'},
                 timeout=8)
d = r.json()
total = d.get('meta', {}).get('pagination', {}).get('total', 0)
print(f'Strapi icindeki anime sayisi: {total}')
for item in d.get('data', []):
    title = item.get('title', '?')
    rating = item.get('rating', '?')
    print(f'  - {title} (puan: {rating})')
