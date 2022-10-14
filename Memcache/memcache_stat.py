import datetime

# The mem-cache should store its statistics every 5 seconds
                                   
"""/////////////////////////////STAT CLASS////////////////////////////////////"""
# use list
class Stats:
    """
    class for memcache statistics
    number of requests(for calling all 5 operations): reqServed_num
    miss = missing times on GET: missCount
    hit = hitting times on GET: hitCount
    hit rate = hit / hit+miss
    miss rate = miss / hit+miss
    """

    def __init__(self):

        self.reqServed_num = 0  # total request number to be added during run time
        self.missCount = 0
        self.hitCount = 0
        self.total_image_size = 0

        """////no out////"""
        self.listOfStat = []  # list of tuple in the format (miss or hit str, timestamp)
    
    
    def countStat(self):
        """
        Add states within 10 min in to a list
        """
        miss = 0
        hit = 0
        currentTime = datetime.datetime.now()
        #diffTime = currentTime - datetime.timedelta(minutes=10)  # 10 minutes before
        
        '''
        for index in range(len(self.listOfStat)):
            time = self.listOfStat[index][1]
            if time >= diffTime:  # why current time>=time wtf
                if self.listOfStat[index][0] == "miss":
                    miss += 1
                else:
                    hit += 1
            else:
                del self.listOfStat[index]
        '''

        self.missCount = miss
        self.hitCount = hit
