# -*- coding: utf-8 -*-
"""
@channel: Playdede
@for: Alfa addon
@author: Alfa Develop Group
@maintainer: SistemaRayoXP
"""
import sys, re, datetime
PY3 = False
if sys.version_info[0] >= 3: PY3 = True; unicode = str; unichr = chr; long = int

from bs4 import BeautifulSoup
from core import httptools, jsontools, scrapertools, servertools, tmdb
from core.item import Item
from platformcode import config, logger, platformtools, unify
from channelselector import get_thumb

host = 'https://playdede.com'

IDIOMAS = {'lat': 'LAT', 'esp': 'CAST', 'espsub': 'VOSE', 'engsub': 'VOS', 'eng': 'VO'}
SERVIDORES = {'11': 'clipwatching', '57': 'aparatcam', '12': 'gamovideo', '56': 'doodstream', '4': 'upstream', '5': 'cloudvideo', '55': 'okru', '12': 'powvideo', '2': 'streamplay', '50': 'fembed'}

list_language = list(IDIOMAS.values())
list_quality = ['HD1080', 'HD720', 'HDTV', 'DVDRIP']
list_servers = list(SERVIDORES.values())

show_langs = config.get_setting('show_langs', channel='playdede')
account = None

def create_soup(url, post=None, headers=None, referer=False):
    logger.info()

    data = httptools.downloadpage(url, post=post, headers=headers, referer=referer).data
    soup = BeautifulSoup(data, "html5lib", from_encoding="utf-8")
    return soup


def login():
    logger.info()

    usuario = config.get_setting('user', channel='playdede')
    clave = config.get_setting('pass', channel='playdede')
    credentials = {'user': usuario,
                   'pass': clave,
                   '_method': 'auth/login'}

    if not usuario:
        return False

    if not clave:
        platformtools.dialog_notification("Falta la contraseña", "Revisa la contraseña en la configuración del canal.", sound=False)
        logger.error('Contraseña no encontrada')
        return False

    if not httptools.get_cookie(host, 'MoviesWebsite'):
        httptools.downloadpage(host)

    if httptools.get_cookie(host, 'utoken'):
        return True

    logger.info('Casi...')

    httptools.downloadpage('{}/ajax.php'.format(host), post=credentials, referer=True, add_host=True, headers={'Origin': host})
    httptools.downloadpage(host)
    
    if httptools.get_cookie(host, 'utoken'):
        logger.info('¡Token de sesión conseguido!')
        platformtools.dialog_notification("Sesión iniciada satisfactoriamente", "Disfruta del canal :)", sound=False)
        return True
    else:
        logger.error('¡Ouh! Parece que no hay token de inicio de sesión, reparar...')
        platformtools.dialog_notification("Error al iniciar sesión", "Verifica que el usuario y contraseña sean correctos y que puedas iniciar sesión en la web. Si están correctos, genera un reporte desde el menú principal", sound=False)
        return False


def logout(item):
    logger.info()

    if PY3:
        import urllib.parse as urlparse
    else:
        import urlparse

    # Borramos las cookies
    domain = urlparse.urlparse(host).netloc
    dict_cookie = {"domain": domain, 'expires': 0}
    httptools.set_cookies(dict_cookie)

    # Borramos el estado de login
    config.set_setting("user", "", channel="playdede")
    config.set_setting("pass", "", channel="playdede")

    platformtools.dialog_notification("Sesión cerrada", "Reconfigura las credenciales", sound=False)
    
    # Mandamos a configuración del canal
    return settings(item)


def mainlist(item):
    logger.info()

    global account
    account = login()
    itemlist = []

    if not account:
        platformtools.dialog_notification("Registro necesario", "Regístrate en playdede.com e ingresa tus credenciales para utilizar este canal", sound=False)
        itemlist.append(
            Item(
                action = "settings",
                channel = item.channel,
                folder = False,
                text_bold = True,
                thumbnail = get_thumb("setting_0.png"),
                title = "Debes iniciar sesión para utilizar este canal",
            )
        )

    else:
        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                fanart = item.fanart,
                list_type = 'movies',
                thumbnail = get_thumb("movies", auto=True),
                title = "Películas",
                url = "{}/peliculas/".format(host),
                viewType = 'movies'
            )
        )
        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                fanart = item.fanart,
                list_type = 'tvshows',
                thumbnail = get_thumb("tvshows", auto=True),
                title = "Series",
                url = "{}/series/".format(host),
                viewType = 'tvshows'
            )
        )
        itemlist.append(
            Item(
                action = "list_all",
                channel = item.channel,
                fanart = item.fanart,
                list_type = 'tvshows',
                thumbnail = get_thumb("animacion", auto=True),
                title = "Animación",
                url = "{}/animes/".format(host),
                viewType = 'tvshows'
            )
        )
        itemlist.append(
            Item(
                action = "genres",
                channel = item.channel,
                fanart = item.fanart,
                thumbnail = get_thumb("colections", auto=True),
                title = "Listas",
                url = "{}/listas/".format(host),
                viewType = 'videos'
            )
        )
        itemlist.append(
            Item(
                action = "search",
                channel = item.channel,
                fanart = item.fanart,
                thumbnail = get_thumb("search", auto=True),
                title = "Buscar",
                url = "{}/search/?s=".format(host),
                viewType = "movies"
            )
        )
        itemlist.append(
            Item(
                action = "logout",
                channel = item.channel,
                folder = False,
                plot = "Cierra la sesión",
                title = "Cerrar sesión", 
                thumbnail = get_thumb("setting_0.png")
            )
        )
        itemlist.append(
            Item(
                action = "settings",
                channel = item.channel,
                folder = False,
                plot = "Configura tus credenciales, búsqueda global, etc.",
                title = "Configurar canal", 
                thumbnail = get_thumb("setting_0.png")
            )
        )
    return itemlist


def settings(item):
    logger.info()

    platformtools.show_channel_settings()
    platformtools.itemlist_refresh()

    return 


def genres(item):
    logger.info()

    itemlist = []
    soup = create_soup(item.url)

    if not soup:
        platformtools.dialog_notification("Cambio de estructura", "Reporta el error desde el menú principal", sound=False)

        return itemlist

    items = soup.find("div", id="movidyMain").find_all("article")

    for article in items:
        data = article.find("a", attrs={"up-target": "body"})
        fanart = article.find(class_="postersMov").find_all("img")[1]['src']
        thumb = article.find(class_="postersMov").find("img")['src']
        title = data.find("h2").text
        plot = "[COLOR=green]Creado por:[/COLOR] {}\n[COLOR=red]Corazones:[/COLOR] {}".format(article.find(class_="kcdirs").span.text, article.find("div", class_="createdbyT").span.text)
        url = data['href']

        it = item.clone(
                action = "list_all",
                fanart = fanart,
                plot = plot,
                thumbnail = thumb,
                title = title,
                tmdb = False,
                url = url
            )

        itemlist.append(it)

    btnnext = soup.find("div", class_="pagPlaydede")
    
    if btnnext:
        itemlist.append(
            item.clone(
                title = "Siguiente >",
                url = btnnext.find("a")['href']
            )
        )

    return itemlist


def list_all(item):
    logger.info()

    itemlist = []
    soup = create_soup(item.url)

    if not soup:
        platformtools.dialog_notification("Cambio de estructura", "Reporta el error desde el menú principal", sound=False)
        return itemlist

    items = soup.find('div', id='archive-content').find_all('article')

    for article in items:
        data = article.find('div', class_='data')
        infoLabels = {'year': data.find('p').text, 'genres': data.find('span').text}
        thumbnail = article.find('img')['src']
        title = data.find('h3').text

        if 'tmdb.org' in thumbnail:
            infoLabels['filtro'] = scrapertools.find_single_match(thumbnail, "/(\w+)\.\w+$")

        it = Item(
                action = 'findvideos',
                channel = item.channel,
                fanart = item.fanart,
                infoLabels = infoLabels,
                thumbnail = thumbnail,
                title = title,
                url = article.find('a')['href']
            )

        if item.list_type and item.list_type in ['movies', 'tvshows']:
            list_type = item.list_type

        elif item.viewType and item.list_type in ['movies', 'tvshows']:
            list_type = item.list_type

        else:
            if 'serie' in it.url:
                list_type = 'tvshows'

            elif 'pelicula' in it.url:
                list_type = 'movies'

        if list_type == 'tvshows':
            it.action = 'seasons'
            it.contentSerieName = title
            it.contentType = 'tvshow'
            it.viewType = 'episodes'

        elif list_type == 'movies':
            it.contentTitle = title
            it.contentType = 'movie'
            it.viewType = 'movies'

        itemlist.append(it)

    if not isinstance(item.tmdb, bool) or item.tmdb != False:
        tmdb.set_infoLabels(itemlist, True)

    return itemlist


def search(item, texto):
    logger.info()

    try:
        if texto:
            texto = scrapertools.slugify(texto).replace('-', '+')
            item.url = '{}{}'.format(item.url, texto)

            return list_all(item)

        else:
            return

    except:
        # Se captura la excepción, para no interrumpir al buscador global si un canal falla
        for line in sys.exc_info():
            logger.error("%s" % line)

        return []


def seasons(item):
    logger.info()

    itemlist = []
    soup = create_soup(item.url)
    items = soup.find('div', id='seasons').find_all('div', class_='se-c')

    for div in items:
        season = div['data-season']

        itemlist.append(
            item.clone(
                action = 'episodesxseason',
                contentSeason = season,
                episode_data = str(div),
                title = config.get_localized_string(60027) % season
            )
        )

    tmdb.set_infoLabels(itemlist, True)

    return itemlist


def episodios(item):
    logger.info()

    itemlist = []
    templist = seasons(item)

    for tempitem in templist:
        itemlist += episodesxseason(tempitem)

    return itemlist


def episodesxseason(item):
    logger.info()

    itemlist = []
    soup = BeautifulSoup(item.episode_data, "html5lib", from_encoding="utf-8")
    items = soup.find('ul', class_='episodios').find_all('li')

    for li in items:
        episode = scrapertools.find_single_match(li.find('div', class_='numerando').text, '\d+ - (\d+)')
        infoLabels = item.infoLabels
        infoLabels['episode'] = episode
        title = '{}x{} - {}'.format(item.contentSeason, episode, li.find('div', class_='epst').text)

        itemlist.append(
            Item(
                action = 'findvideos',
                channel = item.channel,
                contentEpisode = episode,
                infoLabels = infoLabels,
                thumbnail = li.find('img')['src'],
                title = title,
                url = li.find('a')['href']
            )
        )

    tmdb.set_infoLabels(itemlist, True)

    return itemlist


def findvideos(item):
    logger.info()

    itemlist = []
    soup = create_soup(item.url)
    items = []
    linklists = soup.findAll('div', class_='linkSorter')
    items.extend(soup.find('div', class_='contEP contepID_1 contEP_A').find('div', class_='innerSelector').find_all('div', class_="playerItem"))

    for lst in linklists:
        items.extend(lst.find_all('li'))

    for li in items:
        language = IDIOMAS.get(li.get('data-lang', '').lower(), '')
        quality = li.get('data-quality', '')

        if quality:
            server = SERVIDORES.get(li.get('data-provider', '').lower(), '')
            url = li.find('a')['href']

        else:
            data = li.find('div', class_='meta')

            if data:
                quality = data.p.span.text
                server = data.find('h3').text
                url = 'https://playdede.com/ajax.php'

        title = item.title

        if not server:
            server = servertools.get_server_from_url(url)

        if server == 'directo':
            continue

        title = "{}".format(server.title())

        if language:
            title = unify.add_languages(title, language)

        if quality:
            title += ' [COLOR=cyan][{}][/COLOR]'.format(quality.upper())

        itemlist.append(
            item.clone(
                action = 'play',
                language = language,
                player = li.get('data-loadplayer', ''),
                quality = quality,
                server = server,
                title = title,
                url = url
            )
        )

    return itemlist


def play(item):
    logger.info()

    if host in item.url and item.player:
        data = httptools.downloadpage("{}/embed.php?id={}".format(host, item.player), post={}).data
        realurl = scrapertools.find_single_match(data, """iframe src=["'](.+?)["']""")

        return [item.clone(url = realurl)]

    else:
        return [item]