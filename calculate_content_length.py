import requests
from math import ceil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import os


max_workers = 32


session = requests.Session()
session.proxies = {
    
    'https': 'http://192.168.12.30:8080',
    'http': 'http://192.168.12.30:8080'
}
with open('panorama_image_download_list.txt', 'r') as f:
    links = f.read().splitlines()
#     for i, link in enumerate(links):
        
#         r = session.head(link)
#         print(f"video {i} content length is {ceil(int(r.headers['content-length'])/(1024*1024))} MB")
#         contect_length = contect_length + int(r.headers['content-length'])
#         print('#########################################################################')
#         print(f"Some of content length until there is {ceil( contect_length / (1024 * 1024) )} MB")
#         print('#########################################################################')







def scrapper_worker_1(link_list, worker_id, session):

    print("Worker " + str(worker_id) + " started")
    if worker_id == (max_workers - 1):
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers + len(link_list) % max_workers]
    else:
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers]

    contect_length = 0
    for i, link in enumerate(this_worker_link_list):
        
        try:
            r = session.head(link)
            print(f"media {i} content length is {ceil(int(r.headers['content-length'])/(1024*1024))} MB")
            contect_length = contect_length + int(r.headers['content-length'])
            print('#########################################################################')
            print(f"Some of content length until there is {ceil( contect_length / (1024 * 1024) )} MB")
            print('#########################################################################')
            
        except requests.exceptions.ConnectTimeout:
            print(f"Connection timeout in worker {worker_id}")
            time.sleep(2)
            this_worker_link_list.append(link)
    
    return contect_length



async def get_data_asynchronous(session, link_list):
    
    contect_length_total = 0
    with ThreadPoolExecutor(max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                scrapper_worker_1,
                # Allows us to pass in multiple arguments to `scrapper_worker`
                *(link_list, worker_id, session)
            )
            for worker_id in range(max_workers)
        ]
        # await asyncio.sleep(10)
        for response in await asyncio.gather(*tasks):
            # print(response)
            contect_length_total = contect_length_total + response
            print(f"all links content length in MB : {contect_length_total / (1024 * 1024)}")



def Scrapper_async(session, link_list):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous(session, link_list))
    loop.run_until_complete(future)


Scrapper_async(session, links)