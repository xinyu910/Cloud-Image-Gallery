import datetime

# The mem-cache should store its statistics every 5 seconds
                                   
"""/////////////////////////////STAT CLASS////////////////////////////////////"""
# use list
class Stats:
    """
    class for memcache statistics
    number of requests(for calling all 5 operations)
    miss = missing times on GET
    hit = hitting times on GET
    hit rate = hit / hit+miss
    miss rate = miss / hit+miss
    """

    def __init__(self):

        self.reqServed_num = 0  # total request number to be added during run time
        self.miss = 0
        self.hit = 0

        """////no out////"""
        self.listOfStat = []  # stats to be appended during run time
        self.listOfTime = []  # time stamp to be appended during run time

    def countStat(self):
        """
        Add states within 10 min in to a list
        """
        miss = 0
        hit = 0
        currentTime = datetime.datetime.now()
        diffTime = currentTime - datetime.timedelta(minutes=10)  # 1 minutes before

        for index in range(len(self.listOfTime)):
            time = self.listOfTime[index]
            if currentTime >= time >= diffTime:  # why current time>=time wtf
                print(index)
                if self.listOfStat[index] == "miss":
                    print("a miss")
                    miss += 1
                else:
                    print("a hit")
                    hit += 1

        self.miss = miss
        self.hit = hit
