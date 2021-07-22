# Live Playlist

<!-- ![Header image of project](images/test_header.jpg) -->

This is a script written in Python3 that grabs concert setlists for a specified
band and creates a Spotify playlist for the given concert.

## How It Works

For security reasons, we store our API keys for this project in a `config.json`
file. If you want to run this project on your local machine, you need a free
API token from setlistFM as well as a free API token from Spotify.

Create a `config.json` file and format it as follows:

```json
{
  "setlist": {
    "api_key": "your-setlist-fm-api-key"
  },
  "spotify": {
    "client_id": "your-spotify-client-id",
    "client_secret": "your-spotify-client-secret"
  }
}
```

Next we... _todo--need basic functionality first_

## Todo List

- [ ] Grab API tokens for Spotify and Setlist.fm
- [ ] Write function to grab setlist for an artist with either the date of the
      show or the tour
- [ ] Write function to find matches on Spotify or skip the track if it is
      unavailable
- [ ] Make playlist with given account and return link to playlist
