"""
    Playlist gen
"""
import json
#from time import sleep

import spotify_wrapper
import setlist_fm_wrapper


def prompt_choice(max_val):
    """
    Prompts a user to choose an input displayed in the terminal
    """
    choice = 0
    while choice not in range(1, max_val+1):
        try:
            choice = int(input(f"Please enter candidate choice (1 - {max_val}): "))
            if choice not in range(1, max_val+1):
                print("Please enter a number within the range")
        except ValueError:
            print("Please enter an integer")
    return choice

def main():
    """
        main for making playlists
    """
    # Open config file to grab api tokens and initialize our wrappers
    conf = open("config.json", mode="r")

    data = json.load(conf)

    setlist_key = data["setlist"]["api_key"]
    spotify_id = data["spotify"]["client_id"]
    spotify_secret = data["spotify"]["client_secret"]

    conf.close()

    # Initialize setlist object
    fm_caller = setlist_fm_wrapper
    setlist = fm_caller.SetlistFmWrapper(setlist_key)

    # Initialize Spotify object
    print("Generating access token for Spotify... ")

    spot = spotify_wrapper
    spotify = spot.SpotifyWrapper(spotify_id, spotify_secret)
    token_generated = spotify.gen_auth_token()

    # Ensure we got a token
    if not token_generated:
        raise Exception("Could not get an access token for Spotify." +
                        "Please make sure your client id and client " +
                        "secret are correct.")

    print("Done.")

    make_playlist = "y"
    while make_playlist == "y":
        # Now let's start by determining our setlist
        # Prompt for artist
        artist_name = ""

        while artist_name == "":
            artist_name = input("Enter the name of the artist: ")

            found = setlist.get_artist_by_name(artist_name)

            # No matches
            if not found:
                print("Could not find the artist. Make sure spelling is correct")
                artist_name = ""
            elif setlist.get_artist_name() == "":
                # Multiple candidates
                print(f"There are several matches for {artist_name}. " +
                      "Please choose which one is correct.")
                artist_matches = setlist.get_num_candidates()

                # Prompt for choice
                setlist.print_candidates()
                artist_choice = prompt_choice(artist_matches)

                # Pick our artist
                setlist.pick_artist(artist_choice)
            else:
                print(f"Found setlists for {artist_name}")

        # prompt for new song versions
        new_version_choice = ""
        while new_version_choice != "y" and new_version_choice != "n":
            new_version_choice = input("Would you prefer the newer versions of songs (y/n): ")\
                                 .strip()[0]

        spotify.set_version_choice(new_version_choice == "y")

        # Search for setlists
        setlist_count = 0
        choice_available = False
        # For limiting setlist totals
        city_name = ""
        state_name = ""
        state_abbr = ""
        tour_name = ""
        venue_name = ""
        year = ""

        while setlist_count < 1 or not choice_available:
            # Prompt for other limiters
            year = input("Enter the year of the show (recommended): ").strip()
            city_name = input("Enter the name of the city " +
                              "(press Enter to skip): ").strip()
            state_name = input("Enter the name of the state " +
                               "(press Enter to skip): ").strip()
            state_abbr = input("Enter the two-letter state abbreviation " +
                               "(press Enter to skip): ").strip()
            tour_name = input("Enter the name of the tour " +
                              "(press Enter to skip): ").strip()
            venue_name = input("Enter the name of the venue " +
                               "(press Enter to skip): ").strip()

            # Gather setlists
            print(f"Searching for setlists for {artist_name}... ", end="")
            setlist.get_all_setlists(artist_name, "", city_name,
                                     state_name, state_abbr, tour_name,
                                     venue_name, year)
            print("Done")

            # Narrow setlist choice
            setlist_count = setlist.get_num_setlists()


            print("Possible sets to choose from: " + f"{setlist_count}")
            setlist.print_setlists_sparse()

            while not choice_available:
                try:
                    choice = input("Is your show listed? y/n: ").strip().lower()[0]
                    if choice == "y":
                        choice_available = True
                        # Pick set
                        set_choice = prompt_choice(setlist_count)
                        setlist.pick_setlist(set_choice)
                except IndexError:
                    print("Please enter a yes or no response")

        # Show set
        # print("Set found. Printing setlist...")
        setlist.print_setlist()

        # Create playlist and populate it
        song_list = setlist.get_setlist_songs()
        print("Finding songs...")
        missing = spotify.find_songs(artist_name, song_list)

        if missing > 0:
            print(f"Could not find matches for {missing} songs. " +
                  "They may not be on Spotify or may be covers.")

        spotify.create_playlist(setlist.setlist_name_to_string(),
                                setlist.setlist_info_to_string())

        make_playlist = input("Would you like to make another playlist (y/n): ").strip()[0]

if __name__ == "__main__":
    main()
