
import time
import click
import requests
import threading
from threading import Lock
# The below code is used for each chunk of file handled
# by each thread for downloading the content from specified
# location to storage
lock = Lock()


def Handler(start, end, url, file, worker_id, session):
    
    print("Downloading in worker %d from %d to %d" % (worker_id,start, end))

    headers = {'Range': 'bytes=%d-%d' % (start, end), 
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

    content_len = 0                
    while content_len < end - start - 1000:       
        try:
            r = session.get(url, headers=headers)
            content_len = len(r.content)
            print(len(r.content))
        except KeyboardInterrupt:
            print("Keyboard Interrupt")
            return
        except Exception as e:
            print("Exception: %s" % e)
            return


    with lock:
        print('##############################################################')
        print("Downloading from %d to %d" % (start, end))
        print(f'file tell before write in worker_id {worker_id} is : {file.tell()}')

        file.seek(start)
        file.write(r.content)
        # if len(r.content) < 20000:
        #     print(r.content)
        print('length of content is : ', len(r.content))

        print(f'file tell after write in worker_id {worker_id} is : {file.tell()}')
        print('##############################################################')




@click.command(help="It downloads the specified file with specified name")
@click.option('—number_of_threads',default=4, help="No of Threads")
@click.option('--name',type=click.Path(),help="Name of the file with extension")
@click.argument('url_of_file',type=click.Path())

@click.pass_context
def download_file(ctx,url_of_file,name,number_of_threads):
    session = requests.Session()
    r = session.head(url_of_file , headers={'referer': 'https://n1.training/'})
    if name:
        file_name = name
    else:
        file_name = url_of_file.split('/')[-1]
    try:
        file_size = int(r.headers['content-length'])
        print(file_size)
    except:
        print ("Invalid URL")
        return
    part = int(file_size) // number_of_threads
    fp = open(file_name, "wb")
    fp.write(bytearray(file_size))
 

    for i in range(number_of_threads):
        if i != number_of_threads - 1:
            start = part * i
            end = start + part 
        if i == number_of_threads - 1 :
            start =  part * i
            end   =  file_size
        # create a Thread with start and end locations
        t = threading.Thread(target=Handler,kwargs={'start': start, 'end': end, 'url': url_of_file, 'file': fp , 'worker_id': i, 'session': session} , daemon=True)
        t.start()
        time.sleep(i * 0.5)
        

    main_thread = threading.current_thread()
    for t in threading.enumerate():
        if t is main_thread:
            continue
        t.join()
    print ('%s downloaded'%(file_name))
    fp.close()


if __name__ == '__main__':
	download_file(obj={})






# SuperFastPython.com
# example of thread-safe writing to a file
# from random import random
# from threading import Thread
# from threading import Lock

# # task for worker threads
# def task(number, file, lock):
#     # task loop
#     for i in range(1000):
#         # generate random number between 0 and 1
#         value = random()
#         # write to the file
#         with lock:
#             file.write(f'Thread {number} got {value}.\n')

# # create the shared lock
# lock = Lock()
# # defile the shared file path
# filepath = 'output.txt'
# # open the file
# file = open(filepath, 'a')
# # configure many threads
# threads = [Thread(target=task, args=(i,file,lock)) for i in range(1000)]
# # start threads
# for thread in threads:
#     thread.start()
# # wait for threads to finish
# for thread in threads:
#     thread.join()
# # close the file
# file.close()
