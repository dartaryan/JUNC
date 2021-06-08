from Routes import *
from Lanes import *


class Direction:
    """
      A class used to represent a direction containing it's counts and lanes
      The counts (volumes) are divided to two different properties: Morning_route and Evening_route.

    """

    def __init__(self, name):
        """ The constructor of the Direction class,called when a new instance of a class is created.assigns values
        into the instance.
        :param name: Represents the name of the Direction (street / way)
        :type name : str
        :return: none
         """

        self.__Morning_route = Routes()  # A property representing the volumes for the morning rush hour
        self.__Evening_route = Routes()  # A property representing the volumes for the evening rush hour
        self.__All_lanes = Lanes()  # A property representing the lanes for the specific direction
        self.__Name = name  # A property representing the name or the way

    @property
    def MOR(self):
        """Get the morning info"""
        return self.__Morning_route

    @MOR.setter
    def MOR(self, value):
        """Set the morning info"""
        self.__Morning_route = value

    @property
    def EVE(self):
        """Get the evening info"""
        return self.__Evening_route

    @EVE.setter
    def EVE(self, value):
        """Set the evening info"""
        self.__Evening_route = value

    @property
    def LAN(self):
        """Get the lanes info"""
        return self.__All_lanes

    @LAN.setter
    def LAN(self, value):
        """Set the lanes info"""
        self.__All_lanes = value

    @property
    def NAME(self):
        """Get the name of the direction"""
        return self.__Name

    @NAME.setter
    def NAME(self, value):
        """Set the name of the direction"""
        self.__Name = value

    def empty_direction(self):
        """The method checks whether a direction is empty (has no volumes AND lanes);
          It returns 0 if the direction is empty, and 1 if the direction is not empty"""
        if self.LAN.Empty_lanes() is False or self.MOR.Empty_routes() is False or self.EVE.Empty_routes() is False:
            return 1
        else:
            return 0
