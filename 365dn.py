#!/usr/bin/env python

"""
    Music downloader for the website https://www.song365mp3.info/
"""

from main import *

verbose = False
verbose2 = False
automate = False
noconfirm = False
prefix_url = "https://www.song365mp3.org"

def vprint(arg):
    global verbose
    if verbose:
        for i in arg:
            print i

def vvprint(arg):
    global verbose2
    if verbose2:
        for i in arg:
            print i

def get_dl_url(furl):
    r1 = requests.get(furl)
    s1 = BeautifulSoup(r1.text, 'html.parser')
    try:
        js = s1.find_all('script')[7]
    except:
        print "Error: ", r1.content
        return ""
    pattern = re.compile(ur'hqurl = \'.*\'')
    dl_url = pattern.findall(unicode(js))[0].split('=')[1].strip()
    dl_url = dl_url[1:][:-1]
    return dl_url

def parse_url(url):

    print """\n\nWarning!!! Either input a list of comma separated song nos
           to download particular songs or \"all\" to download the
           complete album. For example to download song nos 1, 2
           and 4, input 1, 2, 4"""
    print "Please adhere to the input format, otherwise the downloader won't behave as expected!!!\n\n"

    vprint(["Fetching data from the url provided..."])

    r = requests.get(url)

    vprint(["Data fetching complete", "Parsing data..."])

    s = BeautifulSoup(r.text, 'html.parser')

    t = url.split('/')[3]

    if t == 'album':
        vprint(["in album"])
        songs_dict, dpath = parse_album(s)
        handle_album(songs_dict, dpath)

    elif t == 'track':
        vprint(["in track"])
        dpath, furl, song_name = parse_track(s)
        handle_track(dpath, furl, song_name)

    elif t == 'artist' and url.split('/')[4] == 'albums':
        vprint(["in artist"])
        album_list = parse_artist(s)
        handle_artist(album_list)

    else:
        print "Unrecognised type of url"

def parse_track(s):
    artist_name = s.find('div', {'id' : 'title'}).span.text.strip().title()
    dpath = [artist_name]
    song_name = s.find('div', {'id' : 'title'}).text.split('-')[0].strip().title()
    furl = prefix_url + s.find('a', {'class' : 'right'})['href']
    return (dpath, furl, song_name)

def parse_artist(s):
    global prefix_url, verbose
    vprint(["Parsing albums list..."])
    #dictionary of album_name:album_url
    dic = {i.text: prefix_url + i.a['href'] for i in s.find_all('em', {'class':'album-name'})}
    vprint(["Albums list parsed", "Creating artist's list..."])
    album_list = []
    temp = verbose
    verbose = verbose2
    for album in dic:
        r = requests.get(dic[album])
        s = BeautifulSoup(r.text, 'html.parser')
        songs_dict, dpath = parse_album(s)
        if len(songs_dict) is not 0:
            album_list.append((album, songs_dict, dpath))

    verbose = temp
    vprint(["Artist's list created"])
    return album_list

def parse_album(s):
    global prefix_path
    raw_songs_list = s.find_all('div', {'class' : ['song-name', 'buttons'] })
    album_name = s.find('div', {'class' : 'page'}).h1.text.strip().title()

    vprint(["Processing album: " + album_name, "Parsing directory paths..."])

    artist_name = s.find('em' , {'class' : 'profile-item-value'}).text.strip().title()
    dpath = [artist_name, album_name]

    vprint(["Parsing Complete"])

    vprint(["Creating songs dictionary..."])

    i = 0
    songs_dict = {}
    while i < len(raw_songs_list):
        song_name = raw_songs_list[i].text
        dl_link = prefix_url + raw_songs_list[i + 1].find('a', {'class' : 'download'})['href']
        songs_dict.update({i/2 : [song_name, dl_link]})
        i += 2

    vprint(["Songs dictionary created"])
    return (songs_dict, dpath)

def handle_track(dpath, furl, song_name):
    songs_dict = {1 : [song_name, furl]}
    handle_album(songs_dict, dpath)

def handle_artist(album_list):
    dl_list = []
    for i in album_list:
        print "\nAlbum: " + i[0]
        dl_dict = fetch_download_dict(i[1])
        if len(dl_dict) is not 0:
            dl_list.append([i[0], dl_dict, i[2]])
    if len(dl_list) == 0:
        print "No songs to be downloaded"
    else:
	print "List of the songs about to be downloaded:"
        for i in album_list:
            print "\n\tAlbum Name: " + i[0] 
            for j in i[1]:
                print "\t\tSong Name: " + i[1][j][0]

    for i in dl_list:
        print "Downloading album: " + i[0]
        handle_album(i[1], i[2], fetched = 1)
        print "Download complete"

def handle_album(songs_dict, dpath, fetched = 0, dl_dict = {}):
    if fetched == 0:
        dl_dict = fetch_download_dict(songs_dict)    
    elif fetched == 1:
        dl_dict = songs_dict

    if len(dl_dict) == 0:
        print "No songs selected"
    else:
        print "Creating the directory structure... "
        dirpath = "."
        for i in dpath:
            dirpath = dirpath + '/' + str(i)

        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

        for i in dl_dict:
            print "Downloading " + str(i) + ': ' + dl_dict[i][0] + "... "
            download_song(dirpath + '/' + dl_dict[i][0] + '.mp3', dl_dict[i][1])

def fetch_download_dict(songs_dict):
    global automate, noconfirm

    vprint(["Get the list of songs to download from user..."])

    if automate:
        dl_list = [s for s in songs_dict]
        print "List of songs to be downloaded:"
        for i in dl_list:
            if i in songs_dict:
                print str(i) + ': ' + songs_dict[i][0]
    elif noconfirm:
        print 'here in noconfirm'
        dl_list = display_songs(songs_dict)
    else:
        dl_list = select_songs(songs_dict)

    vprint(["Download list received from user", "Creating dictionary of songs to download..."])

    dl_dict = {}
    #dictionary of songs with the download links
    for i in dl_list:
        title = songs_dict[i][0].replace('/', '-')
        furl = songs_dict[i][1]
        vvprint(["Fetching download url for the song: " + title + " from url: " + furl])
        dl_url = get_dl_url(furl)
        dl_dict.update({i : [title, dl_url]})
    
    return dl_dict

#first download:https://www.song365mp3.info/album/omnia-alive-131442.html

if __name__ == "__main__":
    if (int(requests.__version__[0]) == 0):
        print ("Your version of requests needs updating\nTry: '(sudo) pip install -U requests'")
        sys.exit()

    # store the original SIGINT handler
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)

    #argument parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help = "increase output verbosity to level 1", action = "store_true")
    parser.add_argument("-vv", "--verbose2", help = "increase output verbosity to level 2", action = "store_true")
    parser.add_argument("-n", "--noconfirm", help = "do not ask for confirmation", action = "store_true")
    parser.add_argument("-a", "--all", help = "download everything", action = "store_true")
    parser.add_argument("music_url", help = "Bandcamp Song URL")
    args = parser.parse_args()
    verbose = bool(args.verbose)
    verbose2 = bool(args.verbose2)
    if verbose2:
        verbose = True
    noconfirm = bool(args.noconfirm)
    automate = bool(args.all)
    parse_url(args.music_url)
