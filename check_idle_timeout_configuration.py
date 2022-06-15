import requests
import json

session = requests.Session()
get_response = session.get(
    "http://localhost:8888/jupyter/default/sagemaker-studio-autoshutdown/idle_checker"
)
print(get_response)
print(get_response.json())
