class Routes:
    """
      A class used to represent the counting of a route with right, left and through
    """

    def __init__(self, left=0, right=0, through=0):
        self.__left = left
        self.__right = right
        self.__through = through

    @property
    def L(self):
        """Get the left count"""
        return self.__left

    @L.setter
    def L(self, value):
        """Set the left count"""
        self.__left = value

    @property
    def R(self):
        """Get the right count"""
        return self.__right

    @R.setter
    def R(self, value):
        """Set the right count"""
        self.__right = value

    @property
    def T(self):
        """Get the through count"""
        return self.__through

    @T.setter
    def T(self, value):
        """Set the through count"""
        self.__through = value

    def Empty_routes(self):
        """The method returns if True if the routes (volumes) == 0, and False if has volumes"""
        all_routes = [self.L, self.T, self.R]
        return sum(all_routes) == 0
