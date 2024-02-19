import ban_manager, server

if __name__ == '__main__':
    bm = ban_manager.BanDatabaseService()
    print(bm.all_bans())
    selectedServerHandler = server.SelectedServerHandler()
    serv = selectedServerHandler.fetch_from_server_list('nylex')

    bm.add_ban(ip='130.5.22.211', hwid=['hwid1', 'hwid2', 'hwid3'], steam64=76561199633576330, duration=0, reason='testing', server=serv)
    print(bm.all_bans())

    bm.fetch_bans_for_match(ip='130.5.22.211', steam64=76561199634446896, hwid=['hwid1', 'hwid2', 'hwid3'])