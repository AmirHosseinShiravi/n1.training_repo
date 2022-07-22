from tqdm import tqdm
import requests

url = "https://vod-progressive.akamaized.net/exp=1658308573~acl=%2Fvimeo-prod-skyfire-std-us%2F01%2F4262%2F12%2F321314525%2F1258567690.mp4~hmac=32d6c1c32a09c687cf8bc611640dfedba846e6eff58fccbf40f7168d76c89154/vimeo-prod-skyfire-std-us/01/4262/12/321314525/1258567690.mp4"
# response = requests.get(url,headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}, stream=True)


# with tqdm.wrapattr(
#     open('amir10.mp4', "wb"), "write",
#     unit='B', unit_scale=True, unit_divisor=1024, miniters=1,
#     desc='amir10.mp4', total=int(response.headers.get('content-length', 0))
# ) as fout:
#     for chunk in response.iter_content(chunk_size=4096):
#         fout.write(chunk)


def download_worker_func(url):
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB',
                        unit_scale=True, colour='green')
    file_name = url.split('/')[-1]
    with open(file_name, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")

download_worker_func(url)