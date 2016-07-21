#!/usr/bin/env python

"""
    Music downloader for the website https://www.song365mp3.info/
"""

import signal, time, os, sys, requests, re, argparse
from bs4 import BeautifulSoup

verbose = False
automate = False
noconfirm = False
prefix_url = "https://www.song365mp3.info"

def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if raw_input("\nReally quit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here    
    signal.signal(signal.SIGINT, exit_gracefully)

def vprint(arg):
    global verbose
    if verbose:
        for i in arg:
            print i

def get_dl_url(furl):
    r1 = requests.get(furl)
    s1 = BeautifulSoup(r1.text, 'html.parser')
    js = s1.find_all('script')[7]
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

    dpath = []

    t = url.split('/')[3]
    if t == 'album':
        raw_songs_list = s.find_all('div', {'class' : ['song-name', 'buttons'] })

        vprint(["Parsing directory paths..."])

        artist_name = s.find('em' , {'class' : 'profile-item-value'}).text.strip().title()
        album_name = s.find('div', {'class' : 'page'}).h1.text.strip().title()
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
   
        handle_album(songs_dict, dpath)

    elif t == 'track':
        artist_name = s.find('div', {'id' : 'title'}).span.text.strip().title()
        dpath = [artist_name]
        song_name = s.find('div', {'id' : 'title'}).text.split('-')[0].strip().title()
        furl = prefix_url + s.find('a', {'class' : 'right'})['href']
        handle_track(dpath, furl, song_name)

def handle_album(songs_dict, dpath):
    dl_dict = fetch_download_dict(songs_dict)    

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
            print "Downloading Complete"

def handle_track(dpath, furl, song_name):
    songs_dict = {1 : [song_name, furl]}
    handle_album(songs_dict, dpath)

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
        dl_list = display_songs(songs_dict)
    else:
        dl_list = select_songs(songs_dict)

    vprint(["Download list received from user", "Creating dictionary of songs to download..."])

    dl_dict = {}
    #dictionary of songs with the download links
    for i in dl_list:
        title = songs_dict[i][0]
        furl = songs_dict[i][1]
        vprint(["Fetching download url for the song: " + title + " from url: " + furl])
        dl_url = get_dl_url(furl)
        dl_dict.update({i : [title, dl_url]})
    
    return dl_dict

def select_songs(songs_dict):

    user_response = 'n'
    while user_response.strip() is not 'y':
        dl_list = display_songs(songs_dict)    
        print "Are you sure you are done with your songs' choice and you want to go ahead and download them?"
        user_response = raw_input("y/n/c(to cancel): ")
        if user_response.strip() == 'c':
            print "Downloading canceled"
            sys.exit()
        while user_response.strip() is not 'y' and user_response.strip() is not 'n':
            print "Please enter a corect response!!"
            user_response = raw_input("y/n/c(to cancel): ")
            if user_response.strip() == 'c':
                print "Downloading canceled"
                sys.exit()
    return dl_list            

def display_songs(songs_dict):
    #print songs_dict
    for key in songs_dict:
        print str(key) + ": " + songs_dict[key][0]
    print ""    
    
    user_input = raw_input()
    if user_input.strip() == 'all':
        dl_list = [s for s in songs_dict]
    else:
        dl_list = [int(s) for s in user_input.split(',') if s.strip().isdigit()]
    
    dl_list = list(set(dl_list))

    print "\nYou have selected following songs:"
    for i in dl_list:
        if i in songs_dict:
            print str(i) + ': ' + songs_dict[i][0]
        else:
            dl_list.remove(i)
    if len(dl_list) == 0:
        print "Oops!! Looks like you either entered wrong song nos or none at all."

    return dl_list

def open_file(song_file):
    while True:
        try:
            f = open(song_file, 'wb')
        except IOError as e:
            print e.errno
            old_song_file = song_file
            print "Invalid song name: " + song_file + "."
            song_file = raw_input("Please provide a valid name along with the absolute path as present in the invalid name: ")
            print "Changing file name from " + old_song_file + " to " + song_file 
        else:
            return f

def download_song(song_file, url):

    f = open_file(song_file)

    print "Downloading " + song_file + "..."
    data = requests.get(url, stream = True)
    for chunk in data.iter_content(chunk_size=1024*1024):
        if chunk:
            print "len: " + str((len(chunk))/(1024*1024)) + "MB"
            f.write(chunk)
    f.close()
    return data        



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
    parser.add_argument("-v", "--verbose", help = "increase output verbosity", action = "store_true")
    parser.add_argument("-n", "--noconfirm", help = "do not ask for confirmation", action = "store_true")
    parser.add_argument("-a", "--all", help = "download everything", action = "store_true")
    parser.add_argument("music_url", help = "Bandcamp Song URL")
    args = parser.parse_args()
    verbose = bool(args.verbose)
    noconfirm = bool(args.noconfirm)
    automate = bool(args.all)
    parse_url(args.music_url)