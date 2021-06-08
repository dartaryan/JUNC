class Lanes:
    """
      A class used to represent the lanes of the counter, divided to [regular, p_transport] for each lane.
    """

    def __init__(self):
        self._Separated_Right = [0, 0]
        self._Right_Left = [0, 0]
        self._All = [0, 0]
        self._Left = [0, 0]
        self._Through_Left = [0, 0]
        self._Through = [0, 0]
        self._Through_Right = [0, 0]
        self._Right = [0, 0]

    @property
    def SR(self):
        """Get the Separated_Right lanes"""
        return self._Separated_Right

    @SR.setter
    def SR(self, value):
        """Set the Separated_Right lanes"""
        self._Separated_Right = value

    @property
    def RL(self):
        """Get the Right_Left lanes"""
        return self._Right_Left

    @RL.setter
    def RL(self, value):
        """Set the Right_Left lanes"""
        self._Right_Left = value

    @property
    def A(self):
        """Get the All lanes"""
        return self._All

    @A.setter
    def A(self, value):
        """Set the All lanes"""
        self._All = value

    @property
    def L(self):
        """Get the left lanes"""
        return self._Left

    @L.setter
    def L(self, value):
        """Set the left lanes"""
        self._Left = value

    @property
    def TL(self):
        """Get the Through_left lanes"""
        return self._Through_Left

    @TL.setter
    def TL(self, value):
        """Set the Through_left lanes"""
        self._Through_Left = value

    @property
    def T(self):
        """Get the Through lanes"""
        return self._Through

    @T.setter
    def T(self, value):
        """Set the Through lanes"""
        self._Through = value

    @property
    def TR(self):
        """Get the Through_Right lanes"""
        return self._Through_Right

    @TR.setter
    def TR(self, value):
        """Set the Through_Right lanes"""
        self._Through_Right = value

    @property
    def R(self):
        """Get the Right lanes"""
        return self._Right

    @R.setter
    def R(self, value):
        """Set the Right lanes"""
        self._Right = value

    def Empty_lanes(self):
        """The method returns if True if the lanes == 0, and False if has lanes"""
        lanes = [self.SR, self.RL, self.A, self.L, self.TL, self.T, self.TR, self.R]
        sum_lanes = [sum(lane) for lane in lanes]
        return sum(sum_lanes) == 0

    def Organize_arrows_order(self):
        """The method organizes the logical order of the arrows (left to right) and adds an arrow type to indicate
        whether the color of the arrow. The method takes care of complex arrows: arrows that contain 2 types,
        meaning - regular and PT. """
        match_arrow_type = {0: "White", 1: "Yellow"}
        complex_arrows = {"D": 1, "A": 2, "W": 3, "S": 4}
        complex_arrows_full = {12: [['U', 1, 'White'], ['F', 1, 'Yellow']],
                               13: [['U', 1, 'Yellow'], ['F', 1, 'White']],
                               23: [['N', 1, 'White'], ['U', 1, 'Yellow']],
                               24: [['N', 1, 'Yellow'], ['U', 1, 'White']],
                               32: [['B', 1, 'White'], ['F', 1, 'Yellow']],
                               33: [['N', 1, 'White'], ['U', 1, 'Yellow'], ['F', 1, 'White']],
                               34: [['N', 1, 'Yellow'], ['H', 1, 'White']],
                               35: [['N', 1, 'White'], ['H', 1, 'Yellow']],
                               36: [['N', 1, 'Yellow'], ['U', 1, 'White'], ['F', 1, 'Yellow']],
                               37: [['B', 1, 'Yellow'], ['F', 1, 'White']],
                               42: [['J', 1, 'White'], ['K', 1, 'Yellow']],
                               43: [['J', 1, 'Yellow'], ['K', 1, 'White']]
                               }
        arranged_arrows = []
        lane_arrows = [["L", self.L], ["A", self.TL], ["T", self.T], ["W", self.A], ["S", self.RL], ["D", self.TR],
                       ["R", self.R], ["E", self.SR]]
        for arrow in lane_arrows:
            if arrow[0] in complex_arrows.keys() and arrow[1][1] > 1:
                complex_arrow_symbol = complex_arrows[arrow[0]] * 10 + arrow[1][1]
                build_arrow = complex_arrows_full[complex_arrow_symbol]
                for arr in build_arrow:
                    arranged_arrows.append(arr)
            else:
                for arrow_type in range(len(arrow[1])):
                    arranged_arrows.append([arrow[0], arrow[1][arrow_type], match_arrow_type[arrow_type]])
        return arranged_arrows
