# -*- coding: utf-8 -*-
#------------------------------------------------------------

import sys
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

import re

from core import jsontools as json
from platformcode import config, logger
from core import scrapertools
from core.item import Item
from core import servertools
from core import httptools

host = 'https://www.porntube.com'
url_api = "%s/api/video/list?order=%s&orientation=%s&p=1&ssr=false"


def mainlist(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=url_api % (host, "date", "straight")))
    itemlist.append(item.clone(title="Popular" , action="lista", url=url_api %  (host, "views", "straight")))
    itemlist.append(item.clone(title="Mas Valorada" , action="lista", url=url_api %  (host, "rating", "straight")))
    itemlist.append(item.clone(title="Longitud" , action="lista", url=url_api %  (host, "duration", "straight")))
    itemlist.append(item.clone(title="Pornstars" , action="canal", url=host + "/api/pornstar/list?order=videos&orientation=straight&p=1&ssr=false"))
    itemlist.append(item.clone(title="Canal" , action="canal", url=host + "/api/channel/list?order=rating&orientation=straight&p=1&ssr=false"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/api/tag/list?orientation=straight&ssr=false"))
    itemlist.append(item.clone(title="Buscar", action="search", orientation= "straight"))

    itemlist.append(Item(channel = item.channel, title = ""))
    itemlist.append(item.clone(title="Trans", action="trans"))
    return itemlist


def trans(item):
    logger.info()
    itemlist = []
    itemlist.append(item.clone(title="Nuevos" , action="lista", url=url_api % (host, "date", "shemale")))
    itemlist.append(item.clone(title="Popular" , action="lista", url=url_api %  (host, "views", "shemale")))
    itemlist.append(item.clone(title="Mas Valorada" , action="lista", url=url_api %  (host, "rating", "shemale")))
    itemlist.append(item.clone(title="Longitud" , action="lista", url=url_api %  (host, "duration", "shemale")))
    itemlist.append(item.clone(title="Pornstars" , action="canal", url=host + "/api/pornstar/list?order=videos&orientation=shemale&p=1&ssr=false"))
    itemlist.append(item.clone(title="Canal" , action="canal", url=host + "/api/channel/list?order=rating&orientation=shemale&p=1&ssr=false"))
    itemlist.append(item.clone(title="Categorias" , action="categorias", url=host + "/api/tag/list?orientation=shemale&ssr=false"))
    itemlist.append(item.clone(title="Buscar", action="search", orientation= "shemale"))
    
    return itemlist


def search(item, texto):
    logger.info()
    texto = texto.replace(" ", "+")
    item.url = "%s/api/search/list?order=%s&orientation=%s&q=%s&p=1&ssr=false" % (host, "date",item.orientation, texto)
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
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    for Video in  data["tags"]["_embedded"]["items"]:
        title = Video["name"]
        thumbnail = Video["thumbDesktop"]
        dir = Video["slug"]
        url = "%s/api/tags/%s?order=%s&orientation=%s&p=1&ssr=false" %(host, dir, "date", "straight")
        plot = ""
        # title = "%s (%s)" % (title, vidnum)
        itemlist.append(item.clone(action="lista", title=title, url=url,
                               thumbnail=thumbnail, plot=plot) )
    return itemlist


def canal(item):
    logger.info()
    itemlist = []
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    if "channel" in item.url:
        s= data["channels"]["_embedded"]["items"]
        page= data["channels"]["page"]
        total= data["channels"]["pages"]
        c = "channels"
    else:
        s= data["pornstars"]["_embedded"]["items"]
        page= data["pornstars"]["page"]
        total= data["pornstars"]["pages"]
        c = "pornstars"
    for Video in s:
        title = Video["name"]
        dir = Video["slug"]
        thumbnail= Video["thumbUrl"]
        vidnum = Video["videoCount"]
        url = "%s/api/%s/%s?order=date&orientation=straight&p=1&ssr=false" % (host,c,dir)
        plot = ""
        title = "%s (%s)" % (title, vidnum)
        itemlist.append(item.clone(action="lista", title=title, url=url,
                               thumbnail=thumbnail, plot=plot) )
    next_page = (page+ 1)
    if next_page < total:
        next_page = re.sub(r"&p=\d+", "&p={0}".format(next_page), item.url)
        itemlist.append(item.clone(action="canal", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def lista(item):
    logger.info()
    itemlist = []
    headers = {'Referer': "%s" % host}
    data = httptools.downloadpage(item.url, headers=headers).json
    if not "/video/" in item.url and not "/search/" in item.url:
        s= data["embedded"]["videos"]["_embedded"]["items"]
        page= data["embedded"]["videos"]["page"]
        total= data["embedded"]["videos"]["pages"]
    else:
        s = data["videos"]["_embedded"]["items"]
        page= data["videos"]["page"]
        total= data["videos"]["pages"]
        
    for Video in s:
        tit = Video["title"]
        id = Video["uuid"]
        time= Video["durationInSeconds"]
        thumbnail = Video["thumbnailsList"][0]
        quality = Video["isHD"]
        url = "%s/embed/%s" % (host,id)
        time = timer(time)
        title = "[COLOR yellow]%s[/COLOR] %s" % (time,tit)
        if quality:
            title = "[COLOR yellow]%s[/COLOR] [COLOR red]HD[/COLOR] %s" % (time,tit)
        contentTitle = title
        thumbnail = thumbnail.replace("\/", "/")
        plot = ""
        action = "play"
        if logger.info() == False:
            action = "findvideos"
        itemlist.append(item.clone(action=action, title=title, url=url,
                              thumbnail=thumbnail, plot=plot, contentTitle = contentTitle))
    next_page = (page+ 1)
    if next_page < total:
        next_page = re.sub(r"&p=\d+", "&p={0}".format(next_page), item.url)
        itemlist.append(item.clone(action="lista", title="[COLOR blue]Página Siguiente >>[/COLOR]", url=next_page) )
    return itemlist


def timer(segundos):
    horas=int(segundos/3600)
    segundos-=horas*3600
    minutos=int(segundos/60)
    segundos-=minutos*60
    if segundos < 10:
        segundos = "0%s" %segundos
    if minutos < 10:
        minutos = "0%s" %minutos
    if horas == 00:
        duration = "%s:%s" % (minutos,segundos)
    else:
        duration = "%s:%s:%s" % (horas,minutos,segundos)
    return duration


def findvideos(item):
    logger.info(item)
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist


def play(item):
    logger.info(item)
    itemlist = []
    itemlist.append(item.clone(action="play", title= "%s", contentTitle = item.title, url=item.url))
    itemlist = servertools.get_servers_itemlist(itemlist, lambda i: i.title % i.server.capitalize())
    return itemlist