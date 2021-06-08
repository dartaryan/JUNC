class Phases:
    """
      A class used to represent the directions for each direction in the phase
    """

    def __init__(self):
        self.__north_direction = []
        self.__south_direction = []
        self.__east_direction = []
        self.__west_direction = []
        self.__deter_volume = 0

    @property
    def NO(self):
        """Get the north direction arrows"""
        return self.__north_direction

    @NO.setter
    def NO(self, value):
        """Set the north direction arrows"""
        self.__north_direction = value

    @property
    def SO(self):
        """Get the south direction arrows"""
        return self.__south_direction

    @SO.setter
    def SO(self, value):
        """Set the south direction arrows"""
        self.__south_direction = value

    @property
    def EA(self):
        """Get the east direction arrows"""
        return self.__east_direction

    @EA.setter
    def EA(self, value):
        """Set the east direction arrows"""
        self.__east_direction = value

    @property
    def WE(self):
        """Get the west direction arrows"""
        return self.__west_direction

    @WE.setter
    def WE(self, value):
        """Set the west direction arrows"""
        self.__west_direction = value

    @property
    def VOL(self):
        """Get the determining volume of the phase"""
        return self.__deter_volume

    @VOL.setter
    def VOL(self, value):
        """Set the determining volume of the phase"""
        self.__deter_volume = round(value, 0)

    def split_direction(self, img_output):
        """The method receives string in the format DIRECTION_ARROWS (for example, Str -> direction:South,
        Arrows: through right) and divides it to each direction. """
        if img_output[0] == "N":
            self.NO.append(img_output[1:])
        if img_output[0] == "S":
            self.SO.append(img_output[1:])
        if img_output[0] == "E":
            self.EA.append(img_output[1:])
        if img_output[0] == "W":
            self.WE.append(img_output[1:])

    @staticmethod
    def organize_arrows_order_for_table(diagram_arrows, table_time_img):
        """The method organizes the logical order of the arrows (left to right) and adds an arrow type to indicate
        whether the color of the arrow. The method takes care of complex arrows: arrows that contain 2 types,
        meaning - regular and PT. """
        original_directions_list = [diagram_arrows.NO.LAN, diagram_arrows.SO.LAN, diagram_arrows.EA.LAN,
                                    diagram_arrows.WE.LAN]
        directions_from_phases = [table_time_img.NO, table_time_img.SO, table_time_img.EA, table_time_img.WE]
        i_to_direction = {0: "NO", 1: "SO", 2: "EA", 3: "WE"}
        match_arrow_type = {0: "White", 1: "Yellow"}
        complex_arrows = {"rt": 1, "tl": 2, "rtl": 3, "rl": 4}
        complex_arrows_full = {12: [['U', 1, 'White'], ['F', 1, 'Yellow']],
                               13: [['U', 1, 'Yellow'], ['F', 1, 'White']],
                               23: [['N', 1, 'White'], ['U', 1, 'Yellow']],
                               24: [['N', 1, 'Yellow'], ['U', 1, 'White']],
                               32: [['B', 1, 'White'], ['F', 1, 'Yellow']],
                               33: [['N', 1, 'White'], ['U', 1, 'Yellow'], ['F', 1, 'White']],
                               34: [['N', 1, 'Yellow'], ['H', 1, 'White']],
                               35: [['N', 1, 'White'], ['H', 1, 'Yellow']],
                               36: [['N', 1, 'Yellow'], ['U', 1, 'White'], ['F', 1, 'Yellow', ]],
                               37: [['B', 1, 'Yellow'], ['F', 1, 'White']],
                               42: [['J', 1, 'White'], ['K', 1, 'Yellow']],
                               43: [['J', 1, 'Yellow'], ['K', 1, 'White']]
                               }
        match_arrows_for_string = {"l": "L", "tl": "A", "t": "T", "rtl": "W", "rl": "S", "rt": "D", "r": "R", "e": "E"}
        i = 0
        while i < 4:
            rearranged_arrows = []
            final_arrows = []
            lane_arrows = [["l", original_directions_list[i].L], ["tl", original_directions_list[i].TL],
                           ["t", original_directions_list[i].T],
                           ["rtl", original_directions_list[i].A], ["rl", original_directions_list[i].RL],
                           ["rt", original_directions_list[i].TR],
                           ["r", original_directions_list[i].R], ["e", original_directions_list[i].SR]]
            curr_direction_from_phase = directions_from_phases[i]
            arrows_order = ["l", "tl", "t", "rtl", "rl", "rt", "r", "e"]
            arrange_arrows = [[], [], [], [], [], [], [], []]
            for org_arrow in curr_direction_from_phase:
                arrange_arrows[arrows_order.index(org_arrow)].append(org_arrow)
            for reset_arrow in arrange_arrows:
                for ar in reset_arrow:
                    if ar:
                        rearranged_arrows.append(ar)
            for list_curr_direc in rearranged_arrows:
                for arrow in lane_arrows:
                    if arrow[0] == list_curr_direc and arrow[0] in complex_arrows.keys() and int(arrow[1][1]) > 1:
                        complex_arrow_symbol = complex_arrows[arrow[0]] * 10 + int(arrow[1][1])
                        build_arrow = complex_arrows_full[complex_arrow_symbol]
                        for arr in build_arrow:
                            final_arrows.append(arr)

                    elif arrow[0] == list_curr_direc:
                        for arrow_type in range(len(arrow[1])):
                            if int(arrow[1][arrow_type]) > 0:
                                final_arrows.append([match_arrows_for_string[arrow[0]], arrow[1][arrow_type],
                                                     match_arrow_type[arrow_type]])

            setattr(table_time_img, i_to_direction[i], final_arrows)
            i += 1
        return
