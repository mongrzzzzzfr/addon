# -*- coding: utf-8 -*-
# --------------------------------------------------------
# Conector Fembed By Alfa development Group
# --------------------------------------------------------

from core import httptools
from core import scrapertools
from platformcode import logger


def test_video_exists(page_url):
    global data
    logger.info("(page_url='%s')" % page_url)
    _id = scrapertools.find_single_match(page_url, "/(?:f|v)/([A-z0-9_-]+)")
    if _id:
        page_url = 'https://www.fembed.com/api/source/%s' % _id
    post = "r=&d=feurl.com"
    data = httptools.downloadpage(page_url, post=post).json
    status = data.get('success', '')
    if status == False:
        return False, "[Fembed] El video ha sido borrado"
    elif not status:
        return False, "[Fembed] Error al acceder al video"
    return True, ""


def get_video_url(page_url, user="", password="", video_password=""):
    logger.info("(page_url='%s')" % page_url)
    video_urls = []
    base_sub = "https://thumb.fvs.io/asset/userdata/240560/caption/%s/%s.%s"
    try:
        sub_data = data.get("captions",[])[0]
        subtitle= base_sub % (sub_data['hash'], sub_data['id'], sub_data['extension'])
    except:
        subtitle = ''
    for url in data["data"]:
        video_urls.append([url["label"] + " [Fembed]", url["file"],0, subtitle])
    return video_urls
