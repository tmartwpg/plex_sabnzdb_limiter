# Welcome to # plex_sabnzdb_limiter!

This will limit the speed for SABnzdb when there's remote Plex streams.
The program will grab the current max line speed from SABnzdb and the remote streams from Tautulli (PlexPy).
It will then adjust SABnzdb to allow enough bandwidth for the current streams. 


# Usage
```$ python3 main.py -h
usage: 
main.py [-h] \
	--tautulli_url TAUTULLI_URL \
	--sabnzdb_url SABNZDB_URL
	--tautulli_api_key TAUTULLI_API_KEY \
	--sabnzdb_api_key SABNZDB_API_KEY
	[--leave_unused_line_speed LEAVE_UNUSED_LINE_SPEED] \
	[--debug] \
	[--dry_run]
