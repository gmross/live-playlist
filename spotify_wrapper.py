import requests
import base64
import datetime
import json


class SpotifyWrapper(object):
    """
    A class to handle all Spotify API requests for our playlist generation

    Attributes
    ----------
    access_token: str
        a base64 encoded byte string used to access the Spotify API
        as per the Spotify Developer Guide, the access_token is a base64
        encoded concatenation of the client_id and client_secret in the format
        base64<client_id:client_secret>
    access_token_expiration: datetime
        a datetime object representing the time at which our access token 
        expires
    access_token_is_expired: bool
        a boolean to keep track of if we have an expired access token and need 
        to re-authenticate
    client_id: str
        a string containing the id given to a Spotify application
    client_secret: str
        a string containing the client secret given to the Spotify application
    token_url: str
        the base url for submitting api requests for an auth token
    """

    # Member variables we need to send requests
    access_token = None
    access_token_expiration = datetime.datetime.now()
    access_token_is_expired = True
    client_id = None
    client_secret = None
    # for getting auth token
    token_url = "https://accounts.spotify.com/api/token"

    # for keeping track of songs
    song_ids = []

    # for keeping track of playlist
    playlist_id = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_creds(self):
        """
        Returns the base64 encoded client Auth header
        """
        client_id = self.client_id
        client_secret = self.client_secret

        # Ensure we have valid client id and secret before encoding
        if client_id is None or client_secret is None:
            raise Exception("You need a client id and a client secret to initiate API requests")

        # Spotify Developer API for client credentials flow should encode the 
        # client id and secret in the following format 
        # Authorization: Basic <base64 encoded client_id:client_secret>
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())

        return client_creds_b64.decode()

    def get_token_header(self):
        """
        Returns the request header for client credentials workflow
        """
        return {
            "Authorization": f"Basic {self.get_client_creds()}"
        }

    def get_token_params(self):
        """
        Returns the request body for client credentials workflow
        """
        return {
            "grant_type": "client_credentials"
        }

    def gen_access_token(self):
        """
        Generates an oauth token that lasts an hour so we can make our requests
        """
        req = requests.post(self.token_url, data=self.get_token_params(), 
                            headers=self.get_token_header())

        # Check we got a valid response
        if req.status_code in range(200, 299):
            token_response = req.json()
            # Figure out expiration time
            now = datetime.datetime.now()
            expires_time = token_response['expires_in']  # expiration time in seconds
            expiration = now + datetime.timedelta(seconds=expires_time)
            self.access_token_expiration = expiration
            self.access_token_is_expired = False
            # Update access token
            self.access_token = token_response['access_token']

            return True

        return False
    
    def get_search_header(self):
        """
        Returns the header field for search endpoints
        """
        return {
            "Authorization": f"Bearer {self.access_token}"
        }
    
    def get_search_params(self, song_name, artist_name):
        """
        Returns the search body for a song name and artist name

        Params
        ------
        song_name: str
            The name of the song
        artist_name: str
            The name of the artist
        """
        return {
            "q": f"{song_name} {artist_name}",
            "type": "track,artist"
        }
    
    def find_song(self, song_name, artist_name):
        """
        Searches for a specified song in the spotify API

        Params
        ------
        song_name: str
            The name of the song
        artist_name: str
            The name of the artist
        """
        if self.access_token_is_expired:
            self.gen_access_token()
        
        search_url = "https://api.spotify.com/v1/search"
        response = requests.get(url=search_url, 
                           params=self.get_search_params(song_name, artist_name), 
                           headers=self.get_search_header())
        
        # Validate response
        status = response.status_code
        if status not in range(200, 299):
            print(f"Error {status}. Search for {song_name} by {artist_name} " 
                    + "unsuccessful.")
            return False
        
        # Pull needed data from response
        res = response.json()

        if res["tracks"]["total"] < 1:
            print(f"No result found for {song_name}")
            return False

        # Just get first match for now
        for track in res["tracks"]["items"]:
            '''Debugging info
            print(f"{track['name']} by {track['artists'][0]['name']} on " + 
                  f"{track['album']['name']}", end=" ")
            '''
            print(f"Grabbing data for {song_name} by {artist_name}")
            uri = res["tracks"]["items"][0]["uri"]
            self.song_ids.append(uri)
            return True

        print(f"Could not find {song_name} by {artist_name}.") 
        print("It may be missing from Spotify")
        return False

    def find_songs(self, artist_name, song_list):
        """
        Searches for all given songs and retrieves data we need for making a playlist

        Params
        ------
        artist_name: str
            The name of the artist
        song_list: list
            A list of the songs we are searching for
        """
        missing = 0
        for song in song_list:
            result = self.find_song(song, artist_name)
            if not result:
                missing = missing + 1
        
        return missing
    
    def get_user_headers(self):
        """
        Returns the properly formatted header for getting user info
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_user_id(self):
        """
        Gets the users id
        """
        me_url = "https://api.spotify.com/v1/me"
        response = requests.get(url=me_url, headers=self.get_user_headers())

        status = response.status_code
        if status not in range(200, 299):
            print(f"{status} Trouble finding user. Make sure you've added an access token.")
            return ""
        
        res = response.json()

        return res["id"]

    def get_creation_body(self, name, desc):
        return {
            "name": f"{name}",
            "description": f"{desc}",
            "public": "false"
        }
    
    def get_creation_header(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_playlist(self, name, desc, user_id):
        """
        Creates a new playlist on Spotify

        Params
        ------
        name: str
            The name for the playlist
        desc: str
            The description for the playlist
        """
        create_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

        response = requests.post(url=create_url, 
                                 data=self.get_creation_body(name, desc), 
                                 headers=self.get_creation_header())
        
        # Validate
        status = response.status_code
        if status not in range(200, 299):
            print("Could not make playlist")
            return False
        
        res = response.json()
        self.playlist_id = res["id"]

        return True




def main():
    print("The Spotify API class is not meant to be called on its own.")
    print("Please call the playlist_gen.py file instead, or " +
          "refer to the documentation if you need more help.")


if __name__ == "__main__":
    main()
