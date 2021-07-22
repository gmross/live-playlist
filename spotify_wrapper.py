import requests
import base64
import datetime


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

    # for checking expiration

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


def main():
    print("The Spotify API class is not meant to be called on its own.")
    print("Please call the playlist_gen.py file instead, or " +
          "refer to the documentation if you need more help.")


if __name__ == "__main__":
    main()
