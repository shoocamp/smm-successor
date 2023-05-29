import requests

url = 'http://127.0.0.1:8000/api/v1/upload_video'
file_path = '/Users/sergeyzaitsev/PycharmProjects/smm-successor/video_content/Timeline 1.mov'

video = {
    'title': 'My Video Title',
    'description': 'Video description',
    'target_platform': 'YouTube',
    'time_to_publish': '2023-06-01T12:00:00Z'
}



# print(video['title'])

files = {'file': open(file_path, 'rb')}

response = requests.post(url, files=files, data=video)

print(response.status_code)
print(response.json())
