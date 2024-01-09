import os
import requests

dir = 'images'
url = 'https://picsum.photos/100'
count = 300

os.makedirs(dir, exist_ok=True)
for i in range(count):
    print(f'{i + 1}/{count}')
    response = requests.get(url, stream=True) 
    with open(os.path.join(dir, f'img_{i:03d}.jpg'), 'wb') as file:
        file.write(response.content)
