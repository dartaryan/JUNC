import codecs
import json
import time
from datetime import datetime

from Diagram import Diagram
from VOLCOV import VolCov


class Jucson:
    def __init__(self, output_diagram, jucson_object=""):
        self.__output_diagram = output_diagram
        self.__jucson_obj = jucson_object
        self.__Project_name = ""
        self.__Project_number = ""
        self.__Author = ""
        self.__Date_time = str(time.strftime("%d/%m/%Y   %H:%M"))
        self.__Counter = 0
        self.__More_info = ""
        self.__Street_names = ""
        self.__output_jucson = {}

    @property
    def OUTJUNC(self):
        """Get the output junc object"""
        return self.__output_diagram

    @OUTJUNC.setter
    def OUTJUNC(self, diagram):
        """Set the output junc object"""
        self.__output_diagram = diagram

    @property
    def JUCSON(self):
        """Get the jucson object"""
        return self.__jucson_obj

    @JUCSON.setter
    def JUCSON(self, jucson_obj):
        """Set the jucson object"""
        self.__jucson_obj = jucson_obj

    @property
    def OUTJUCSON(self):
        """Get the jucson object"""
        return self.__output_jucson

    @OUTJUCSON.setter
    def OUTJUCSON(self, out_jucson_obj):
        """Set the jucson object"""
        self.__output_jucson = out_jucson_obj

    @property
    def PROJ_NAME(self):
        """Get the name of the project"""
        return self.__Project_name

    @PROJ_NAME.setter
    def PROJ_NAME(self, name):
        """Set the name of the project"""
        self.__Project_name = name

    @property
    def PROJ_NUM(self):
        """Get the project number"""
        return self.__Project_number

    @PROJ_NUM.setter
    def PROJ_NUM(self, number):
        """Set the project number"""
        self.__Project_number = number

    @property
    def AUTHOR(self):
        """Get the name of the author, based on the info written in office"""
        return self.__Author

    @AUTHOR.setter
    def AUTHOR(self, author):
        """Set the name of the author | DO NOT USE UNLESS NEEDED!"""
        self.__Author = author

    @property
    def DATETIME(self):
        """Get the time of the created JUNC"""
        return self.__Date_time

    @DATETIME.setter
    def DATETIME(self, datetime):
        """Set the time of the created JUNC | DO NOT USE UNLESS NEEDED!"""
        self.__Date_time = datetime

    @property
    def COUNT(self):
        """Get the number of tries or versions for this JUNC"""
        return self.__Counter

    @COUNT.setter
    def COUNT(self, count):
        """Set  the number of tries or versions for this JUNC"""
        self.__Counter = count

    @property
    def INFO(self):
        """Get the additional info about the JUNC"""
        return self.__More_info

    @INFO.setter
    def INFO(self, info):
        """Set the additional info about the JUNC"""
        self.__More_info = info

    @property
    def STREETS(self):
        """Get the names of the streets for this JUNC"""
        return self.__Street_names

    @STREETS.setter
    def STREETS(self, streets):
        """Set the names of the streets for this JUNC | DO NOT USE UNLESS NEEDED!"""
        self.__Street_names = streets

    def loadJucson(self, file_directory):
        # f = open(file_directory, )
        # self.JUCSON = json.load(f)
        # with codecs.open(file_directory, encoding='utf-8') as f:
        #     self.JUCSON = json.loads(f)

        with open(file_directory, encoding='utf-8') as fh:
            self.JUCSON = json.load(fh)

    def saveJucsonFromDiagram(self, directory=""):
        self.pull_vol()
        self.pull_id_info()
        self.pull_street_names()
        self.pull_arr()
        self.pull_general_info()
        self.pull_lrt_info()
        dateTimeObj = datetime.now()
        time_stamp = str(dateTimeObj.strftime("%d-%m-%Y_%H-%M"))
        location = directory + "\×JUCSON×" + time_stamp + ".json"
        with codecs.open(location, 'wb', encoding='utf-8') as f:
            json.dump(self.OUTJUCSON, f, ensure_ascii=False)

    def loadJucsonToDiagram(self):
        self.push_id_info()
        self.push_arr()
        self.push_vol()
        self.push_general_info()
        self.push_lrt_info()
        self.push_street_names()

    # #{'Morning_Volumes': [0, 1515, 560, 820, 594, 0, 685, 0, 76, 0, 0, 0], 'Regular_Arrows': [0, 0, 1, 0, 1, 0, 0,
    # 9, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'General_Information': [1800, 0, 1, 1, 0, 3, 3,
    # 0, 0, 0, 1], 'LRT_Information': [0, 120, 25, 4, 1, 0], 'PublicTransport_Arrows': [0, 0, 1, 0, 0, 0, 0, 0, 0, 1,
    # 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 'Evening_Volumes': [0, 1749, 615, 743, 774, 0, 312, 0,
    # 110, 0, 0, 0], 'Street_Names': ['משה דיין', 'משה דיין', 'שמשון', 0], 'ID_Information': [0, 0, 0, 0, 0],
    # 'VC_Author': 'Ben Akiva'}

    def push_id_info(self):
        """the method uses the output section info of Phaser and the excel properties of the volume_calculator to
        push it into the right property of the class. """
        self.PROJ_NAME = self.JUCSON["ID_Information"][0]
        self.PROJ_NUM = self.JUCSON["ID_Information"][1]
        self.COUNT = self.JUCSON["ID_Information"][3]
        self.INFO = self.JUCSON["ID_Information"][4]
        self.AUTHOR = self.JUCSON["VC_Author"]
        streets = str(self.OUTJUNC.WE.NAME) + " · " + str(self.OUTJUNC.EA.NAME) + " · " + str(
            self.OUTJUNC.SO.NAME) + " · " + str(
            self.OUTJUNC.NO.NAME)
        self.STREETS = streets

    def pull_id_info(self):
        self.OUTJUCSON["ID_Information"] = ["", "", "", "", ""]
        self.OUTJUCSON["ID_Information"][0] = self.PROJ_NAME
        self.OUTJUCSON["ID_Information"][1] = self.PROJ_NUM
        self.OUTJUCSON["ID_Information"][3] = self.COUNT
        self.OUTJUCSON["ID_Information"][4] = self.INFO
        self.OUTJUCSON["VC_Author"] = self.AUTHOR

    def push_arr(self):
        """the method uses the output arrows of Phaser to push them into the right subclass of each direction,
        divided to regular arrows and public transport arrows. """
        arr_list = [self.JUCSON["Regular_Arrows"], self.JUCSON["PublicTransport_Arrows"]]
        orig_lanes = ["R", "TR", "T", "TL", "L", "A", "RL"]
        directions = [self.OUTJUNC.NO.LAN, self.OUTJUNC.SO.LAN, self.OUTJUNC.EA.LAN, self.OUTJUNC.WE.LAN]

        for direc in directions:
            for lan in orig_lanes:
                if arr_list[0]:
                    cur_arrow_input = [arr_list[0][0], arr_list[1][0]]
                    if lan == "R":
                        SR_cur_arrow_input = [0, 0]
                        if arr_list[0][0] == 9:
                            SR_cur_arrow_input[0] = 1
                            cur_arrow_input[0] = 0
                        if arr_list[1][0] == 9:
                            SR_cur_arrow_input[1] = 1
                            cur_arrow_input[1] = 0
                        if sum(SR_cur_arrow_input) > 0:
                            setattr(direc, "SR", SR_cur_arrow_input)
                    setattr(direc, lan, cur_arrow_input)
                    arr_list[0].pop(0)
                    arr_list[1].pop(0)

    def pull_arr(self):
        regular, public = [], []
        both_arrows = {"R": [0, 0], "TR": [0, 0], "T": [0, 0], "TL": [0, 0], "L": [0, 0], "A": [0, 0], "RL": [0, 0]}
        directions = [self.OUTJUNC.NO.LAN, self.OUTJUNC.SO.LAN, self.OUTJUNC.EA.LAN, self.OUTJUNC.WE.LAN]

        for direc in directions:
            cur_sr = getattr(direc, "SR")
            temp_r = [0, 0]
            if cur_sr[0] == 1:
                temp_r[0] = 9
            if cur_sr[1] == 1:
                temp_r[1] = 9
            if sum(temp_r) > 0:
                both_arrows["R"] = temp_r

            for lan in both_arrows.keys():
                if lan == "R" and sum(temp_r) > 0:
                    continue
                else:
                    cur_lan = getattr(direc, lan)
                    both_arrows[lan] = cur_lan
            for arrows in both_arrows.keys():
                regular.append(both_arrows[arrows][0])
                public.append(both_arrows[arrows][1])

        self.OUTJUCSON["Regular_Arrows"] = regular
        self.OUTJUCSON["PublicTransport_Arrows"] = public

    def push_vol(self):
        """the method uses the output volumes of Phaser to push them into the right subclass of each direction,
        divided to morning and evening"""
        vol_list = [self.JUCSON["Morning_Volumes"], self.JUCSON["Evening_Volumes"]]
        directions_mor = [self.OUTJUNC.NO.MOR, self.OUTJUNC.SO.MOR, self.OUTJUNC.EA.MOR, self.OUTJUNC.WE.MOR]
        directions_eve = [self.OUTJUNC.NO.EVE, self.OUTJUNC.SO.EVE, self.OUTJUNC.EA.EVE, self.OUTJUNC.WE.EVE]
        count = -1

        for vol in vol_list:
            count += 1
            if count == 0:
                directions = directions_mor
            else:
                directions = directions_eve
            for direc in directions:
                routes = ["R", "T", "L"]
                for rou in routes:
                    if vol:
                        value_to_push = int(vol[0])
                        setattr(direc, rou, value_to_push)
                        vol.pop(0)

    def pull_vol(self):
        self.OUTJUCSON["Morning_Volumes"] = []
        self.OUTJUCSON["Evening_Volumes"] = []
        directions = ["NO", "SO", "EA", "WE"]
        routes = ["R", "T", "L"]
        err_value = ["", " "]

        for direction in directions:
            cur_direction = getattr(self.OUTJUNC, direction)
            cur_mor = getattr(cur_direction, "MOR")
            cur_eve = getattr(cur_direction, "EVE")
            for route in routes:
                cur_mor_route = getattr(cur_mor, route)
                cur_eve_route = getattr(cur_eve, route)
                if cur_mor_route in err_value or type(cur_mor_route) == str:
                    cur_mor_route = 0
                if cur_eve_route in err_value or type(cur_eve_route) == str:
                    cur_eve_route = 0
                self.OUTJUCSON["Morning_Volumes"].append(cur_mor_route)
                self.OUTJUCSON["Evening_Volumes"].append(cur_eve_route)

    def push_street_names(self):
        """the method uses the output street names of Phaser to push it into phsr_lst subclass and to the
        matching property in that subclass (STREET)."""
        phaser_street_names_list = self.JUCSON["Street_Names"]
        dir_list = {"NO": self.OUTJUNC.NO, "SO": self.OUTJUNC.SO, "EA": self.OUTJUNC.EA, "WE": self.OUTJUNC.WE}
        dir_keys = list(dir_list.keys())
        for cur_dir in dir_keys:
            the_dir = dir_list[cur_dir]
            the_name = phaser_street_names_list[dir_keys.index(cur_dir)]
            setattr(the_dir, "NAME", the_name)

    def pull_street_names(self):
        self.OUTJUCSON["Street_Names"] = []
        direction_names = [self.OUTJUNC.NO.NAME, self.OUTJUNC.SO.NAME, self.OUTJUNC.EA.NAME, self.OUTJUNC.WE.NAME]
        for cur_name in direction_names:
            self.OUTJUCSON["Street_Names"].append(cur_name)

    def push_general_info(self):
        """the method uses the output general information of Phaser to push it into G_INF subclass and to each
        matching property in that subclass. For specific info that related to the LRT, it pushes it to LRT_INF """
        phaser_gen_info_list = self.JUCSON["General_Information"]
        info_list = [self.OUTJUNC.G_INF, self.OUTJUNC.LRT_INF]
        inf_counter = 0
        lrt_types = [0, 0]
        info_types = ["CAP", "NLSL", "ELWL", "IMG5", "IMG6", "GEONS", "GEOEW", "LOOP", "LRT_Orig", "LRT_Orig",
                      "INF"]
        while inf_counter < len(info_types):
            if inf_counter == 8 or inf_counter == 9:
                curr_inf = info_list[1]
                lrt_types[inf_counter - 8] = phaser_gen_info_list[inf_counter]
                data_to_push = lrt_types
            else:
                curr_inf = info_list[0]
                data_to_push = phaser_gen_info_list[inf_counter]
            setattr(curr_inf, info_types[inf_counter], data_to_push)
            inf_counter += 1
        self.OUTJUNC.LRT_INF.lrt_orig_to_dir()

    def pull_general_info(self):
        self.OUTJUCSON["General_Information"] = []
        info_list = self.OUTJUNC.G_INF
        lrt_info = self.OUTJUNC.LRT_INF.LRT_Orig
        info_types = ["CAP", "NLSL", "ELWL", "IMG5", "IMG6", "GEONS", "GEOEW", "LOOP", "LRT_Orig", "INF"]

        for info in info_types:
            if info == "LRT_Orig":
                self.OUTJUCSON["General_Information"].extend(lrt_info)
            else:
                cur_info = getattr(info_list, info)
                self.OUTJUCSON["General_Information"].append(int(cur_info))

    def push_lrt_info(self):
        """the method uses the output LRT information of Phaser to push it into LRT_INF subclass and to each
        matching property in that subclass."""
        phaser_lrt_info_list = self.JUCSON["LRT_Information"]
        phaser_lrt_info_list.pop(0)
        lrt_info_types = ["CYC_TIME", "LRT_LOST_TIME", "LRT_HDWAY", "LRT_MCU", "GEN_LOST_TIME"]
        for lrt_inf in lrt_info_types:
            setattr(self.OUTJUNC.LRT_INF, lrt_inf, phaser_lrt_info_list[lrt_info_types.index(lrt_inf)])

    def pull_lrt_info(self):
        self.OUTJUCSON["LRT_Information"] = []
        lrt_info_types = ["CYC_TIME", "LRT_LOST_TIME", "LRT_HDWAY", "LRT_MCU", "GEN_LOST_TIME"]
        if self.OUTJUNC.LRT_INF.LRT_Dir > 0:
            self.OUTJUCSON["LRT_Information"].append(1)
        else:
            self.OUTJUCSON["LRT_Information"].append(0)

        for lrt_inf in lrt_info_types:
            cur_lrt_inf = getattr(self.OUTJUNC.LRT_INF, lrt_inf)
            self.OUTJUCSON["LRT_Information"].append(cur_lrt_inf)

#
#
# junc_diagram = Diagram()
#
# vc = VolCov(r"C:\Users\darta\Desktop\volume_calculator.xlsx")
#
# jucon = vc.toJSON()
#
# juc = Jucson(junc_diagram)
# juc.loadJucson(r"C:\Users\darta\Desktop\×JUCSON×2021_10_11-12_03_33_PM.json")

# juc.saveJucsonFromDiagram(r"C:\Users\darta\Desktop")
