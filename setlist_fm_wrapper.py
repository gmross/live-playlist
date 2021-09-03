import requests
import json
from requests.exceptions import HTTPError
from time import sleep


class SetlistFmWrapper:
    """
    A class to handle API requests to setlist.fm

    Attributes
    ----------
    api_key: str
        Your personal API key to access the setlist.fm API
    api_base_url: str
        the base url for accessing the setlist.fm API
    artist: str
        the name of the artist we chose a set for
    possible_artists: list
        a list of artists matching the name criteria if we have multiple options
    possible_sets: list
        a list of potential sets for a given query to limit the number of 
        requests that we send
    set_name: str
        the name of the tour for the set
    set_date: str
        the date the setlist was played
    set_venue: str
        the venue where the set was played
    set_loc: str
        the location of the venue
    setlist: list
        the songs played in the set
    """
    api_key = None
    api_base_url = "https://api.setlist.fm/rest"
    artist = ""             # store artists and setlists to reduce api calls
    artist_info = {}
    possible_artists = []
    possible_sets = []
    set_name = ""
    set_date = ""
    set_venue = ""
    set_loc = ""
    tour = ""
    setlist = []

    def __init__(self, api_key):
        self.api_key = api_key

    def get_header(self):
        """ 
        Returns the request header
        """
        return {
            "x-api-key": f"{self.api_key}",
            "Accept": "application/json"
        }

    def get_params_artist_name(self, name):
        """ 
        Creates the request body to search for an artist by name
        """
        return f"artistName={name}&sort=relevance"
        # Outdated--ignore
        # return {
        #     "artistName": f"{name}",
        #     "sort": "relevance"
        # }

    def get_artist_endpoint(self):
        """
        Returns the url to search an artist by name
        """
        return f"{self.api_base_url}/1.0/search/artists"

    def get_artist_by_name(self, name):
        """
        Searches for the artist using their name

        Params
        ------
        name: str
            The artist's name for which we are searching
        """
        try:
            response = requests.get(f"{self.get_artist_endpoint()}" + "?" +
                                    f"{self.get_params_artist_name(name)}",
                                    headers=self.get_header())

            # Ensure we succeed
            response.raise_for_status()
        except HTTPError as http_err:
            print(f"HTTP Error occurred: {http_err}")
            return False
        except Exception as err:
            print(f"Other error occurred: {err}")
            return False

        # parse response
        resp = response.json()

        # Make candidates
        for art in resp["artist"]:
            # Ignore "features" to cut down on duplicates
            if "feat." not in art["name"]:
                self.possible_artists.append(art)

        if len(self.possible_artists) == 1:
            self.artist_info = {self.possible_artists[0]["name"]:
                                self.possible_artists[0]["mbid"]}
            self.artist = self.possible_artists[0]["name"]
        else:
            self.artist_info = {"artist_name": "artist_id"}

        return True

    def get_artist_name(self):
        """
        Returns the name of the artist
        """
        return self.artist
    
    def get_num_candidates(self):
        """
        Returns the number of artists that match a given name
        """
        return len(self.possible_artists)

    def print_candidates(self):
        """
        Print the artists returned by our search for an artist's name
        Artists will be marked by their name and any distinction provided by the API
        """
        current = 1

        for art in self.possible_artists:
            name = art["name"]
            if "disambiguation" in art and art["disambiguation"] != "":
                dis = "(" + art["disambiguation"] + ")"
            else:
                dis = ""
            print(f"   {current}: {name} {dis}")
            current = current + 1

    def pick_artist(self, num):
        """
        Sets our artist to one of the candidates we found when searching for them
        Potential candidates are only those in potential_artists

        Params
        ------
        num: int
            index of the artist we want to settle on
        """
        self.artist = self.possible_artists[num - 1]["name"]
        self.artist_info = {
            "name": self.possible_artists[num - 1]["name"],
            "mbid": self.possible_artists[num - 1]["mbid"]
        }

    def get_setlist_endpoint(self):
        """
        Returns the API endpoint to search for a setlist
        """
        return f"{self.api_base_url}/1.0/search/setlists"

    def print_setlist_info(self, artist_set):
        # Essential info
        artist = artist_set["artist"]["name"]
        set_date = artist_set["eventDate"]
        # Account for missing venues
        if artist_set["venue"]["name"] != "":
            set_venue = artist_set["venue"]["name"]
        else:
            set_venue = "Unknown Venue"
        # See if we have a tour name
        if "tour" in artist_set:
            tour_name = artist_set["tour"]["name"]
        else:
            tour_name = "Unknown tour"

        # Define location based on country to avoid wordiness
        if artist_set["venue"]["city"]["name"] != "":
            set_loc = artist_set["venue"]["city"]["name"] + ", "
        else:
            set_loc = "Unknown City, "
        
        if artist_set["venue"]["city"]["country"]["code"] == "US":
            set_loc = set_loc + artist_set["venue"]["city"]["state"]
        else:
            set_loc = set_loc + artist_set["venue"]["city"]["country"]["name"]

        print("Setlist for " + f"{artist} on {tour_name}")
        print(f"Set played at {set_venue} in {set_loc} on {set_date}")

        # Need to iterate over our setlist to account for encores
        number = 1
        for set_portion in artist_set["sets"]["set"]:
            setlist = set_portion["song"]
            for song in setlist:
                song_name = song["name"]
                print(f"   {number : >2}: {song_name}")
                number = number + 1
    
    def print_setlists_sparse(self):
        """
        Prints just the barebones info on our setlist candidates to narrow candidates
        We only worry about tour, artist, location, venue, and date
        """
        num = 1   # For indexing options to let user choose
        last_tour = ""
        
        artist = self.possible_sets[0]["artist"]["name"]
        print(f"Matching setlists available for {artist}:")
        for setlist in self.possible_sets:
            # Basic info
            set_date = setlist["eventDate"]
            if setlist["venue"]["name"] != "":
                set_venue = setlist["venue"]["name"]
            else:
                set_venue = "Unknown Venue"
            # See if we have a tour name
            if "tour" in setlist:
                tour_name = setlist["tour"]["name"]
            else:
                tour_name = "Unknown tour"
            
            # Define location based on country to avoid wordiness
            if setlist["venue"]["city"]["name"] != "":
                set_loc = setlist["venue"]["city"]["name"] + ", "
            else:
                set_loc = "Unknown City, "
            # print(set["venue"])
            if setlist["venue"]["city"]["country"]["code"] == "US":
                set_loc = set_loc + setlist["venue"]["city"]["state"]
            else:
                set_loc = set_loc + setlist["venue"]["city"]["country"]["name"]
            
            # For empty venue/location info
            if set_venue == "":
                set_venue = "Unknown Venue"
            if set_loc == "":
                set_loc = "Unknown City"
            
            if last_tour != tour_name:
                print(f" On {tour_name}")
                last_tour = tour_name
            print(f" {num : >3}: " + f"{set_venue} in {set_loc} on {set_date}")
            
            num = num + 1
    
    def get_setlists_by_artist_name(self, artist_name):
        """
        Gets all setlists for artists that match the given artist name

        Params
        ------
        artistName: str
            The artists name for which we are searching
        """
        url = f"{self.get_setlist_endpoint()}" + "?" + f"artistName={artist_name}&p=1"
        headers = self.get_header()

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Validate response went through
        except HTTPError as err:
            print(f"HTTP Error occurred: {err}")
            return False
        except Exception as err:
            print(f"Other error occurred: {err}")
            return False

        # print(response)
        res = response.json()
        test_candidates = {"artist_name": "artist_id"}  # dummy entry for debugging purposes

        for setlist in res["setlist"]:
            # Avoid empty setlists so we can  filter artists with no concerts
            if setlist["sets"]["set"]:
                # Temporary status to store artist name, artist id
                test_candidates[setlist["artist"]["name"]] = setlist["artist"]["mbid"]
                #self.print_setlist_info(setlist)  # Debugging print statement
                self.possible_sets.append(setlist)

        # print(test_candidates)

        return True
    
    def get_num_setlists(self):
        """
        Returns the number of setlists to choose from
        """
        return len(self.possible_sets)

    def get_setlist(self):
        """
        Returns the setlist
        """
        return self.setlist
        
    def pick_setlist(self, num):
        """
        Picks the user defined setlist from our setlists we found in our search

        Params
        ------
        num: int
            The 1-indexed choice of setlist provided 
            where 1 <= num <= |possible_setlists|
        """
        self.setlist = self.possible_sets[num - 1]
        # Set details for printing later
        if self.setlist["venue"]["name"] != "":
            self.set_venue = self.setlist["venue"]["name"]
        else:
            self.set_venue = "Unknown Venue"
        self.set_date = self.setlist["eventDate"]
        # Account for missing locations and different countries
        if self.setlist["venue"]["city"]["name"] != "":
            self.set_loc = self.setlist["venue"]["city"]["name"] + ", "
        else:
            self.set_loc = "Unknown City, "
        if self.setlist["venue"]["city"]["country"]["code"] == "US":
            self.set_loc = self.set_loc + self.setlist["venue"]["city"]["state"]
        else:
            self.set_loc = self.set_loc + self.setlist["venue"]["city"]["country"]["name"]
        # See if we have a tour name
        if "tour" in self.setlist:
            self.tour = self.setlist["tour"]["name"]
        else:
            self.tour = ""
    
    
    def get_setlist_page(self, artist_name, artist_id, city, state_name, 
                         state_abbr, tour_name, venue_name, year, page_num):
        """
        Grab a given page of 20 sets (including empty sets) for an artist
        """
        # Build our url based on what parameters we're given
        url = f"{self.get_setlist_endpoint()}" + "?" + f"artistName={artist_name}"#"&year=2019&p={page_num}"
        if city:
            url = url + f"&cityName={city}"
        if state_name:
            url = url + f"&state={state_name}"
        if state_abbr:
            url = url + f"&stateCode={state_abbr}"
        if tour_name:
            url = url + f"&tourName={tour_name}"
        if venue_name:
            url = url + f"&venueName={venue_name}"
        if year:
            url = url + f"&year={year}"
        url = url + f"&p={page_num}"
        headers = self.get_header()

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Validate response went through
        except HTTPError as err:
            print(f"HTTP Error occurred: {err}")
            return 0
        except Exception as err:
            print(f"Other error occurred: {err}")
            return 0

        # print(response)
        res = response.json()
        test_candidates = {"artist_name": "artist_id"}  # dummy entry for debugging purposes

        for setlist in res["setlist"]:
            # Avoid empty setlists so we can  filter artists with no concerts
            if setlist["sets"]["set"]:
                # Temporary status to store artist name, artist id
                test_candidates[setlist["artist"]["name"]] = setlist["artist"]["mbid"]
                #self.print_setlist_info(setlist)  # Debugging print statement
                self.possible_sets.append(setlist)
        # print(test_candidates)
        return res["total"]
    
    def get_all_setlists(self, artist_name, artist_id, city, state_name, 
                         state_abbr, tour_name, venue_name, year):
        """
        Sends requests to get all possible tours for an artist

        Params
        ------
        artist_name: str
            The name of the artist
            REQUIRED
        city: str
            The name of the city
            optional
        state_name: str
            The name of the state
            optional
        state_abbr: str
            The two-letter abbreviation of the state's name
            optional
        tour_name: str
            The name of the tour
            optional
        venue_name: str
            The name of the venue
            optional
        year: str
            The year of the show
            optional 
        """

        # TODO: Iterate over all pages and sleep between requests

        total = self.get_setlist_page(artist_name, artist_id, city, state_name, 
                                      state_abbr, tour_name, venue_name, year, 1)
        print(f"Total number of matching setlists: {total}")

        tally = 20
        nextPage = 2

        while tally < total:
            # We need to sleep between API calls so we do not exceed limit
            sleep(0.5)
            print(f"Grabbing page {nextPage}...")
            self.get_setlist_page(artist_name, artist_id, city, state_name, 
                                  state_abbr, tour_name, venue_name, year, 
                                  nextPage)
            #increment
            tally = tally + 20
            nextPage = nextPage + 1
        
        print(f"Total number of retrieved candidates: {len(self.possible_sets)}")
    
    def get_setlist_songs(self):
        """
        Gets all song names from a set
        """
        songs = []

        for portion in self.setlist["sets"]["set"]:
            for song in portion["song"]:
                songs.append(song["name"])
        
        return songs
    
    def setlist_name_to_string(self):
        """
        Returns a string formatted to represent a playlist title
        """
        return f"{self.artist} Live @ {self.set_venue}"
    
    def print_setlist(self):
        """
        Prints the setlist we picked
        """
        self.print_setlist_info(self.setlist)
    
    def setlist_info_to_string(self):
        """
        Returns a string that describes the setlist information
        """
        desc = f"Setlist for {self.artist}"
        if self.tour != "":
            desc = desc + f" on {self.tour}. "
        else:
            desc = desc + ". "
        desc = desc + f"They played at {self.set_venue} in {self.set_loc}. Performed on {self.set_date}."
        return desc


def main():
    print("The Setlist.fm API class is not meant to be called on its own.")
    print("Please call the playlist_gen.py file instead, or ")
    print("refer to the documentation if you need more help.")


if __name__ == "__main__":
    main()
