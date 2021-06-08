class PhsrOutput:
    """
    A class used to represent the list of lists containing the output of Phaser.
    """

    def __init__(self, Phaser_list):
        """ The constructor of the Phaser output list. To initialize, gets the list and sets each sublist to the
        right property. """
        self.__Phaser_List = Phaser_list
        self.__Morning_Volumes = self.__Phaser_List[1]
        self.__Regular_Arrows = self.__Phaser_List[2]
        self.__General_Information = self.__Phaser_List[3]
        self.__LRT_Information = self.__Phaser_List[4]
        self.__PublicTransport_Arrows = self.__Phaser_List[5]
        self.__Morning_VOC = self.__Phaser_List[6]
        self.__Morning_Total = self.__Phaser_List[7]
        self.__Morning_Determining_Volume = self.__Phaser_List[8]
        self.__Morning_Arrows_Table = list(self.__Phaser_List[8].keys())[:-6]
        self.__Morning_LRT = self.__Phaser_List[9]
        self.__Evening_Volumes = self.__Phaser_List[11]
        self.__Evening_VOC = self.__Phaser_List[16]
        self.__Evening_Total = self.__Phaser_List[17]
        self.__Evening_Determining_Volume = self.__Phaser_List[18]
        self.__Evening_Arrows_Table = list(self.__Phaser_List[18].keys())[:-6]
        self.__Evening_LRT = self.__Phaser_List[19]
        self.__Street_Names = self.__Phaser_List[20]
        self.__ID_Information = self.__Phaser_List[21]

    @property
    def PHSR_LIST(self):
        """Get the phaser list info"""
        return self.__Phaser_List

    @property
    def MOR_VOL(self):
        """Get the Morning Volumes info"""
        return self.__Morning_Volumes

    @property
    def ARROW_REG(self):
        """Get the Regular Arrows info"""
        return self.__Regular_Arrows

    @property
    def GEN_INFO(self):
        """Get the General Information info"""
        return self.__General_Information

    @property
    def LRT_INFO(self):
        """Get the LRT Information info"""
        return self.__LRT_Information

    @property
    def ARROW_PT(self):
        """Get the PublicTransport Arrows info"""
        return self.__PublicTransport_Arrows

    @property
    def MOR_VOC(self):
        """Get the Morning VOC info"""
        return self.__Morning_VOC

    @property
    def MOR_TOT(self):
        """Get the Morning Total info"""
        return self.__Morning_Total

    @property
    def MOR_DETER_VOL(self):
        """Get the Morning Determining Volume info"""
        return self.__Morning_Determining_Volume

    @property
    def MOR_ARROW_TABLE(self):
        """Get the Morning Arrows Table  info"""
        return self.__Morning_Arrows_Table

    @property
    def MOR_LRT(self):
        """Get the Morning LRT info"""
        return self.__Morning_LRT

    @property
    def EVE_VOL(self):
        """Get the Evening Volumes info"""
        return self.__Evening_Volumes

    @property
    def EVE_VOC(self):
        """Get the Evening VOC info"""
        return self.__Evening_VOC

    @property
    def EVE_TOT(self):
        """Get the Evening Total info"""
        return self.__Evening_Total

    @property
    def EVE_DETER_VOL(self):
        """Get the Evening Determining Volume info"""
        return self.__Evening_Determining_Volume

    @property
    def EVE_ARROW_TABLE(self):
        """Get the Evening Arrows Table info """
        return self.__Evening_Arrows_Table

    @property
    def EVE_LRT(self):
        """Get the Evening LRT info """
        return self.__Evening_LRT

    @property
    def STREETS(self):
        """Get the Street Names info """
        return self.__Street_Names

    @property
    def ID_INFO(self):
        """Get the  info"""
        return self.__ID_Information
