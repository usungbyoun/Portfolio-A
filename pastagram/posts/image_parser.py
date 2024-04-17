import urllib.parse
import requests
from bs4 import BeautifulSoup as bs

def parse_images(keyword, cnt):
    img_url_list = []
    keyword_quote = urllib.parse.quote(keyword)

    url = 'https://images.search.yahoo.com/search/images; \
        _ylt=Awr9IlCx7FdgSIEAGZJXNyoA;_ylu==Y29sbwNncT \
        EEcG9zAzEEdnRpZANDMDE2MF8xBHNlYwNwaXZz?p='
    url = url + keyword_quote + '&fr2=piv-web&fr=yfp-t'

    response = requests.get(url)
    soup = bs(response.text, 'html.parser')
    tag_imgs = soup.select('li.ld a > img')

    for tag_img in tag_imgs[:cnt]:
        img_url_list.append(tag_img.attrs['data-src'])

    return img_url_list



    # keyword_quote = urllib.parse.quote(keyword)

    # url = f'https://images.search.yahoo.com/search/images; \
    #             _ylt=Awr9IlCx7FdgSIEAGZJXNyoA;_ylu==Y29sbwNncT \
    #             EEcG9zAzEEdnRpZANDMDE2MF8xBHNlYwNwaXZz?p={keyword_quote}&fr2=piv-web&fr=yfp-t'

    # response = requests.get(url)
    # soup = BeautifulSoup(response.text, 'html.parser')
    # tag_imgs = soup.select('li.ld a > img')

    # for tag_img in tag_imgs[:cnt]:
    #     img_url_list.append(tag_img.attrs['data-src'])

    # return img_url_list