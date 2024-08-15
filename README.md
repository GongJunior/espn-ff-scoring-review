# espn fantasy player data
## what
trying to get all espn stats to test scoring changes

## stats endpoint
https://lm-api-reads.fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leagues/655727?scoringPeriodId=0&view=kona_player_info

## notes
- all players file: 2023allplayers.json
- $resp = & '.\req.ps1'

## how
- find endpoint in network after going to https://fantasy.espn.com/football/players/add?leagueId=xxxxxxx
    - logged into league
    - Players > Add Players
    - Change filters to all
- from endpoint, copy as powershell and save as req.ps1
    - in "x-fantasy-filter" header, change limit to values higher than max players or however many you want
        - >"limit":2550
    - subseqent requests, you'll only need to change the $session info
- run app.py
    - may need to remove old csvs for fresh data
    - may need to setup env