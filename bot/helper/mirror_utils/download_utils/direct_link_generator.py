# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
""" Helper Module containing various sites direct links generators. This module is copied and modified as per need
from https://github.com/AvinashReddy3108/PaperplaneExtended . I hereby take no credit of the following code other
than the modifications. See https://    from bot import LOGGER, UPTOBOX_TOKEN
github.com/AvinashReddy3108/PaperplaneExtended/commits/master/userbot/modules/direct_links.py
for original authorship. """

from requests import get as rget, head as rhead, post as rpost, Session as rsession
from re import findall as re_findall, sub as re_sub, match as re_match, search as re_search
from urllib.parse import urlparse, unquote
from json import loads as jsonloads
from lk21 import Bypass
from cfscrape import create_scraper
from bs4 import BeautifulSoup
from base64 import standard_b64encode, b64decode
from time import sleep
from lxml import etree
from bot import LOGGER, UPTOBOX_TOKEN, APPDRIVE_EMAIL, APPDRIVE_PASS, CRYPT
from bot.helper.ext_utils.bot_utils import is_Sharerlink
from bot.helper.ext_utils.exceptions import DirectDownloadLinkException
from bot.helper.ext_utils.bot_utils import is_appdrive_link, is_gdtot_link
fmed_list = ['fembed.net', 'fembed.com', 'femax20.com', 'fcdn.stream', 'feurl.com', 'layarkacaxxi.icu',
             'naniplay.nanime.in', 'naniplay.nanime.biz', 'naniplay.com', 'mm9842.com']


def direct_link_generator(link: str):
    """ direct links generator """
    if 'youtube.com' in link or 'youtu.be' in link:
        raise DirectDownloadLinkException(f"ERROR: Use ytdl cmds for Youtube links")
    elif 'yadi.sk' in link or 'disk.yandex.com' in link:
        return yandex_disk(link)
    elif 'mediafire.com' in link:
        return mediafire(link)
    elif 'uptobox.com' in link:
        return uptobox(link)
    elif 'osdn.net' in link:
        return osdn(link)
    elif 'github.com' in link:
        return github(link)
    elif 'hxfile.co' in link:
        return hxfile(link)
    elif 'anonfiles.com' in link:
        return anonfiles(link)
    elif 'letsupload.io' in link:
        return letsupload(link)
    elif '1drv.ms' in link:
        return onedrive(link)
    elif 'pixeldrain.com' in link:
        return pixeldrain(link)
    elif 'antfiles.com' in link:
        return antfiles(link)
    elif 'streamtape.com' in link:
        return streamtape(link)
    elif 'bayfiles.com' in link:
        return anonfiles(link)
    elif 'racaty.net' in link:
        return racaty(link)
    elif '1fichier.com' in link:
        return fichier(link)
    elif 'solidfiles.com' in link:
        return solidfiles(link)
    elif 'krakenfiles.com' in link:
        return krakenfiles(link)
    elif 'upload.ee' in link:
        return uploadee(link)
    elif is_Sharerlink(link):
        if 'gdtot' in link:
            return gdtot(link)
        elif 'filepress' in link:
            return filepress(link)
        elif any(x in link for x in ['appdrive', 'gdflix']):
            return sharer_scraper(link)
        else:
            raise DirectDownloadLinkException('ERROR: Currently this sharer link does not support')
    elif is_appdrive_link((link)):
        return appdrive(link)
    elif is_gdtot_link(link):
        return gdtot(link)
    elif any(x in link for x in fmed_list):
        return fembed(link)
    elif any(x in link for x in ['sbembed.com', 'watchsb.com', 'streamsb.net', 'sbplay.org']):
        return sbembed(link)
    else:
        raise DirectDownloadLinkException(f'No Direct link function found for {link}')

def yandex_disk(url: str) -> str:
    """ Yandex.Disk direct link generator
    Based on https://github.com/wldhx/yadisk-direct """
    try:
        link = re_findall(r'\b(https?://(yadi.sk|disk.yandex.com)\S+)', url)[0][0]
    except IndexError:
        return "No Yandex.Disk links found\n"
    api = 'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={}'
    try:
        return rget(api.format(link)).json()['href']
    except KeyError:
        raise DirectDownloadLinkException("ERROR: File not found/Download limit reached")

def uptobox(url: str) -> str:
    """ Uptobox direct link generator
    based on https://github.com/jovanzers/WinTenCermin and https://github.com/sinoobie/noobie-mirror """
    try:
        link = re_findall(r'\bhttps?://.*uptobox\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Uptobox links found")
    if UPTOBOX_TOKEN is None:
        LOGGER.error('UPTOBOX_TOKEN not provided!')
        dl_url = link
    else:
        try:
            link = re_findall(r'\bhttp?://.*uptobox\.com/dl\S+', url)[0]
            dl_url = link
        except:
            file_id = re_findall(r'\bhttps?://.*uptobox\.com/(\w+)', url)[0]
            file_link = f'https://uptobox.com/api/link?token={UPTOBOX_TOKEN}&file_code={file_id}'
            req = rget(file_link)
            result = req.json()
            if result['message'].lower() == 'success':
                dl_url = result['data']['dlLink']
            elif result['message'].lower() == 'waiting needed':
                waiting_time = result["data"]["waiting"] + 1
                waiting_token = result["data"]["waitingToken"]
                sleep(waiting_time)
                req2 = rget(f"{file_link}&waitingToken={waiting_token}")
                result2 = req2.json()
                dl_url = result2['data']['dlLink']
            elif result['message'].lower() == 'you need to wait before requesting a new download link':
                cooldown = divmod(result['data']['waiting'], 60)
                raise DirectDownloadLinkException(f"ERROR: Uptobox is being limited please wait {cooldown[0]} min {cooldown[1]} sec.")
            else:
                LOGGER.info(f"UPTOBOX_ERROR: {result}")
                raise DirectDownloadLinkException(f"ERROR: {result['message']}")
    return dl_url

def mediafire(url: str) -> str:
    """ MediaFire direct link generator """
    try:
        link = re_findall(r'\bhttps?://.*mediafire\.com\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No MediaFire links found")
    page = BeautifulSoup(rget(link).content, 'lxml')
    info = page.find('a', {'aria-label': 'Download file'})
    return info.get('href')

def osdn(url: str) -> str:
    """ OSDN direct link generator """
    osdn_link = 'https://osdn.net'
    try:
        link = re_findall(r'\bhttps?://.*osdn\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No OSDN links found")
    page = BeautifulSoup(
        rget(link, allow_redirects=True).content, 'lxml')
    info = page.find('a', {'class': 'mirror_link'})
    link = unquote(osdn_link + info['href'])
    mirrors = page.find('form', {'id': 'mirror-select-form'}).findAll('tr')
    urls = []
    for data in mirrors[1:]:
        mirror = data.find('input')['value']
        urls.append(re_sub(r'm=(.*)&f', f'm={mirror}&f', link))
    return urls[0]

def github(url: str) -> str:
    """ GitHub direct links generator """
    try:
        re_findall(r'\bhttps?://.*github\.com.*releases\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No GitHub Releases links found")
    download = rget(url, stream=True, allow_redirects=False)
    try:
        return download.headers["location"]
    except KeyError:
        raise DirectDownloadLinkException("ERROR: Can't extract the link")

def hxfile(url: str) -> str:
    """ Hxfile direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_filesIm(url)

def anonfiles(url: str) -> str:
    """ Anonfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_anonfiles(url)

def letsupload(url: str) -> str:
    """ Letsupload direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    try:
        link = re_findall(r'\bhttps?://.*letsupload\.io\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Letsupload links found\n")
    return Bypass().bypass_url(link)

def fembed(link: str) -> str:
    """ Fembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    dl_url= Bypass().bypass_fembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count-1]

def sbembed(link: str) -> str:
    """ Sbembed direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    dl_url= Bypass().bypass_sbembed(link)
    count = len(dl_url)
    lst_link = [dl_url[i] for i in dl_url]
    return lst_link[count-1]

def onedrive(link: str) -> str:
    """ Onedrive direct link generator
    Based on https://github.com/UsergeTeam/Userge """
    link_without_query = urlparse(link)._replace(query=None).geturl()
    direct_link_encoded = str(standard_b64encode(bytes(link_without_query, "utf-8")), "utf-8")
    direct_link1 = f"https://api.onedrive.com/v1.0/shares/u!{direct_link_encoded}/root/content"
    resp = rhead(direct_link1)
    if resp.status_code != 302:
        raise DirectDownloadLinkException("ERROR: Unauthorized link, the link may be private")
    return resp.next.url

def pixeldrain(url: str) -> str:
    """ Based on https://github.com/yash-dk/TorToolkit-Telegram """
    url = url.strip("/ ")
    file_id = url.split("/")[-1]
    if url.split("/")[-2] == "l":
        info_link = f"https://pixeldrain.com/api/list/{file_id}"
        dl_link = f"https://pixeldrain.com/api/list/{file_id}/zip"
    else:
        info_link = f"https://pixeldrain.com/api/file/{file_id}/info"
        dl_link = f"https://pixeldrain.com/api/file/{file_id}"
    resp = rget(info_link).json()
    if resp["success"]:
        return dl_link
    else:
        raise DirectDownloadLinkException(f"ERROR: Cant't download due {resp['message']}.")

def antfiles(url: str) -> str:
    """ Antfiles direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_antfiles(url)

def streamtape(url: str) -> str:
    """ Streamtape direct link generator
    Based on https://github.com/zevtyardt/lk21
    """
    return Bypass().bypass_streamtape(url)

def racaty(url: str) -> str:
    """ Racaty direct link generator
    based on https://github.com/SlamDevs/slam-mirrorbot"""
    dl_url = ''
    try:
        re_findall(r'\bhttps?://.*racaty\.net\S+', url)[0]
    except IndexError:
        raise DirectDownloadLinkException("No Racaty links found")
    scraper = create_scraper()
    r = scraper.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    op = soup.find("input", {"name": "op"})["value"]
    ids = soup.find("input", {"name": "id"})["value"]
    rapost = scraper.post(url, data = {"op": op, "id": ids})
    rsoup = BeautifulSoup(rapost.text, "lxml")
    dl_url = rsoup.find("a", {"id": "uniqueExpirylink"})["href"].replace(" ", "%20")
    return dl_url

def fichier(link: str) -> str:
    """ 1Fichier direct link generator
    Based on https://github.com/Maujar
    """
    regex = r"^([http:\/\/|https:\/\/]+)?.*1fichier\.com\/\?.+"
    gan = re_match(regex, link)
    if not gan:
      raise DirectDownloadLinkException("ERROR: The link you entered is wrong!")
    if "::" in link:
      pswd = link.split("::")[-1]
      url = link.split("::")[-2]
    else:
      pswd = None
      url = link
    try:
      if pswd is None:
        req = rpost(url)
      else:
        pw = {"pass": pswd}
        req = rpost(url, data=pw)
    except:
      raise DirectDownloadLinkException("ERROR: Unable to reach 1fichier server!")
    if req.status_code == 404:
      raise DirectDownloadLinkException("ERROR: File not found/The link you entered is wrong!")
    soup = BeautifulSoup(req.content, 'lxml')
    if soup.find("a", {"class": "ok btn-general btn-orange"}) is not None:
        dl_url = soup.find("a", {"class": "ok btn-general btn-orange"})["href"]
        if dl_url is None:
          raise DirectDownloadLinkException("ERROR: Unable to generate Direct Link 1fichier!")
        else:
          return dl_url
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 3:
        str_2 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_2).lower():
            numbers = [int(word) for word in str(str_2).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException("ERROR: 1fichier is on a limit. Please wait a few minutes/hour.")
            else:
                raise DirectDownloadLinkException(f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.")
        elif "protect access" in str(str_2).lower():
          raise DirectDownloadLinkException(f"ERROR: This link requires a password!\n\n<b>This link requires a password!</b>\n- Insert sign <b>::</b> after the link and write the password after the sign.\n\n<b>Example:</b> https://1fichier.com/?smmtd8twfpm66awbqz04::love you\n\n* No spaces between the signs <b>::</b>\n* For the password, you can use a space!")
        else:
            print(str_2)
            raise DirectDownloadLinkException("ERROR: Failed to generate Direct Link from 1fichier!")
    elif len(soup.find_all("div", {"class": "ct_warn"})) == 4:
        str_1 = soup.find_all("div", {"class": "ct_warn"})[-2]
        str_3 = soup.find_all("div", {"class": "ct_warn"})[-1]
        if "you must wait" in str(str_1).lower():
            numbers = [int(word) for word in str(str_1).split() if word.isdigit()]
            if not numbers:
                raise DirectDownloadLinkException("ERROR: 1fichier is on a limit. Please wait a few minutes/hour.")
            else:
                raise DirectDownloadLinkException(f"ERROR: 1fichier is on a limit. Please wait {numbers[0]} minute.")
        elif "bad password" in str(str_3).lower():
          raise DirectDownloadLinkException("ERROR: The password you entered is wrong!")
        else:
            raise DirectDownloadLinkException("ERROR: Error trying to generate Direct Link from 1fichier!")
    else:
        raise DirectDownloadLinkException("ERROR: Error trying to generate Direct Link from 1fichier!")

def solidfiles(url: str) -> str:
    """ Solidfiles direct link generator
    Based on https://github.com/Xonshiz/SolidFiles-Downloader
    By https://github.com/Jusidama18 """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    pageSource = rget(url, headers = headers).text
    mainOptions = str(re_search(r'viewerOptions\'\,\ (.*?)\)\;', pageSource).group(1))
    return jsonloads(mainOptions)["downloadUrl"]

def krakenfiles(page_link: str) -> str:
    """ krakenfiles direct link generator
    Based on https://github.com/tha23rd/py-kraken
    By https://github.com/junedkh """
    page_resp = rsession().get(page_link)
    soup = BeautifulSoup(page_resp.text, "lxml")
    try:
        token = soup.find("input", id="dl-token")["value"]
    except:
        raise DirectDownloadLinkException(f"Page link is wrong: {page_link}")

    hashes = [
        item["data-file-hash"]
        for item in soup.find_all("div", attrs={"data-file-hash": True})
    ]
    if not hashes:
        raise DirectDownloadLinkException(f"ERROR: Hash not found for : {page_link}")

    dl_hash = hashes[0]

    payload = f'------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name="token"\r\n\r\n{token}\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--'
    headers = {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        "cache-control": "no-cache",
        "hash": dl_hash,
    }

    dl_link_resp = rsession().post(
        f"https://krakenfiles.com/download/{hash}", data=payload, headers=headers)

    dl_link_json = dl_link_resp.json()

    if "url" in dl_link_json:
        return dl_link_json["url"]
    else:
        raise DirectDownloadLinkException(f"ERROR: Failed to acquire download URL from kraken for : {page_link}")

def uploadee(url: str) -> str:
    """ uploadee direct link generator
    By https://github.com/iron-heart-x"""
    try:
        soup = BeautifulSoup(rget(url).content, 'lxml')
        sa = soup.find('a', attrs={'id':'d_l'})
        return sa['href']
    except:
        raise DirectDownloadLinkException(f"ERROR: Failed to acquire download URL from upload.ee for : {url}")
account = {
    'email': APPDRIVE_EMAIL,
    'passwd': APPDRIVE_PASS
    }
def account_login(client, url, email, password):
    """ AppDrive google drive link generator
    By https://github.com/xcscxr """

    if APPDRIVE_EMAIL is None:
        raise DirectDownloadLinkException("ERROR: Appdrive  Email Password not provided")

    data = {
        'email': email,
        'password': password
    }
    client.post(f'https://{urlparse(url).netloc}/login', data=data)

def gen_payload(data, boundary=f'{"-"*6}_'):
    data_string = ''
    for item in data:
        data_string += f'{boundary}\r\n'
        data_string += f'Content-Disposition: form-data; name="{item}"\r\n\r\n{data[item]}\r\n'
    data_string += f'{boundary}--\r\n'
    return data_string

def parse_info(data):
    info = re_findall(r'>(.*?)<\/li>', data)
    info_parsed = {}
    for item in info:
        kv = [s.strip() for s in item.split(':', maxsplit=1)]
        info_parsed[kv[0].lower()] = kv[1]
    return info_parsed

def appdrive(url: str) -> str:
    client = rsession()
    client.headers.update({
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
    })
    account_login(client, url, account['email'], account['passwd'])
    res = client.get(url)
    key = re_findall(r'"key",\s+"(.*?)"', res.text)[0]
    ddl_btn = etree.HTML(res.content).xpath("//button[@id='drc']")
    info_parsed = parse_info(res.text)
    info_parsed['error'] = False
    info_parsed['link_type'] = 'login'  # direct/login
    headers = {
        "Content-Type": f"multipart/form-data; boundary={'-'*4}_",
    }
    data = {
        'type': 1,
        'key': key,
        'action': 'original'
    }
    if len(ddl_btn):
        info_parsed['link_type'] = 'direct'
        data['action'] = 'direct'
    while data['type'] <= 3:
        try:
            response = client.post(url, data=gen_payload(data), headers=headers).json()
            break
        except: data['type'] += 1
    if 'url' in response:
        info_parsed['gdrive_link'] = response['url']
    elif 'error' in response and response['error']:
        info_parsed['error'] = True
        info_parsed['error_message'] = response['message']
    if urlparse(url).netloc == 'driveapp.in' and not info_parsed['error']:
        res = client.get(info_parsed['gdrive_link'])
        drive_link = etree.HTML(res.content).xpath("//a[contains(@class,'btn')]/@href")[0]
        info_parsed['gdrive_link'] = drive_link
    if not info_parsed['error']:
        link = info_parsed.get('gdrive_link')
        return link
    else:
        raise DirectDownloadLinkException(f"{info_parsed['error_message']}")

def gdtot(url: str) -> str:
    """ Gdtot google drive link generator
    By https://github.com/xcscxr """

    if CRYPT is None:
        raise DirectDownloadLinkException("ERROR: CRYPT cookie not provided")

    match = re_findall(r'https?://(.+)\.gdtot\.(.+)\/\S+\/\S+', url)[0]

    with rsession() as client:
        client.cookies.update({'crypt': CRYPT})
        client.get(url)
        res = client.get(f"https://{match[0]}.gdtot.{match[1]}/dld?id={url.split('/')[-1]}")
    matches = re_findall('gd=(.*?)&', res.text)
    try:
        decoded_id = b64decode(str(matches[0])).decode('utf-8')
    except:
        raise DirectDownloadLinkException("ERROR: Try in your broswer, mostly file not found or user limit exceeded!")
    return f'https://drive.google.com/open?id={decoded_id}'

def filepress(url):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        raw = urlparse(url)
        json_data = {
            'id': raw.path.split('/')[-1],
            'method': 'publicDownlaod',
            }
        api = f'{raw.scheme}://api.{raw.hostname}/api/file/downlaod/'
        res = cget('POST', api, headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if 'data' not in res:
        raise DirectDownloadLinkException(f'ERROR: {res["statusText"]}')
    return f'https://drive.google.com/uc?id={res["data"]}&export=download'

def gdtot(url):
    cget = create_scraper().request
    try:
        res = cget('GET', f'https://gdbot.xyz/file/{url.split("/")[-1]}')
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    token_url = etree.HTML(res.content).xpath("//a[contains(@class,'inline-flex items-center justify-center')]/@href")
    if not token_url:
        raise DirectDownloadLinkException('ERROR: Token page url not found')
    token_url = token_url[0]
    try:
        token_page = cget('GET', token_url)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__} with {token_url}')
    path = re_findall('\("(.*?)"\)', token_page.text)
    if not path:
        raise DirectDownloadLinkException('ERROR: Cannot bypass this')
    path = path[0]
    raw = urlparse(token_url)
    final_url = f'{raw.scheme}://{raw.hostname}{path}'
    return sharer_scraper(final_url)

def sharer_scraper(url):
    try:
        cget = create_scraper().request
        url = cget('GET', url).url
        raw = urlparse(url)
        res = cget('GET', url)
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    key = re_findall('"key",\s+"(.*?)"', res.text)
    if not key:
        raise DirectDownloadLinkException("ERROR: Key not found!")
    key = key[0]
    if not etree.HTML(res.content).xpath("//button[@id='drc']"):
        raise DirectDownloadLinkException("ERROR: This link don't have direct download button")
    headers = {
        'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryi3pOrWU7hGYfwwL4',
        'x-token': raw.hostname,
    }
    data = '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action"\r\n\r\ndirect\r\n' \
        f'------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="key"\r\n\r\n{key}\r\n' \
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4\r\nContent-Disposition: form-data; name="action_token"\r\n\r\n\r\n' \
        '------WebKitFormBoundaryi3pOrWU7hGYfwwL4--\r\n'
    try:
        res = cget("POST", url, cookies=res.cookies, headers=headers, data=data).json()
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if "url" not in res:
        raise DirectDownloadLinkException('ERROR: Drive Link not found')
    if "drive.google.com" in res["url"]:
        return res["url"]
    try:
        res = cget('GET', res["url"])
    except Exception as e:
        raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
    if (drive_link := etree.HTML(res.content).xpath("//a[contains(@class,'btn')]/@href")) and "drive.google.com" in drive_link[0]:
        return drive_link[0]
    else:
        raise DirectDownloadLinkException('ERROR: Drive Link not found')
