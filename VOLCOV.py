import ctypes
import json
import openpyxl as xl
from datetime import datetime


def suppress_null(val):
    if not val:
        return 0
    else:
        return val


class VolCov:
    """
    A class used to get data from a volume calculator file and format it to a Diagram Class
    """

    def __init__(self, VC_file_directory=""):
        """ The constructor of the Volume calculator format. To initialize, gets the directory of the VC file and
        sets each sublist to the right property. """

        self.__VC_file = VC_file_directory
        self.vc_json = {}
        # self.__Morning_Volumes = ""
        # self.__Regular_Arrows = ""
        # self.__General_Information = ""
        # self.__LRT_Information = ""
        # self.__PublicTransport_Arrows = ""
        # self.__Evening_Volumes = ""
        # self.__Street_Names = ""
        # self.__ID_Information = ""

    # 0 ['Morning volume', [0, 1515, 560, 820, 594, 0, 685, 0, 76, 0, 0, 0]]
    # 1 ['lanes', [0, 0, 1, 0, 1, 0, 0, 9, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # 2 ['instructions', [1800, 0, 1, 1, 0, 3, 3, 0, 0, 0, 1]]
    # 3 ['rakal_instructions', [0, 120, 25, 4, 1, 0]]
    # 4 ['junc_public_trans', [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
    # 5 ['Evening volume', [0, 1749, 615, 743, 774, 0, 312, 0, 110, 0, 0, 0]]
    # 6 ['streets', ['משה דיין', 'משה דיין', 'שמשון', 0]]
    # 7 ['junc_instructions', [0, 0, 0, 0, 0]]

    def toJSON(self):
        VC_list, xl_prop = self.getVC()
        VC_titles = ["Morning_Volumes", "Regular_Arrows", "General_Information", "LRT_Information",
                     "PublicTransport_Arrows", "Evening_Volumes", "Street_Names", "ID_Information"]
        for title, data in zip(VC_titles, VC_list):
            self.vc_json[title] = data
        self.vc_json["VC_Author"] = xl_prop[0].lastModifiedBy
        return self.vc_json

    def saveFile(self, directory=""):
        time_stamp = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
        location = directory + "×JUCSON×" + time_stamp + ".json"
        print(location)
        with open(location, "w+") as f:
            json.dump(self.toJSON(), f)

    def read_from_excel(self, run):
        wb = xl.load_workbook(self.VC, data_only=True)
        ws = wb.active
        volume = []
        lanes = []
        public_trans = []
        junc_public_trans = []
        streets = []

        junc_instructions = [suppress_null(ws.cell(row=36 + i, column=19).value) for i in range(5)]

        for i in range(4):
            temp_volume = [suppress_null(ws.cell(row=4 + run, column=4 + 4 * i + j).value) for j in range(3)]
            volume += temp_volume
            temp_lanes = [suppress_null(ws.cell(row=8, column=3 + 8 * i + j).value) for j in range(7)]
            lanes += temp_lanes
            temp_public_trans = [suppress_null(ws.cell(row=9, column=3 + 8 * i + j).value) for j in range(7)]
            public_trans += temp_public_trans
            temp_junc_public_trans = [suppress_null(ws.cell(row=9, column=3 + 8 * i + j).value) for j in range(7)]
            junc_public_trans += temp_junc_public_trans

        instructions = [suppress_null(ws.cell(row=36 + i, column=22).value) for i in range(11)]
        for i in range(12):
            try:
                volume[i] = round(volume[i] * instructions[10], 0)
            except:
                error = "volume must be put as numbers"
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, error, 'Phaser error', 0)
                exit()
        rakal_instructions = [suppress_null(ws.cell(row=36 + i, column=26).value) for i in range(6)]

        for i in range(6):
            if i == 4 and rakal_instructions[i] == 1.125:
                i = i + 1
            if not isinstance(rakal_instructions[i], int):
                error = "rakal instructions table must be integers"
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, error, 'Phaser error', 0)
                exit()
        for i in range(11):

            # אם בעתיד מגדילים את הריינג' לשנות את פקדות הברייק שמתחת
            if i == 10 and isinstance(instructions[i], float):
                break
            if not isinstance(instructions[i], int):
                error = "instructions table must be integers"
                MessageBox = ctypes.windll.user32.MessageBoxW
                MessageBox(None, error, 'Phaser error', 0)
                exit()

        for rakal_cell in range(12):
            if (rakal_cell + 2) % 3 != 0:
                volume[rakal_cell] = round(volume[rakal_cell] * rakal_instructions[4], 0)
        if instructions[7] == 1:
            for m in range(28):
                public_trans[m] = 0
        for cell_street in range(4):
            temp_street = [suppress_null(ws.cell(row=4, column=22 + cell_street).value)]
            if temp_street == 0:
                temp_street = ""
            streets += temp_street

        prop = wb.properties
        return volume, lanes, instructions, rakal_instructions, public_trans, streets, \
               junc_instructions, wb.properties, junc_public_trans

    def getVC(self):
        run = 0
        junc_list = []
        excel_properties_list = []

        while run < 2:
            wb = xl.load_workbook(self.VC)

            active = wb.active
            volume, lanes, instructions, rakal_instructions, public_trans, streets, junc_instructions, \
            excel_properties, junc_public_trans = self.read_from_excel(run)

            # שליחת נתונים לגאנק
            junc_list.append(volume)

            if run == 0:
                junc_list.append(lanes)
                junc_list.append(instructions)
                junc_list.append(rakal_instructions)
                junc_list.append(junc_public_trans)

            if run == 1:
                junc_list.append(streets)
                junc_list.append(junc_instructions)
                excel_properties_list.append(excel_properties)

            run = run + 1

        return junc_list, excel_properties_list

    @property
    def VC(self):
        """Get the phaser list info"""
        return self.__VC_file


if __name__ == "__main__":
    vc = VolCov(r"C:\Users\darta\Desktop\Bens\Work\Python\JUNC\git\JUNC\volume_calculator.xlsx")
    vc.saveFile()
    print(vc.getVC())
