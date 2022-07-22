import time
import requests
# import lxml.html
from bs4 import BeautifulSoup , Tag
# from apps.home.models import fyuse_embed
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pickle
import re
import json



with open(os.getcwd() + '\\extra\\' + "index.html" , 'r' , encoding='utf-8') as f:
    content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    all_exercise_pages_link = soup.find_all('li', class_='exl-exercise-card card') 
    for i, elem in enumerate(all_exercise_pages_link):
        a = elem.find('a')
        # "https://n1.training/exercises/anterior-delt-cable-raise-to-ear/"
        address = "{% url 'exercise' '" + a.attrs['href'].split('/')[-2] + "' %}"
        a.attrs['href'] = address
    
    all_footer_link = soup.find_all('div', {'class':"modal-footer"})
    for i, elem in enumerate(all_footer_link):
        a = elem.find('a')
        if a:
            address = "{% url 'exercise' '" + a.attrs['href'].split('/')[-2] + "' %}"
            a.attrs['href'] = address







    # html = str(soup)
    html = soup.decode()
    with open('indexxxxxxx.html', 'w', encoding='utf-8') as f:
        f.write(html)
