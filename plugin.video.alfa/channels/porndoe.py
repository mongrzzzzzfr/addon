# -*- coding: utf-8 -*-
#------------------------------------------------------------
import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

if PY3:
    import urllib.parse as urlparse                             # Es muy lento en PY2.  En PY3 es nativo
else:
    import urlparse                                             # Usamos el nativo de PY2 que es más rápido

import re

from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools
from bs4 import BeautifulSoup

host = 'https://porndoe.com'


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=host +"/videos"))
    itemlist.append(item.clone(title="Exclusivos" , action="lista", url=host + "/category/74/premium-hd"))
    itemlist.append(item.clone(title="Mas vistos" , action="lista", url=host + "/videos?sort=views-down"))
    itemlist.append(item.clone(title="Mejor valorado" , action="lista", url=host + "/videos?sort=likes-down"))
    itemlist.append(item.clone(title="Mas largo" , action="lista", url=host + "/videos?sort=duration-down"))
    itemlist.append(item.clone(title="PornStar" , action="categorias", url=host + "/pornstars"))
    itemlist.append(item.clone(title="Canal" , action="categorias", url=host + "/channels?sort=ranking"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/categories"))
    itemlist.append(item.clone(title="Buscar", action="search"))
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/search?keywords=%s" % (host,texto)
    try:
        return lista(item)
    except:
        import sys
        for line in sys.exc_info():
            logger.error("%s" % line)
        return []


def categorias(item):
    logger.info()
    itemlist = []
    data = httptools.downloadpage(item.url).data
    data = re.sub(r"\n|\r|\t|&nbsp;|<br>|amp;", "", data)
    if "pornstars" in item.url:
        patron  = 'class="actors-list-item">(.*?)</div>'
    else:
        patron  = 'class="item">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:
        if "channels" in item.url:
            action = "lista"
        else:
            action = "lista2"
        scrapedurl = scrapertools.find_single_match(match,'href="([^"]+)"')
        if "channel-profile" in scrapedurl:
            scrapedurl = scrapedurl.replace("channel-profile", "channel-profile-videos")
            scrapedurl += "?sort=date-down"
        thumbnail = scrapertools.find_single_match(match,'data-src="([^"]+)"')
        scrapedtitle = ""
        scrapedtitle = scrapertools.find_single_match(match,'title="([^"]+)"')
        if not scrapedtitle:
            scrapedtitle = scrapertools.find_single_match(match,'class="item-title">([^<]+)<').strip()
        cantidad = ""
        if "/category" in scrapedurl:
            cantidad = scrapertools.find_single_match(match,'<span class="count">([^<]+)<')
        if "/pornstars-profile" in scrapedurl:
            thumbnail = scrapertools.find_single_match(match,';(https://p.cdn.porndoe.com/image/porn_star/.*?.jpg)')
            cantidad = scrapertools.find_single_match(match,'<span class="-grow">([^<]+)<')
            cantidad = "(%s)" % cantidad
        title = "%s %s" % (scrapedtitle, cantidad)
        scrapedurl = scrapedurl.replace("https://letsdoeit.com", "")
        url = urlparse.urljoin(item.url,scrapedurl)
        itemlist.append(item.clone(action=action, title=title, url=url,
                              fanart=thumbnail, thumbnail=thumbnail, plot="") )
    next_page = scrapertools.find_single_match(data, '<li class="page next page-hide-mobile">.*?href="([^"]+)"')
    if next_page:
        next_page = urlparse.urljoin(item.url,next_page)
        itemlist.append(item.clone(action="categorias", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def create_soup(url, referer=None, unescape=False):
    logger.info()
    if referer:
        data = httptools.downloadpage(url, headers={'Referer': referer}).data
    else:
        data = httptools.downloadpage(url).data
    if unescape:
        data = scrapertools.unescape(data)
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def lista(item):
    logger.info()
    itemlist = []
    soup = create_soup(item.url)
    matches = soup.find_all('div', class_='video-item')
    for elem in matches:
        url = elem.a['href']
        if "redirect" in url:
            continue
        title = elem.find('a', class_='video-item-title')['title']
        thumbnail = elem.svg['data-src']
        time = elem['data-duration']
        hd = elem['data-hd']
        vr = elem['data-vr']
        quality = ""
        if "true" in vr: quality = "VR"
        if "true" in hd: quality = "HD"
        url = urlparse.urljoin(host,url)
        title = "[COLOR yellow]%s[/COLOR] [COLOR red]%s[/COLOR] %s" % (time,quality,title)
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url, thumbnail=thumbnail,
                                fanart=thumbnail, contentTitle=title ))
    next_page = soup.find('a', class_='pager-next')
    if next_page:
        next_page = next_page['href']
        next_page = urlparse.urljoin(host,next_page)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def findvideos(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist
