class Event:
    def __init__(self):
        self.name = "Default Name"
        self.host = "No host found"
        self.desc = "No description found"
        self.startDate = None
        self.endDate = None
        self.location = "No location found"

    def prettyPrint(self):
        print("Name: ", str(self.name))
        print("Host: ", str(self.host))
        print("Desc: ", str(self.desc))
        print("Start Date: ", str(self.startDate))
        print("End Date: ", str(self.endDate))
        print("Location: ", str(self.location))


