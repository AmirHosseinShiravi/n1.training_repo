import time
import requests
# import lxml.html
from bs4 import BeautifulSoup , Tag
from apps.home.models import fyuse_embed
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import pickle
import re
import json

cookie = {"wordpress_logged_in_8446d561c21ca37c7a76067b1cb18519":"navid.moravej%7C1658621670%7C4isTnSPubR1bN63l8GEWlRIYzKjndfzJ3UNwoQVNubx%7C7ead6b9f471735b24130e09b387de0432d2d7d11e8e74d10c1020027fed3ad60"}
max_workers = 16
panorama_image_download_list = []
videos_link_list = []
##########################################
change_page_source_flag = True
save_page_flag = True
download_videos_flag = False
get_videos_links_flag = True
download_panorama_images_flag = False
get_address_of_panorama_image_flag = True
save_links_flag = True
video_quality = '1080p'  # ['1080p' , '720p', '540p', '360p']
##########################################


session = requests.session()
session_with_proxy = requests.session()
# session_with_proxy.proxies = {
    
# 'https': '20.47.108.204:8888',
# 'http' : '8.219.97.248:80',
# 'https': '144.202.61.154:8888',
# 'http' : '206.81.0.107:80',
# 'http' : '47.74.152.29:8888',
# 'http' : '65.20.152.46:8080',
# 'https': '64.189.24.250:3129',
# 'http' : '47.91.44.217:8000',
# 'http' : '66.29.154.103:3128',
# 'http' : '67.212.186.100:80',
# }
session_with_proxy.proxies = {
    'https': 'http://192.168.211.30:8080',
    'https': 'http://192.168.211.30:8080'
}


def scrapper_worker_1(link_list, worker_id, session):
    print("Worker " + str(worker_id) + " started")
    if worker_id == (max_workers - 1):
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers + len(link_list) % max_workers]
    else:
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers]

    
    for link in this_worker_link_list:
        path = link['image_path'].split('/')[-3] + '\\' + link['image_path'].split('/')[-2] + '\\'
        try:
            img = session.get(link['image_path']+ link['image_name'])
            with open(os.getcwd() + '\\apps\\static\\wp-content\\360_view_contents\\' + path  + link['image_name'], 'wb') as f:
                f.write(img.content)
                f.close()
        except requests.exceptions.ConnectTimeout:
            print(f"Connection timeout in worker {worker_id}")
            time.sleep(2)
            this_worker_link_list.append(link)

def scrapper_worker_2(link_list, worker_id, session):
    print("Worker " + str(worker_id) + " started")
    if worker_id == (max_workers - 1):
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers: worker_id * len(
            link_list)//max_workers + len(link_list)//max_workers + len(link_list) % max_workers]
    else:
        this_worker_link_list = link_list[worker_id * len(link_list)//max_workers: worker_id * len(
            link_list)//max_workers + len(link_list)//max_workers]

    
    for link in this_worker_link_list:
        path = link['image_path'].split('/')[-3] + '\\' + link['image_path'].split('/')[-2] + '\\'
        try:
            img = session.get(link['image_path']+ link['image_name'])
            with open(os.getcwd() + '\\apps\\static\\wp-content\\360_view_contents\\' + path  + link['image_name'], 'wb') as f:
                f.write(img.content)
                f.close()
        except requests.exceptions.ConnectTimeout:
            print(f"Connection timeout in worker {worker_id}")
            time.sleep(2)
            this_worker_link_list.append(link)


async def get_data_asynchronous(session, link_list):
    with ThreadPoolExecutor(max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                scrapper_worker_1,
                # Allows us to pass in multiple arguments to `scrapper_worker`
                *(link_list, worker_id, session_with_proxy)
            )
            for worker_id in range(max_workers)
        ]
        # await asyncio.sleep(10)
        for response in await asyncio.gather(*tasks):
            pass


def Scrapper_async(session, link_list):
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(get_data_asynchronous(session, link_list))
    loop.run_until_complete(future)






def get_video_link_from_exercise_page(exercise_page_address, cookie):
    con = requests.Session()
    # con.proxies = {
    #     'http': 'http://192.168.243.225:8080',
    #     'https': 'http://192.168.243.225:8080'
    # }
    res = con.get(str(exercise_page_address), cookies=cookie)
    # print(res.text)

    tree = lxml.html.fromstring(res.text)
    elem_execution = tree.xpath('//*[@id="execution-video-iframe"]/@src')
    elem_education = tree.xpath('//*[@id="education-video-iframe"]/@src')
    print(elem_execution, elem_education)



def apply_neccessary_change_on_exercise_lib_html():

    with open("C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates/home/exercise-library1.html" , 'r' , encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        elem1 = soup.find_all('li', class_='exl-exercise-card card')
        for i, elem in enumerate(elem1):
            print(i, elem.find('a').get('href'))
            page_address = elem.find('a').get('href').split('/')[-2]
            elem.find('a').attrs['href'] = "{% url 'exercise' '" + str(page_address) + "' %}"
            print(elem.find('a').attrs['href'])
        html = str(soup)
        f.close()
    with open("C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates/home/exercise-library1.html" , 'w' , encoding='utf-8') as f:
        f.write(html)
        f.close()


def get_panorama(main_page_content, session_with_proxy):

    global panorama_image_download_list

    link_of_360_degree = main_page_content.find('div', {"class":"fyu_container fyu_vertical"})  
    if link_of_360_degree:
        
        embed_url_slug = link_of_360_degree.get('id')[4:]  # in example:  <div id="fyu_me3zt7bc5y" class="fyu_container fyu_vertical"></div>
        print(embed_url_slug)
        while True:
            embed_response = session_with_proxy.get('https://fyu.se/embed/' + embed_url_slug)
            embed_response_json = embed_response.json()
            if embed_response_json.get("success") == 1:
                break
            else:
                time.sleep(1)
                continue

        print('fyuse get response ok')
        print(embed_response.text)
        embed_response_json = embed_response.json()
        # some times the response path is not https://i.fyue.com/ , so we need to override it to fyu-embed-3.0.0.js line #1786 code work properly
        download_img_path_prefix = embed_response_json['path'].split('//')[1]
        download_img_path_prefix = download_img_path_prefix.split('/')[1:] 
        embed_response_json['path'] = 'https://i.fyuse.com/' + '/'.join(download_img_path_prefix)
        
        if not fyuse_embed.objects.filter(slug = embed_url_slug).exists():
            fyuse_embed.objects.create(slug= embed_url_slug, data = embed_response_json)
        else:
            print('panorama exist previously')
        download_img_path = embed_response_json['path']
        path = download_img_path.split('/')[-3] + '\\' + download_img_path.split('/')[-2] + '\\'
        dir_path = '\\apps\\static\\wp-content\\360_view_contents\\' + path
        print(path)
        os.makedirs(os.getcwd() + '\\apps\\static\\wp-content\\360_view_contents\\' + path , exist_ok=True)
        for j in range(0, embed_response_json['fy']['l'][1]): # in example: embed_response_json['fy']['l'] == [0 , 300]
            panorama_image_download_list.append({'image_path':download_img_path, 'folder_path': dir_path , 'image_name': 'frames_' +  str(j) + '.jpg'})
            # img = session.get(download_img_path + 'frames_' +  str(j) + '.jpg?v=1')
            # os.makedirs('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/static/wp-content/360_view_contents' + download_img_path[19:] , exist_ok=True)
            # print('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/static/wp-content/360_view_contents' + download_img_path[19:]  + 'frames_' +  str(j) + '.jpg')
            # with open( 'C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/static/wp-content/360_view_contents' + download_img_path[19:] + 'frames_' +  str(j) + '.jpg', 'wb') as f:
            #     f.write(img.content)

def get_video_link(main_page_content, session_with_proxy):
    global videos_link_list

    education_video_link = main_page_content.find('iframe', {"id":"education-video-iframe"})

    if education_video_link:
        education_video_link = education_video_link.get('src')
        res = session_with_proxy.get(education_video_link, headers={'Referer': 'https://n1.training/'})
        # exract javascript variable from html
        soup3 = BeautifulSoup(res.text, 'html.parser')
        script = soup3.findAll('script')[-1].string
        json_string = re.search(r"var config = (.*?);", script, flags=re.DOTALL)
        data = json.loads(json_string[1])

        education_video_thumbnail_link  = data['video']['thumbs']['base']
        for field in data['request']['files']['progressive']:
            if field['quality'] == video_quality:
                videos_link_list.append({'video_links': field['url'] , 'path_to_save_video'    : 'apps/static/wp-content/videos/' + page_address[30:] , 'video_file_name'    : 'education_video.mp4',
                                        'video_thumbnail_links': education_video_thumbnail_link , 'path_to_save_thumbnail': 'apps/static/wp-content/videos/' + page_address[30:] , 'thumbnail_file_name': 'education_video_thumbnail.avif'})
                break
    
    execution_video_link = main_page_content.find('iframe', {"id":"execution-video-iframe"})
    if execution_video_link:
        execution_video_link = execution_video_link.get('src')
        res = session_with_proxy.get(execution_video_link, headers={'Referer': 'https://n1.training/'})
        soup3 = BeautifulSoup(res.text, 'html.parser')
        script = soup3.findAll('script')[-1].string
        json_string = re.search(r"var config = (.*?);", script, flags=re.DOTALL)
        data = json.loads(json_string[1])
        execution_video_thumbnail_link  = data['video']['thumbs']['base']
        for field in data['request']['files']['progressive']:
            if field['quality'] == video_quality:
                videos_link_list.append({'video_links': field['url']  , 'path_to_save_video'    : 'apps/static/wp-content/videos/' + page_address[30:] , 'video_file_name'    :'execution_video.mp4'
                                        ,'video_thumbnail_links': execution_video_thumbnail_link , 'path_to_save_thumbnail': 'apps/static/wp-content/videos/' + page_address[30:] , 'thumbnail_file_name':'execution_video_thumbnail.avif'})
                break            


with open(os.getcwd() + '\\extra\\' + "index.html" , 'r' , encoding='utf-8') as f:
    content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    all_exercise_pages_link = soup.find_all('li', class_='exl-exercise-card card') 

    for i, elem in enumerate(all_exercise_pages_link):
        print(i, elem.find('a').get('href'))
        page_address = elem.find('a').get('href')
        # page_address = 'https://n1.training/exercises/ffw-bfe-db-split-squat/'
        # html = session_with_proxy.get('https://n1.training/exercises/ffw-bfe-db-split-squat/', cookies=cookie).text
        html = session_with_proxy.get(page_address, cookies=cookie).text

        soup2 = BeautifulSoup(html, 'html.parser')
        main_page_content = soup2.find('div', {'id':"single-exercise"})
        

        #################### get panorama links #####################
        if get_address_of_panorama_image_flag:        
            get_panorama(main_page_content, session_with_proxy)


        if download_panorama_images_flag:
            Scrapper_async(session, panorama_image_download_list)


        ##################### get video link ########################
        if get_videos_links_flag:

            get_video_link(main_page_content, session_with_proxy)

        if download_videos_flag:
            if videos_link_list :
                for video_link in videos_link_list:
                    video = session.get(video_link['video_links'], headers={'Referer': 'https://n1.training/'}, cookies=cookie, stream=True)
                    os.makedirs('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/' + video_link['path_to_save_video'] , exist_ok=True)
                    with open('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/' + video_link['path_to_save_video'] + video_link['video_file_name'], 'wb') as f:
                        for chunk in video.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)
                    thumb = session.get(video_link['video_thumbnail_links'], headers={'Referer': 'https://n1.training/'}, cookies=cookie, stream=True)
                    os.makedirs('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/' + video_link['path_to_save_thumbnail'] , exist_ok=True)
                    with open('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/' + video_link['path_to_save_thumbnail'] + video_link['thumbnail_file_name'], 'wb') as f:
                        for chunk in thumb.iter_content(chunk_size=1024):
                            if chunk:
                                f.write(chunk)

                videos_link_list.clear()
        ###################### main page html ############################
        if change_page_source_flag:

            education_video_iframe = main_page_content.find('iframe', {"id":"education-video-iframe"})
            execution_video_iframe = main_page_content.find('iframe', {"id":"execution-video-iframe"})
            
            if education_video_iframe:
                v = Tag(builder=soup2.builder, name='video', attrs={'width': '640', 'height': '360', 'poster': f"/static/wp-content/videos/{page_address[30:]}education_video_thumbnail.avif", 'controls': 'controls'})
                education_video_iframe.replace_with(v)
                v.insert(0,Tag(builder=soup2.builder, name='source', attrs={'src': f"/static/wp-content/videos/{page_address[30:]}education_video.mp4", 'type':'video/mp4'}))
            
            if execution_video_iframe:
                v = Tag(builder=soup2.builder, name='video', attrs={'width': '640', 'height': '360', 'poster': f"/static/wp-content/videos/{page_address[30:]}execution_video_thumbnail.avif" , 'controls': 'controls'})
                execution_video_iframe.replace_with(v)
                v.insert(0,Tag(builder=soup2.builder, name='source', attrs={'src': f"/static/wp-content/videos/{page_address[30:]}execution_video.mp4", 'type':'video/mp4'}))
            
            fyu_script = main_page_content.find('div', {'class':"fyu_container fyu_vertical"})
            if fyu_script:
                fyu_script = fyu_script.next_element
                fyu_script.attrs['src'] = '/static/exercise-assets/fyu.se/embed.js'
            
            ######################### Revealed Links #############################

            other_pages_of_exercise = main_page_content.find('section', {'id': 'fyuse-setup-cues'})
            other_pages_of_exercise = other_pages_of_exercise.findAll('div', {'class': 'col-12 col-sm-6 col-md-6'})[1]
            other_pages_of_exercise = other_pages_of_exercise.findAll('a')
            if other_pages_of_exercise:
                for a in other_pages_of_exercise:
                    other_page_address = a.attrs['href']
                    revealed_num = other_page_address[other_page_address.find('?') + 10: ]
                    if int(revealed_num) != 0:
                        html = session_with_proxy.get(other_page_address , cookies=cookie).text
                        soup4 = BeautifulSoup(html, 'html.parser')
                        other_page_content = soup4.find('div', {'id':"single-exercise"})
                        if get_address_of_panorama_image_flag:        
                            get_panorama(other_page_content, session_with_proxy)
                        
                        if change_page_source_flag:
                            education_video_iframe = other_page_content.find('iframe', {"id":"education-video-iframe"})
                            execution_video_iframe = other_page_content.find('iframe', {"id":"execution-video-iframe"})
                            
                            if education_video_iframe:
                                v = Tag(builder=soup2.builder, name='video', attrs={'width': '640', 'height': '360', 'poster': f"/static/wp-content/videos/{page_address[30:]}education_video_thumbnail.avif", 'controls': 'controls'})
                                education_video_iframe.replace_with(v)
                                v.insert(0,Tag(builder=soup2.builder, name='source', attrs={'src': f"/static/wp-content/videos/{page_address[30:]}education_video.mp4", 'type':'video/mp4'}))
                            
                            if execution_video_iframe:
                                v = Tag(builder=soup2.builder, name='video', attrs={'width': '640', 'height': '360', 'poster': f"/static/wp-content/videos/{page_address[30:]}execution_video_thumbnail.avif" , 'controls': 'controls'})
                                execution_video_iframe.replace_with(v)
                                v.insert(0,Tag(builder=soup2.builder, name='source', attrs={'src': f"/static/wp-content/videos/{page_address[30:]}execution_video.mp4", 'type':'video/mp4'}))
                            
                            fyu_script = other_page_content.find('div', {'class':"fyu_container fyu_vertical"})
                            if fyu_script:
                                fyu_script = fyu_script.next_element
                                fyu_script.attrs['src'] = '/static/exercise-assets/fyu.se/embed.js'
                            ###################################### similar section  ########################################
                            similar_section = other_page_content.find('section',  {'id':"similar-substitutions"})
                            all_link = similar_section.find_all('a')
                            for elem in all_link:
                                # "https://n1.training/exercises/anterior-delt-cable-raise-to-ear/"
                                address = "{% url 'exercise' '" + elem.attrs['href'].split('/')[-2] + "' %}"
                                elem.attrs['href'] = address

                            ##################################### other revealed page ######################################
                            other_pages_of_exercise = other_page_content.find('section', {'id': 'fyuse-setup-cues'})
                            other_pages_of_exercise = other_pages_of_exercise.findAll('div', {'class': 'col-12 col-sm-6 col-md-6'})[1]
                            all_link = other_pages_of_exercise.find_all('a')
                            if all_link:

                                for elem in all_link:
                                    # "https://n1.training/exercises/anterior-delt-cable-raise-to-ear/"
                                    address = "{% url 'exercise-revealed' " + "exercise_name='" + elem.attrs['href'].split('/')[-3]  + "' " + elem.attrs['href'].split('/')[-1][1:] + " %}"
                                    elem.attrs['href'] = address

                            back_button = other_page_content.find('section', {'id': 'back-to-exercises'})
                            back_button_a_tag = back_button.find('a')
                            back_button_a_tag.attrs['href'] = '/'
                        ################################################################################################

                        other_page_html = str(other_page_content)
                        other_page_html = "".join(['{% extends "layouts/base.html" %} \n {% block content %} \n', other_page_html, ' \n  {% endblock content %}'])
                        page_path = page_address[19:]
                        os.makedirs('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates' + page_path + revealed_num + '/' , exist_ok=True)
                        with open(  'C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates' + page_path + revealed_num + '/' + 'index.html', 'w', encoding='utf-8') as f:
                            f.write(other_page_html)


            ######################### link replace #############################
            similar_section = main_page_content.find('section',  {'id':"similar-substitutions"})
            all_link = similar_section.find_all('a')
            for elem in all_link:
                # "https://n1.training/exercises/anterior-delt-cable-raise-to-ear/"
                address = "{% url 'exercise' '" + elem.attrs['href'].split('/')[-2] + "' %}"
                elem.attrs['href'] = address

            other_pages_of_exercise = main_page_content.find('section', {'id': 'fyuse-setup-cues'})
            other_pages_of_exercise = other_pages_of_exercise.findAll('div', {'class': 'col-12 col-sm-6 col-md-6'})[1]
            all_link = other_pages_of_exercise.find_all('a')
            if all_link:

                for elem in all_link:
                    # "https://n1.training/exercises/anterior-delt-cable-raise-to-ear/"
                    address = "{% url 'exercise-revealed' " + "exercise_name='" + elem.attrs['href'].split('/')[-3]  + "' " + elem.attrs['href'].split('/')[-1][1:] + " %}"
                    elem.attrs['href'] = address


            back_button = main_page_content.find('section', {'id': 'back-to-exercises'})
            back_button_a_tag = back_button.find('a')
            back_button_a_tag.attrs['href'] = '/'





            ####################################################################
            

            
        if save_page_flag:

            main_page_html = main_page_content.decode()
            main_page_html = "".join(['{% extends "layouts/base.html" %} \n {% block content %} \n', main_page_html, ' \n  {% endblock content %}'])
            page_path = page_address[19:]
            os.makedirs('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates' + page_path , exist_ok=True)
            with open('C:/Users/jijij/OneDrive/Desktop/django_tabler_n1_training/apps/templates' + page_path + 'index.html', 'w', encoding='utf-8') as f:
                f.write(main_page_html)
        print('done')      






# def scrapper_worker_1(link_list, worker_id, session):

#     print("Worker " + str(worker_id) + " started")
#     if worker_id == (max_workers - 1):
#         this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers + len(link_list) % max_workers]
#     else:
#         this_worker_link_list = link_list[worker_id * len(link_list)//max_workers  :   worker_id * len(link_list)//max_workers + len(link_list)//max_workers]

#     contect_length = 0
#     for i, link in enumerate(this_worker_link_list):
        
#         try:
#             r = session.head(link)
#             print(f"media {i} content length is {ceil(int(r.headers['content-length'])/(1024*1024))} MB")
#             contect_length = contect_length + int(r.headers['content-length'])
#             print('#########################################################################')
#             print(f"Some of content length until there is {ceil( contect_length / (1024 * 1024) )} MB")
#             print('#########################################################################')
            
#         except requests.exceptions.ConnectTimeout:
#             print(f"Connection timeout in worker {worker_id}")
#             time.sleep(2)
#             this_worker_link_list.append(link)
    
#     return contect_length



# async def get_data_asynchronous(session, link_list):
    
    
#     with ThreadPoolExecutor(max_workers) as executor:
#         loop = asyncio.get_event_loop()
#         tasks = [
#             loop.run_in_executor(
#                 executor,
#                 scrapper_worker_1,
#                 # Allows us to pass in multiple arguments to `scrapper_worker`
#                 *(link_list, worker_id, session)
#             )
#             for worker_id in range(max_workers)
#         ]
#         # await asyncio.sleep(10)
#         for response in await asyncio.gather(*tasks):
#             pass


# def Scrapper_async(session, link_list):
#     loop = asyncio.get_event_loop()
#     future = asyncio.ensure_future(get_data_asynchronous(session, link_list))
#     loop.run_until_complete(future)


# Scrapper_async(session, links)








################ save links #########################

if save_links_flag:
    with open('panorama_image_download_list_pickle', 'ab') as f:
        pickle.dump(panorama_image_download_list, f)

    with open('panorama_image_download_list.txt', 'w') as f:
        for link in panorama_image_download_list:
            f.write(link['image_path']+ link['image_name'] + '\n')
    

    with open('video_download_list_pickle', 'ab') as f:
        pickle.dump(videos_link_list, f)

    with open('video_download_list.txt', 'w') as f:
        for link in videos_link_list:
            f.write(link['video_links']+ '\n')

    with open('video_download_list_thumbnail.txt', 'w') as f:
        for link in videos_link_list:
            f.write(link['video_thumbnail_links']+ '\n')

        
print('done total')



    # Write to file
    # panorama_image_download_list_file_handler = open('panorama_image_download_list', 'ab')
    # pickle.dump(panorama_image_download_list, panorama_image_download_list_file_handler)
    # panorama_image_download_list_file_handler.close()

