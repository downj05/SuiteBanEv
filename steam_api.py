from steamwebapi.api import ISteamUser, IPlayerService, ISteamUserStats
import a2s
import json
import random

# TODO : Add steam api support
steamuserinfo = ISteamUser(steam_api_key='None')

def steamid3_to_steam64(steamid3):
	universe = 1  # The default universe for most Steam accounts
	account_id = int(steamid3.split(":")[2])  # Extract the account ID from the SteamID3 string
	steam64 = (account_id + 76561197960265728) | (universe << 56)  # Construct the 64-bit SteamID
	return steam64

def get_user_info(steam64id):
	user_summary = steamuserinfo.get_player_summaries(steam64id)
	if len(user_summary['response']['players']) < 1:
		# Fallback to trying custom URL
		print("[get_user_info() from steam_api] Invalid Steam64 detected, falling back to custom URL")
		steam64id = steamuserinfo.resolve_vanity_url(steam64id)['response']['steamid']
		print(f"[get_user_info() from steam_api] Custom URL fallback successful, got {steam64id}")
		return get_user_info(steam64id=steam64id)
	return user_summary['response']['players'][0]


if __name__ == '__main__':
	print(get_user_info(76561199204905808))