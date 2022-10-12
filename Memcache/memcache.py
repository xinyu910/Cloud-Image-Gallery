class EachStat:
    """
    Class for each single state
    includes a time stamp and an action
    """
    def __init__(self):
        pass

class Stats:
    """
    class for memcache statistics
    should be store in
    number of items in cache, total size of items in cache,
    number of requests served, miss rate and hit rate
    """
    def __init__(self):
        self.statList = []
        self.totalSize = 0
        self.reqServed_num = 0

    def StatList(self):
        """
        Add states within 10 min in to a list
        """

    def Rate_Calc(self):
        """
        calculate hit and miss rate with the statlist
        """
