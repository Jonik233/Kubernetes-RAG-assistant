import time
import requests


start = time.time()

question = "Which service object should i use if i only want to interact with pods within cluster?"

response = requests.post("http://0.0.0.0:8080/query", json={"query": question})
print(response.json())

elapsed_time = time.time() - start
print(elapsed_time)