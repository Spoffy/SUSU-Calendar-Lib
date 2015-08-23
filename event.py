class Event:
    def __init__(self):
        self.name = "Default Name"
        self.host = "No host found"
        self.desc = "No description found"
        self.start_date = None
        self.end_date = None
        self.location = "No location found"

    def pretty_print(self):
        print("Name: ", str(self.name))
        print("Host: ", str(self.host))
        print("Desc: ", str(self.desc))
        print("Start Date: ", str(self.start_date))
        print("End Date: ", str(self.end_date))
        print("Location: ", str(self.location))


