import datetime
#The mem-cache should store its statistics every 5 seconds
global eachState
global cacheTotalState

class SingleStat:
    """
    Class for each single state
    includes a time stamp and an action
    """

    def __init__(self):
        self.type = "" #    hit or miss
        self.time = "" #    timestemp
        

class Stats:
    """
    class for memcache statistics
    number of requests(for calling all 5 operations)
    miss = missing times on GET
    hit = hitting times on GET
    hit rate = hit / hit+miss
    miss rante = miss / hit+miss
    """
    def __init__(self):
        self.statList = [] # list of SignleState
        self.totalSize = 0
        self.reqServed_num = 0
    

    def AddList(self, oneState):
        self.statList.append(oneState)


    def StatList(self):
        """
        Add states within 10 min in to a list
        """
        currentTime = datetime.datetime.now()
        diffTime = currentTime - datetime.timedelta(minutes=10)  # 10 minutes

        for stat in self.list:
            if currentTime >= stat.timestamp and diffTime <= stat.timestamp:
                if stat.action == "miss":
                    miss = miss+1
                    total = total + 1
                if stat.action == "hit":
                    hit = hit+1
                    total = total + 1


    def Rate_Calc(self):
        """
        calculate hit and miss rate with the statlist
        """

eachState = SingleStat()
cacheTotalState = Stats()
 