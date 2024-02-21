class PartOfFile:
    def __init__(self, total_part, order, data, client, room, file_name, client_name = ""):
        self.total_part = total_part
        self.order = order
        self.data = data
        self.client = client
        self.room = room
        self.file_name = file_name
        self.client_name = client_name