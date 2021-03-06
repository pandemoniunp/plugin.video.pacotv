# -*- coding: utf-8 -*-
#------------------------------------------------------------
# HarryTV - XBMC Add-on by  ()
# Version 0.2.92 (18.07.2014)
#------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Librerías Plugintools por Jesús (www.mimediacenter.info)


import os
import sys
import urllib
import urllib2
import re
import string
import shutil
import zipfile
import time

import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin

import plugintools


home = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.HarryTV/', ''))
tools = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.HarryTV/resources/tools', ''))
addons = xbmc.translatePath(os.path.join('special://home/addons/', ''))
resources = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.HarryTV/resources', ''))
art = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.HarryTV/art', ''))
tmp = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.HarryTV/tmp', ''))
playlists = xbmc.translatePath(os.path.join('special://home/addons/playlists', ''))

icon = art + 'icon.png'
fanart = 'fanart.jpg'


def allmyvideos(params):
    plugintools.log("[HarryTV-0.3.0].allmyvideos " + repr(params))

    url = params.get("url")
    url = url.split("/")
    url_fixed = 'http://www.allmyvideos.net/' +  'embed-' + url[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    plugintools.log("data= "+body)

    r = re.findall('"file" : "(.+?)"', body)
    for entry in r:
        plugintools.log("vamos= "+entry)
        if entry.endswith("mp4?v2"):
            url = entry + '&direct=false'
            params["url"]=url
            plugintools.log("url= "+url)
            plugintools.play_resolved_url(url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Resolviendo enlace...", 3 , art+'icon.png'))


def streamcloud(params):
    plugintools.log("[HarryTV-0.3.0].streamcloud " + repr(params))

    url = params.get("url")

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
    plugintools.log("data= "+body)

    # Barra de progreso para la espera de 10 segundos
    progreso = xbmcgui.DialogProgress()
    progreso.create("HarryTV", "Abriendo Streamcloud..." , url )

    i = 13000
    j = 0
    percent = 0
    while j <= 13000 :
        percent = ((j + ( 13000 / 10.0 )) / i)*100
        xbmc.sleep(i/10)  # 10% = 1,3 segundos
        j = j + ( 13000 / 10.0 )
        msg = "Espera unos segundos, por favor... "
        percent = int(round(percent))
        print percent
        progreso.update(percent, "" , msg, "")
        

    progreso.close()
    
    media_url = plugintools.find_single_match(body , 'file\: "([^"]+)"')
    
    if media_url == "":
        op = plugintools.find_single_match(body,'<input type="hidden" name="op" value="([^"]+)"')
        usr_login = ""
        id = plugintools.find_single_match(body,'<input type="hidden" name="id" value="([^"]+)"')
        fname = plugintools.find_single_match(body,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = plugintools.find_single_match(body,'<input type="hidden" name="referer" value="([^"]*)"')
        hashstring = plugintools.find_single_match(body,'<input type="hidden" name="hash" value="([^"]*)"')
        imhuman = plugintools.find_single_match(body,'<input type="submit" name="imhuman".*?value="([^"]+)">').replace(" ","+")

        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
        request_headers.append(["Referer",url])
        body,response_headers = plugintools.read_body_and_headers(url, post=post, headers=request_headers)
        plugintools.log("data= "+body)
        

        # Extrae la URL
        media_url = plugintools.find_single_match( body , 'file\: "([^"]+)"' )
        plugintools.log("media_url= "+media_url)
        plugintools.play_resolved_url(media_url)

        if 'id="justanotice"' in body:
            plugintools.log("[streamcloud.py] data="+body)
            plugintools.log("[streamcloud.py] Ha saltado el detector de adblock")
            return -1

  

def playedto(params):
    plugintools.log("[HarryTV-0.3.0].playedto " + repr(params))

    url = params.get("url")
    url = url.split("/")
    url_fixed = "http://played.to/embed-" + url[3] +  "-640x360.html"
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    body = body.strip()
    
    if body == "<center>This video has been deleted. We apologize for the inconvenience.</center>":
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Enlace borrado...", 3 , art+'icon.png'))
    else:
        r = re.findall('file(.+?)\n', body)

        for entry in r:
            entry = entry.replace('",', "")
            entry = entry.replace('"', "")
            entry = entry.replace(': ', "")
            entry = entry.strip()
            plugintools.log("vamos= "+entry)
            if entry.endswith("flv"):
                plugintools.play_resolved_url(entry)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Resolviendo enlace...", 3 , art+'icon.png'))
                params["url"]=entry
                plugintools.log("URL= "+entry)



def vidspot(params):
    plugintools.log("[HarryTV-0.3.0].vidspot " + repr(params))
    
    url = params.get("url")
    url = url.split("/")
    url_fixed = 'http://www.vidspot.net/' +  'embed-' + url[3] +  '.html'
    plugintools.log("url_fixed= "+url_fixed)

    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    body,response_headers = plugintools.read_body_and_headers(url_fixed, headers=request_headers)
    plugintools.log("data= "+body)

    r = re.findall('"file" : "(.+?)"', body)
    for entry in r:
        plugintools.log("vamos= "+entry)
        if entry.endswith("mp4?v2"):
            url = entry + '&direct=false'
            params["url"]=url
            plugintools.log("url= "+url)
            plugintools.play_resolved_url(url)
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Resolviendo enlace...", 3 , art+'icon.png'))


def vk(params):
    plugintools.log("[HarryTV-0.3.0].vk " + repr(params))

    # http://vk.com/video_ext.php?oid=238208017&id=169663934&hash=1fc3ef827b751943&hd=1

    data = plugintools.read(params.get("url"))
    data = data.replace("amp;", "")
    
    if "This video has been removed from public access" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
    else:
        match = plugintools.find_single_match(data, '<param name="flashvars"(.*?)</param>')
        plugintools.log("match= "+match)
        matches = plugintools.find_multiple_matches(match, 'vkid(.*?)&')
        for entry in matches:
            plugintools.log("match= "+entry)

        video_host = plugintools.find_single_match(data, 'var video_host = \'(.*?)\';')
        print 'video_host',video_host
        video_uid = plugintools.find_single_match(data, 'var video_uid = \'(.*?)\';')
        print 'video_uid',video_uid        
        video_vtag = plugintools.find_single_match(data, 'var video_vtag = \'(.*?)\';')
        print 'video_vtag',video_vtag        
        video_no_flv = plugintools.find_single_match(data, 'var video_no_flv = \'(.*?)\';')
        print 'video_no_flv',video_no_flv        
        video_max_hd = plugintools.find_single_match(data, 'var video_max_hd = \'(.*?)\';')
        print 'video_max_hd',video_max_hd

        if video_no_flv.strip() == "0" and video_uid != "0":
            media = 'flv'

        url_sintax = video_host + video_uid + '/video/' + video_vtag
        plugintools.log("url_sintax= "+url_sintax)

        # Control para el caso en que no se encuentren los parámetros por "Acceso prohibido o restringido"
        if url_sintax == "/video":
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
        else:            
            url_1 = url_sintax + '.240.mp4'
            url_extended_1 = plugintools.find_single_match(match, 'url240=(.*?)\&')
            url_2 = url_sintax + '.360.mp4'
            url_extended_2 = plugintools.find_single_match(match, 'url360=(.*?)\&')
            url_3 = url_sintax + '.480.mp4'
            url_extended_3 = plugintools.find_single_match(match, 'url480=(.*?)\&')
            url_4 = url_sintax + '.720.mp4'
            url_extended_4 = plugintools.find_single_match(match, 'url720=(.*?)\&')

            video_urls = [url_extended_1, url_extended_2, url_extended_3, url_extended_4]
            print video_urls
            
            dialog_vk = xbmcgui.Dialog()
            selector = ""        
            
            if video_max_hd == "0":
                selector = dialog_vk.select('HarryTV', ['240'])

            if video_max_hd == "1":
                selector = dialog_vk.select('HarryTV', ['240', '360'])

            if video_max_hd == "2":
                selector = dialog_vk.select('HarryTV', ['240', '360', '480'])

            if video_max_hd == "3":
                selector = dialog_vk.select('HarryTV', ['240', '360', '480', '720'])                      

            i = 0
            while i<= video_max_hd :
                if selector == i:
                    plugintools.log("URL_vk= "+video_urls[i])
                    url = video_urls[i]
                    if selector == "":
                        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo ya no está disponible", 3 , art+'icon.png'))
                    else:
                        plugintools.play_resolved_url(url)

                i = i + 1


def nowvideo(params):
    plugintools.log("[HarryTV-0.3.0].nowvideo " + repr(params))

    data = plugintools.read(params.get("url"))
    #data = data.replace("amp;", "")
    
    if "The file is being converted" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo está en proceso", 3 , art+'icon.png'))
    elif "no longer exists" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo ha sido borrado", 3 , art+'icon.png'))        
    else:
        #plugintools.log("data= "+data)
        domain = plugintools.find_single_match(data, 'flashvars.domain="([^"]+)')
        video_id = plugintools.find_single_match(data, 'flashvars.file="([^"]+)')
        filekey = plugintools.find_single_match(data, 'flashvars.filekey=([^;]+)')

        # En la página nos da el token de esta forma (siendo fkzd el filekey): var fkzd="83.47.1.12-8d68210314d70fb6506817762b0d495e";

        token_txt = 'var '+filekey
        #plugintools.log("token_txt= "+token_txt)
        token = plugintools.find_single_match(data, filekey+'=\"([^"]+)')
        token = token.replace(".","%2E").replace("-","%2D")
        
        #plugintools.log("domain= "+domain)   
        #plugintools.log("video_id= "+video_id)
        #plugintools.log("filekey= "+filekey)
        #plugintools.log("token= "+token)
        
        if video_id == "":
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Error!", 3 , art+'icon.png'))
        else:
            #http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=83%2E47%2E1%2E12%2D8d68210314d70fb6506817762b0d495e&file=b5c8c44fc706f&cid=1
            url = 'http://www.nowvideo.sx/api/player.api.php?user=undefined&pass=undefined&cid3=undefined&numOfErrors=0&cid2=undefined&key=' + token + '&file=' + video_id + '&cid=1'

            # Vamos a lanzar una petición HTTP de esa URL
            referer = 'http://www.nowvideo.sx/video/b5c8c44fc706f'
            request_headers=[]
            request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
            request_headers.append(["Referer",referer])
            body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
            # plugintools.log("data= "+body)
            # body= url=http://s173.coolcdn.ch/dl/04318aa973a3320b8ced6734f0c20da3/5440513e/ffe369cb0656c0b8de31f6ef353bcff192.flv&title=The.Black.Rider.Revelation.Road.2014.DVDRip.X264.AC3PLAYNOW.mkv%26asdasdas&site_url=http://www.nowvideo.sx/video/b5c8c44fc706f&seekparm=&enablelimit=0

            body = body.replace("url=", "")
            body = body.split("&")

            if len(body) >= 0:
                print 'body',body
                url = body[0]
                plugintools.play_resolved_url(url)
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Cargando vídeo...", 1 , art+'icon.png'))
            else:
                xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Error!", 3 , art+'icon.png'))                

         
''' En el navegador...

        flashvars.domain="http://www.nowvideo.sx";
        flashvars.file="b5c8c44fc706f";
        flashvars.filekey=fkzd;
        flashvars.advURL="0";
        flashvars.autoplay="false";
        flashvars.cid="1";

'''


def tumi(params):
    plugintools.log("[HarryTV[0.3.0].Tumi "+repr(params))

    data = plugintools.read(params.get("url"))
    
    if "Video is processing now" in data:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "El archivo está en proceso", 3 , art+'icon.png'))       
    else:
        # Vamos a buscar el ID de la página embebida
        matches = plugintools.find_multiple_matches(data, 'add_my_acc=(.*?)\"')
        for entry in matches:
            print 'match',entry
            # http://tumi.tv/embed-i9l4mr7jph1a.html
            url = 'http://tumi.tv/embed-' + entry + '.html'
            
            # Petición HTTP de esa URL
            request_headers=[]
            request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
            request_headers.append(["Referer",params.get("url")])
            body,response_headers = plugintools.read_body_and_headers(url, headers=request_headers)
            plugintools.log("body= "+body)
            video_url= plugintools.find_single_match(body, 'file\: \"(.*?)\"')
            plugintools.log("video_url= "+video_url)
            plugintools.add_item(action="play", title= "hola" , url = video_url , folder = False , isPlayable = True)
            plugintools.play_resolved_url(video_url)

            
def veehd(params):
    plugintools.log("[HarryTV-0.3.05].veehd" + repr(params))
    
    uname = plugintools.get_setting("veehd_user")
    pword = plugintools.get_setting("veehd_pword")
    if uname == '' or pword == '':
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Debes configurar el identificador para Veehd.com", 3 , art+'icon.png'))
        return
    
    url = params.get("url")
    url_login = 'http://veehd.com/login'
    
    request_headers=[]
    request_headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.65 Safari/537.31"])
    request_headers.append(["Referer",url])
    
    post = {'ref': url, 'uname': uname, 'pword': pword, 'submit': 'Login', 'terms': 'on'}
    post = urllib.urlencode(post)
    
    body,response_headers = plugintools.read_body_and_headers(url_login, post=post, headers=request_headers, follow_redirects=True)
    vpi = plugintools.find_single_match(body, '"/(vpi.+?h=.+?)"')
    
    if not vpi:
        if 'type="submit" value="Login" name="submit"' in body:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Error al identificarse en Veehd.com", 3 , art+'icon.png'))
        else:
            xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Error buscando el video en Veehd.com", 3 , art+'icon.png'))            
        return
    
    req = urllib2.Request('http://veehd.com/'+vpi)
    for header in request_headers:
        req.add_header(header[0], header[1]) # User-Agent
    response = urllib2.urlopen(req)
    body = response.read()
    response.close()

    va = plugintools.find_single_match(body, '"/(va/.+?)"')
    if va:
        req = urllib2.Request('http://veehd.com/'+va)
        for header in request_headers:
            req.add_header(header[0], header[1]) # User-Agent
        urllib2.urlopen(req)

    req = urllib2.Request('http://veehd.com/'+vpi)
    for header in request_headers:
        req.add_header(header[0], header[1]) # User-Agent
    response = urllib2.urlopen(req)
    body = response.read()
    response.close()

    video_url = False
    if 'application/x-shockwave-flash' in body:
        video_url = urllib.unquote(plugintools.find_single_match(body, '"url":"(.+?)"'))
    elif 'video/divx' in body:
        video_url = urllib.unquote(plugintools.find_single_match(body, 'type="video/divx"\s+src="(.+?)"'))

    if not video_url:
        xbmc.executebuiltin("Notification(%s,%s,%i,%s)" % ('HarryTV', "Error abriendo el video en Veehd.com", 3 , art+'icon.png'))
        return

    plugintools.log("video_url= "+video_url)
    plugintools.play_resolved_url(video_url)

def streaminto(params):
    plugintools.log("[HarryTV-0.3.05].streaminto "+repr(params))

    page_url = params.get("url")
    
    try:
        if not url.startswith("http://streamin.to/embed-"):
            videoid = plugintools.find_single_match(url,"streamin.to/([a-z0-9A-Z]+)")
            page_url = "http://streamin.to/embed-"+videoid+".html"

    except:
        plugintools.log("page_url= "+page_url)
        pass

    
    # Leemos el código web
    request_headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    #data = plugintools.read(page_url , headers=headers)
    data,response_headers = plugintools.read_body_and_headers(page_url, headers=request_headers)      
    patron_flv = 'file: "([^"]+)"'    
    patron_jpg = 'image: "(http://[^/]+/)'
    
    try:
        host = plugintools.find_single_match(data, patron_jpg)
        plugintools.log("[streaminto.py] host="+host)
        flv_url = plugintools.find_single_match(data, patron_flv)
        plugintools.log("[streaminto.py] flv_url="+flv_url)
        flv = host+flv_url.split("=")[1]+"/v.flv"
        plugintools.log("[streaminto.py] flv="+flv)        
    except:
        plugintools.log("[streaminto.py] opcion 2")
        op = plugintools.find_single_match(data,'<input type="hidden" name="op" value="([^"]+)"')
        plugintools.log("[streaminto.py] op="+op)
        usr_login = ""
        id = plugintools.find_single_match(data,'<input type="hidden" name="id" value="([^"]+)"')
        plugintools.log("[streaminto.py] id="+id)
        fname = plugintools.find_single_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
        plugintools.log("[streaminto.py] fname="+fname)
        referer = plugintools.find_single_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
        plugintools.log("[streaminto.py] referer="+referer)
        hashstring = plugintools.find_single_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
        plugintools.log("[streaminto.py] hashstring="+hashstring)
        imhuman = plugintools.find_single_match(data,'<input type="submit" name="imhuman".*?value="([^"]+)"').replace(" ","+")
        plugintools.log("[streaminto.py] imhuman="+imhuman)
        
        import time
        time.sleep(10)
        
        # Lo pide una segunda vez, como si hubieras hecho click en el banner
        #op=download1&usr_login=&id=z3nnqbspjyne&fname=Coriolanus_DVDrip_Castellano_by_ARKONADA.avi&referer=&hash=nmnt74bh4dihf4zzkxfmw3ztykyfxb24&imhuman=Continue+to+Video
        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
        request_headers.append(["Referer",page_url])
        data_video = plugintools.read_body_and_headers( page_url , post=post, headers=request_headers )
        data_video = data_video[0]
        rtmp = plugintools.find_single_match(data_video, 'streamer: "([^"]+)"')
        print 'rtmp',rtmp
        video_id = plugintools.find_single_match(data_video, 'file: "([^"]+)"')
        print 'video_id',video_id
        swf = plugintools.find_single_match(data_video, 'src: "(.*?)"')
        print 'swf',swf
        url = rtmp+' swfUrl='+swf + ' playpath='+video_id+"/v.flv"
        print 'url',url      
        

    plugintools.play_resolved_url(url)


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    encontrados.add("http://streamin.to/embed-theme.html")
    encontrados.add("http://streamin.to/embed-jquery.html")
    encontrados.add("http://streamin.to/embed-s.html")
    encontrados.add("http://streamin.to/embed-images.html")
    encontrados.add("http://streamin.to/embed-faq.html")
    encontrados.add("http://streamin.to/embed-embed.html")
    encontrados.add("http://streamin.to/embed-ri.html")
    encontrados.add("http://streamin.to/embed-d.html")
    encontrados.add("http://streamin.to/embed-css.html")
    encontrados.add("http://streamin.to/embed-js.html")
    encontrados.add("http://streamin.to/embed-player.html")
    encontrados.add("http://streamin.to/embed-cgi.html")
    devuelve = []

    #http://streamin.to/z3nnqbspjyne
    patronvideos  = 'streamin.to/([a-z0-9A-Z]+)'
    plugintools.log("[streaminto.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for entry in matches:
        url = "http://streamin.to/embed-"+entry+".html"
        if url not in encontrados:
            plugintools.log("URL= "+url)
        else:
            plugintools.log("URL duplicada"+url)

    #http://streamin.to/embed-z3nnqbspjyne.html
    patronvideos  = 'streamin.to/embed-([a-z0-9A-Z]+)'
    plugintools.log("[streaminto.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streaminto]"
        url = "http://streamin.to/embed-"+match+".html"
        if url not in encontrados:
            plugintools.log("URL= "+url)
            devuelve.append( [ titulo , url , 'streaminto' ] )
            encontrados.add(url)
        else:
            plugintools.log("URL duplicada="+url)

    return devuelve


#scrapertools.get_filename_from_url(media_url)[-4:]
def get_filename_from_url(url):
    plugintools.log("[HarryTV-0.3.05].get_filename_from_url "+url)
    
    import urlparse
    parsed_url = urlparse.urlparse(url)
    try:
        filename = parsed_url.path
    except:
        # Si falla es porque la implementación de parsed_url no reconoce los atributos como "path"
        if len(parsed_url)>=4:
            filename = parsed_url[2]
        else:
            filename = ""

    plugintools.log("filename= "+filename)
    return filename



def powvideo(params):
    plugintools.log("[HarryTV-0.3.05].powvideos "+repr(params))

    url = params.get("url")

    # Leemos el código web
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data,headers = plugintools.read_body_and_headers(url, headers=headers)      
    plugintools.log("data= "+data)
    
    try:
        '''
        <input type="hidden" name="op" value="download1">
        <input type="hidden" name="usr_login" value="">
        <input type="hidden" name="id" value="auoxxtvyquoy">
        <input type="hidden" name="fname" value="Star.Trek.Into.Darkness.2013.HD.m720p.LAT.avi">
        <input type="hidden" name="referer" value="">
        <input type="hidden" name="hash" value="1624-83-46-1377796069-b5e6b8f9759d080a3667adad637f00ac">
        <input type="submit" name="imhuman" value="Continue to Video" id="btn_download">
        '''
        option = plugintools.find_single_match(data,'<input type="hidden" name="op" value="(down[^"]+)"')
        id = plugintools.find_single_match(data,'<input type="hidden" name="id" value="([^"]+)"')
        fname = plugintools.find_single_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = plugintools.find_single_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
        hashvalue = plugintools.find_single_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
        submitbutton = plugintools.find_single_match(data,'<input type="submit" name="imhuman" value="([^"]+)"').replace(" ","+")

        time.sleep(5)

        # Lo pide una segunda vez, como si hubieras hecho click en el banner
        #op=download1&usr_login=&id=auoxxtvyquoy&fname=Star.Trek.Into.Darkness.2013.HD.m720p.LAT.avi&referer=&hash=1624-83-46-1377796019-c2b422f91da55d12737567a14ea3dffe&imhuman=Continue+to+Video
        #op=search&usr_login=&id=auoxxtvyquoy&fname=Star.Trek.Into.Darkness.2013.HD.m720p.LAT.avi&referer=&hash=1624-83-46-1377796398-8020e5629f50ff2d7b7de99b55bdb177&imhuman=Continue+to+Video
        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashvalue+"&imhuman="+submitbutton
        headers.append(["Referer",url])
        data = plugintools.read_body_and_headers(url, post=post, headers=headers )
        plugintools.log("data= "+data)
    except:
        pass
    
    # Extrae la URL
    plugintools.log("data= "+data)
    data = plugintools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    plugintools.log("data= "+data)
    from resources.tools.jsunpack import *
    data = unpack(data)
    plugintools.log("data= "+data)
    data = data.replace("\\","")

    media_url = plugintools.find_single_match(data,"file:'([^']+)'")
    video_urls = []
    video_urls.append( [ plugintools.get_filename_from_url(media_url)[-4:]+" [powvideo]",media_url])

    for video_url in video_urls:
        plugintools.log("[powvideo.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls



def catch_superweb(params):
    url = params.get("url")
    try:
        request_headers=[];y=[];
        body,response_headers=read_body_and_headers(url,headers=request_headers);
        url=[x[1] for x in response_headers if x[0]=='location'][0];
        if not url:
            print '********OK';
            pass
        else:
            try:
                body,response_headers=read_body_and_headers(url,headers=request_headers);
            except: pass
    except:
        pass

    try:
        r='\'file\':\s*\'(http:\/\/[\w\W]+?\.\w+)\'';q=plugintools.find_single_match(body,r);
    except:
        pass
    try:
        r='<iframe\ssrc=".*?flv=([^\&]+)';q=plugintools.find_single_match(body,r);
    except:
        pass
    try:
        r='<track\ssrc="([^"]+)';w=plugintools.find_single_match(body,r);
    except:
        w='';y.append(w);pass
    try:
        r='captions\.file\':\s*\'(http:\/\/[\w\W]+?\.\w+)\'';w=plugintools.find_single_match(body,r);y.append(w);
    except:
        w='';y.append(w);pass

    plugintools.play_resolved_url(q)


# Pendiente sustituir getUrl por una función análoga
def mailru(params):
    url = params.get("url")
    plugintools.log("[HarryTV.Mail.ru "+url)    

    url = url.replace('/my.mail.ru/video/', '/api.video.mail.ru/videos/embed/')
    url = url.replace('/videoapi.my.mail.ru/', '/api.video.mail.ru/')
    plugintools.log("URL = "+url)
    result = getUrl(url).result
    plugintools.log("result= "+result)    
    url = re.compile('metadataUrl":"(.+?)"').findall(result)[0]
    cookie = getUrl(url, output='cookie').result
    h = "|Cookie=%s" % urllib.quote(cookie)
    result = getUrl(url).result
    plugintools.log("result= "+result)
    #result = json.loads(result)
    result = data['videos']
    url = []
    url += [{'quality': '1080p', 'url': i['url'] + h} for i in result if i['key'] == '1080p']
    url += [{'quality': 'HD', 'url': i['url'] + h} for i in result if i['key'] == '720p']
    url += [{'quality': 'SD', 'url': i['url'] + h} for i in result if not (i['key'] == '1080p' or i ['key'] == '720p')]
    #if url == []: return
    plugintools.play_resolved_url(url)



class getUrl(object):
    def __init__(self, url, close=True, proxy=None, post=None, mobile=False, referer=None, cookie=None, output='', timeout='10'):
        if not proxy == None:
            proxy_handler = urllib2.ProxyHandler({'http':'%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if output == 'cookie' or not close == True:
            import cookielib
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post == None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url,None)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; CPU; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
        if not referer == None:
            request.add_header('Referer', referer)
        if not cookie == None:
            request.add_header('cookie', cookie)
        response = urllib2.urlopen(request, timeout=int(timeout))
        if output == 'cookie':
            result = str(response.headers.get('Set-Cookie'))
        elif output == 'geturl':
            result = response.geturl()
        else:
            result = response.read()
        if close == True:
            response.close()
        self.result = result

        def cloudflare(url):
            try:
                import urlparse,cookielib
                
                class NoRedirection(urllib2.HTTPErrorProcessor):
                    def http_response(self, request, response):
                        return response

                def parseJSString(s):
                    try:
                        offset=1 if s[0]=='+' else 0
                        val = int(eval(s.replace('!+[]','1').replace('!![]','1').replace('[]','0').replace('(','str(')[offset:]))
                        return val
                    except:
                        pass

                agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'
                cj = cookielib.CookieJar()
                opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
                opener.addheaders = [('User-Agent', agent)]
                response = opener.open(url)
                result = response.read()

                jschl = re.compile('name="jschl_vc" value="(.+?)"/>').findall(result)[0]

                init = re.compile('setTimeout\(function\(\){\s*.*?.*:(.*?)};').findall(result)[0]
                builder = re.compile(r"challenge-form\'\);\s*(.*)a.v").findall(result)[0]
                decryptVal = parseJSString(init)
                lines = builder.split(';')

                for line in lines:
                    if len(line)>0 and '=' in line:
                        sections=line.split('=')

                        line_val = parseJSString(sections[1])
                        decryptVal = int(eval(str(decryptVal)+sections[0][-1]+str(line_val)))

                answer = decryptVal + len(urlparse.urlparse(url).netloc)

                query = '%s/cdn-cgi/l/chk_jschl?jschl_vc=%s&jschl_answer=%s' % (url, jschl, answer)

                opener = urllib2.build_opener(NoRedirection, urllib2.HTTPCookieProcessor(cj))
                opener.addheaders = [('User-Agent', agent)]
                response = opener.open(query)
                cookie = str(response.headers.get('Set-Cookie'))
                response.close()

                return cookie
            except:
                return
            
        def jsunpack(script):
            def __itoa(num, radix):
                result = ""
                while num > 0:
                    result = "0123456789abcdefghijklmnopqrstuvwxyz"[num % radix] + result
                    num /= radix
                return result

            def __unpack(p, a, c, k, e, d):
                while (c > 1):
                    c = c -1
                    if (k[c]):
                        p = re.sub('\\b' + str(__itoa(c, a)) +'\\b', k[c], p)
                return p

            aSplit = script.split(";',")
            p = str(aSplit[0])
            aSplit = aSplit[1].split(",")
            a = int(aSplit[0])
            c = int(aSplit[1])
            k = aSplit[2].split(".")[0].replace("'", '').split('|')
            e = ''
            d = ''
            sUnpacked = str(__unpack(p, a, c, k, e, d))
            return sUnpacked.replace('\\', '')


def captcha(data):
    try:
        captcha = {}


        def get_response(response):
            try:
                dataPath = xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile"))
                i = os.path.join(dataPath.decode("utf-8"),'img')
                f = xbmcvfs.File(i, 'w')
                f.write(getUrl(response).result)
                f.close()
                f = xbmcgui.ControlImage(450,5,375,115, i)
                d = xbmcgui.WindowDialog()
                d.addControl(f)
                xbmcvfs.delete(i)
                d.show()
                xbmc.sleep(3000)
                t = 'Type the letters in the image'
                c = common.getUserInput(t, '')
                d.close()
                return c
            except:
                return

        solvemedia = common.parseDOM(data, "iframe", ret="src")
        solvemedia = [i for i in solvemedia if 'api.solvemedia.com' in i]

        if len(solvemedia) > 0:
            url = solvemedia[0]
            result = getUrl(url).result
            challenge = common.parseDOM(result, "input", ret="value", attrs = { "id": "adcopy_challenge" })[0]
            response = common.parseDOM(result, "iframe", ret="src")
            response += common.parseDOM(result, "img", ret="src")
            response = [i for i in response if '/papi/media' in i][0]
            response = 'http://api.solvemedia.com' + response
            response = get_response(response)
            captcha.update({'adcopy_challenge': challenge, 'adcopy_response': response})
            return captcha
        
        recaptcha = []
        if data.startswith('http://www.google.com'): recaptcha += [data]
        recaptcha += common.parseDOM(data, "script", ret="src", attrs = { "type": "text/javascript" })
        recaptcha = [i for i in recaptcha if 'http://www.google.com' in i]

        if len(recaptcha) > 0:
            url = recaptcha[0]
            result = getUrl(url).result
            challenge = re.compile("challenge\s+:\s+'(.+?)'").findall(result)[0]
            response = 'http://www.google.com/recaptcha/api/image?c=' + challenge
            response = get_response(response)
            captcha.update({'recaptcha_challenge_field': challenge, 'recaptcha_challenge': challenge, 'recaptcha_response_field': response, 'recaptcha_response': response})
            return captcha

        numeric = re.compile("left:(\d+)px;padding-top:\d+px;'>&#(.+?);<").findall(data)

        if len(numeric) > 0:
            result = sorted(numeric, key=lambda ltr: int(ltr[0]))
            response = ''.join(str(int(num[1])-48) for num in result)
            captcha.update({'code': response})
            return captcha

    except:
        return captcha
        
