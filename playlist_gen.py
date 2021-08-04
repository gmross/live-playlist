import spotify_wrapper
import setlist_fm_wrapper

import json
from time import sleep

def main():
    # Open config file to grab api tokens and initialize our 
    conf = open("config.json", mode="r")

    data = json.load(conf)

    setlist_key = data["setlist"]["api_key"]
    spotify_id = data["spotify"]["client_id"]
    spotify_secret = data["spotify"]["client_secret"]

    conf.close()

    # Initialize setlist object
    fm = setlist_fm_wrapper
    setlist = fm.SetlistFmWrapper(setlist_key)

    # Initialize Spotify object
    print("Generating access token for Spotify... "),

    spot = spotify_wrapper
    spotify = spot.SpotifyWrapper(spotify_id, spotify_secret)
    token_generated = spotify.gen_auth_token()

    # Ensure we got a token
    if not token_generated:
        raise Exception("Could not get an access token for Spotify." +
                        "Please make sure your client id and client " + 
                        "secret are correct.")

    print("Done.")

    # Now let's start by determining our setlist
    #print("TODO")
    
    # Searching for bands with similar names
    """
    artist = "Chunk! No, Captain Chunk!"
    setlist.get_artist_by_name(artist)
    if(setlist.artist == ""):
        print("There are multiple artists with a matching name. Please choose one:")
        setlist.print_candidates()
        setlist.pick_artist(1)
    else:
        print("Artist is: " + setlist.artist)
    print(setlist.artist)
    """
    # Searching for setlists by artist name
    artist2 = "August Burns Red"
    '''
    setlist.get_setlists_by_artist_name(artist2)
    print("Possible sets to choose from: " + f"{len(setlist.possible_sets)}")
    setlist.print_setlists_sparse()
    setlist.pick_setlist(6)
    setlist.print_setlist_info(setlist.setlist)
    '''
    
    setlist.get_artist_by_name(artist2)
    if(setlist.artist == ""):
        print("There are multiple artists with a matching name. Please choose one:")
        setlist.print_candidates()
        setlist.pick_artist(1)
    else:
        print(f"Found {setlist.artist}. Searching for sets...")
    #print(setlist.artist)

    # Getting all sets
    sleep(1)
    setlist.get_all_setlists(artist2, "", "", "", "", "", "", "2019")
    setlist.print_setlists_sparse()
    setlist.pick_setlist(73)
    setlist.print_setlist_info(setlist.setlist)
    
    
    song = "Legend of Zelda"

    # Search for a song
    result = spotify.find_song(song, artist2)
    #print(result)

    # Search for all songs in a setlist
    songs = setlist.get_setlist_songs()
    #print(songs)
    result = spotify.find_songs(artist2, songs)
    if result > 0:
        print(f"Couldn't find matches for {result} songs. " + 
            "They may be covers or may not be on Spotify")
    '''
    spotify.create_playlist(f'test {artist2}', 'test descr')
    '''
    spotify.create_playlist(f"{setlist.print_set_name()}", 
                            f"{setlist.print_set_info()}")
    

if __name__ == "__main__":
    main()
