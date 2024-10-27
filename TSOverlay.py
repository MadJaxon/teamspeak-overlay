import json

from TSOverlayUI import TSOverlayUI
from wrapper.TSApiWrapper import TSApiWrapper
from wrapper.TSChannel import TSChannel
from wrapper.TSClient import TSClient
from wrapper.TSConnection import TSConnection


class TSOverlay:
    ui: TSOverlayUI
    connections = []
    channels = []
    clients = []
    def start(self, ui):
        self.ui: TSOverlayUI = ui
        connection = TSApiWrapper(None)
        connection.on("apiReady", self.apiReady)
        connection.on("apiError", self.apiError)
        connection.on("apiConnectionOpen", self.apiConnectionOpen)
        connection.on("clientPropertiesUpdated", self.clientPropertiesUpdated)
        connection.on("clientSelfPropertyUpdated", self.clientSelfPropertyUpdated)
        connection.on("clientChannelGroupChanged", self.clientChannelGroupChanged)
        connection.on("talkStatusChanged", self.talkStatusChanged)
        connection.on("clientMoved", self.clientMoved)
        connection.on("textMessage", self.textMessage)
        connection.connect()
        connection.run_forever()

    def findClient(self, connectionId, clientId):
        for client in self.clients:
            if client.clientId == clientId and client.connectionId == connectionId:
                return client
        return None

    def findChannel(self, channelId):
        for channel in self.channels:
            if channel.channelId == channel:
                return channel
        return None

    def parseChannelProperties(self, connectionId, channelId, properties):
        channel = self.findChannel(channelId)
        isNew = False
        if not channel:
            channel = TSChannel()
            channel.channelId = channelId
            channel.connectionId = connectionId
            isNew = True
        channel.name = properties["name"]
        if isNew:
            self.channels.append(channel)
        # print(json.dumps(self.channels, default=lambda o: o.__dict__))

    def parseClientProperties(self, clientId, properties, connectionId):
        client = self.findClient(connectionId, clientId)
        isNew = False
        if not client:
            if not ("nickname" in properties):
                return
            client = TSClient()
            client.clientId = clientId
            client.connectionId = connectionId
            isNew = True
        if "nickname" in properties:
            client.name = properties["nickname"]

        if "isMuted" in properties:
            client.muted = properties["isMuted"]
        if "inputMuted" in properties:
            client.muted = properties["inputMuted"] or (("isMuted" in properties) and properties["isMuted"])

        if "flagTalking" in properties:
            client.talking = properties["flagTalking"]
        if "inputMuted" in properties:
            client.talking = properties["flagTalking"] or (("isTalker" in properties) and properties["isTalker"])

        # todo: whispering
        # if "nickname" in properties:
        # client.whispering = properties["flagTalking"]

        if "isChannelCommander" in properties:
            client.commander = properties["isChannelCommander"]

        if "away" in properties:
            client.away = properties["away"]

        if "channelGroupInheritedChannelId" in properties:
            client.channelId = properties["channelGroupInheritedChannelId"]


        if isNew:
            self.clients.append(client)
        # print(json.dumps(self.clients, default=lambda o: o.__dict__))

    def apiError(self, payload):
        if payload['socketEvent'].args[0].find("dictionary changed size during iteration") == -1:
            print("apiError")
            print(payload)
        if payload['socketEvent'].args[0].find("KeyboardInterrupt") == -1:
            exit()
        if payload['socketEvent'].args[0].find("main thread is not in main loop") == -1:
            exit()
        pass
    def apiReady(self, payload):
        print("apiReady")
        # print(payload)
        for connectionInfo in payload['connections']:
            connection = TSConnection()
            connection.connectionId = connectionInfo['id']
            connection.name = connectionInfo['properties']['name']
            connection.clientId = connectionInfo['clientId']
            self.connections.append(connection)

            rootChannels = []
            subChannels = []
            if isinstance(connectionInfo['channelInfos']['rootChannels'], dict):
                rootChannels = list(connectionInfo['channelInfos']['rootChannels'].values())
            else:
                rootChannels = connectionInfo['channelInfos']['rootChannels']
            if isinstance(connectionInfo['channelInfos']['subChannels'], dict):
                subChannels = list(connectionInfo['channelInfos']['subChannels'].values())
            else:
                subChannels = connectionInfo['channelInfos']['subChannels']
            subChannels = self.flatten_list(subChannels)
            # for channelInfo in (rootChannels + subChannels):
            #     self.parseChannelProperties(channelInfo['id'], connectionInfo['id'], channelInfo['properties'])
            for channelInfo in rootChannels:
                self.parseChannelProperties(channelInfo['id'], connectionInfo['id'], channelInfo['properties'])
            for channelInfo in subChannels:
                self.parseChannelProperties(channelInfo['id'], connectionInfo['id'], channelInfo['properties'])
            # for channelInfo in connectionInfo['channelInfos']['subChannels']:
            #     self.parseChannelProperties(channelInfo['id'], connectionInfo['id'], channelInfo['properties'])
            # for channelInfo in (connectionInfo['channelInfos']['rootChannels'] + connectionInfo['channelInfos']['subChannels']):
            #     self.parseChannelProperties(channelInfo['id'], connectionInfo['id'], channelInfo['properties'])

            for clientInfo in connectionInfo['clientInfos']:
                self.parseClientProperties(clientInfo['id'], clientInfo['properties'], connectionInfo['id'])
        #print(payload)
        self.updatedClients()
        pass

    def flatten_list(self, nested_list):
        result = []
        for item in nested_list:
            if isinstance(item, list):
                # Recursively flatten the sublist
                result.extend(self.flatten_list(item))
            elif isinstance(item, dict):
                # If the item is a dict, add it to the result directly
                result.append(item)
        return result

    def apiConnectionOpen(self, payload):
        pass

    def clientSelfPropertyUpdated(self, payload):
        pass

    def clientPropertiesUpdated(self, payload):
        self.parseClientProperties(payload["clientId"], payload["properties"], payload["connectionId"])
        pass

    def clientChannelGroupChanged(self, payload):
        pass

    def talkStatusChanged(self, payload):
        client = self.findClient(payload["connectionId"], payload["clientId"])
        if client:
            # print("talkStatusChanged")
            # print(payload)
            client.talking = payload["status"] == 1
            if client.talking:
                client.whispering = payload["isWhisper"]
            pass
        self.updatedClients()

    def updatedClients(self):
        # print(json.dumps(self.clients, default=lambda o: o.__dict__))
        # print("#################################")
        talkingConnections = []
        for connection in self.connections:
            print("########## " + connection.name + " #############")
            talkingClients = []
            for client in self.clients:
                if client.connectionId == connection.connectionId:
                    # if client.muted:
                    #     talkingClients.append(client)
                    if client.talking:
                        self.ui.add_client(client)
                        talkingClients.append(client)
                        if client.whispering:
                            print(client.name + " is WHISPERING")
                        else:
                            print(client.name + " is talking")
                    else:
                        self.ui.remove_client(client)
            if len(talkingClients) > 0:
                talkingConnections.append({
                    "server": connection.name,
                    "connectionid": connection.connectionId,
                    "clients": talkingClients
                })
        # self.ui.update_status(talkingConnections)
        if len(talkingConnections) == 0:    #cleanup leftovers
            self.ui.clear_clients()


    def clientMoved(self, payload):
        pass

    def textMessage(self, payload):
        pass