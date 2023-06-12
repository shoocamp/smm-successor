import requests

from vk_oauth import token


def vk_upload(file_path, title, description):

    url = 'https://api.vk.com/method/video.save'
    params = {
        'name': f'{title}',
        'description': f'{description}',
        'privacy_view': '3',
        'access_token': f'{token}',
        'v': '5.131'
    }

    response = requests.post(url, params=params)
    data = response.json()
    upload_url = data['response']['upload_url']

    files = {'video_file': open(file_path, 'rb')}
    response = requests.post(upload_url, files=files)

    return response.json()
