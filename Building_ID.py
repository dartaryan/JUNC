import os.path
import win32com.client
from Main_Table import *
from PIL import Image

output_directory = JUNC_Diagram.OUTPUT


def create_new_id_templates_file():
    """The function creates a new copy of the ID templates; that will be the file to start working on
    It saves the new copy in the base directory"""
    src = os.getcwd() + r"\ID_template\id_template.pptx"
    prs_id = Presentation(src)
    prs_id.save("id_template.pptx")


def save_id(pres):
    """The function gets the final ID pptx file and saves it in the created ×JUNC× folder on the output_directory"""
    # desktop_id = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    # path = desktop_id + r"\×JUNC×"
    # desktop_id = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = output_directory + r"\×JUNC×"
    save_export_path = path + r'\×ID×.pptx'
    pres.save(save_export_path)
    export_png_id(save_export_path)


def export_png_id(path):
    """The function creates a folder and exports a png photo of the ID to that folder; before that,
    it calls 'fix_text_ID' """
    f = os.path.abspath(path)
    fix_text_id(path)
    powerpoint = cli.CreateObject('Powerpoint.Application')
    powerpoint.ActivePresentation.Export(f, 'PNG')
    powerpoint.ActivePresentation.Close()
    powerpoint.Quit()


def fix_text_id(received_id):
    """The function fixes an issue occurs when trying to apply TEXT_TO_FIT_SHAPE in the other functions.
    It uses a different type of library (not python-pptx) that acts like VBA"""
    App = win32com.client.Dispatch("PowerPoint.Application")
    App.Visible = True
    Pres = App.Presentations.Open(received_id)
    App.CommandBars.ExecuteMso("SlideReset")
    Pres.Save()


def delete_temp_id_pres():
    """The function deletes all the temporary powerpoint files created while creating the final one"""
    prs_to_del = ["id_template.pptx", "id_info.pptx"]
    for temp_prs in prs_to_del:
        if os.path.exists(temp_prs):
            os.remove(temp_prs)


def crop_table(img_path, phase_num):
    im = Image.open(img_path)
    width, height = im.size
    left = 0
    top = 0
    right = width
    times_phase = 27.5 - (2.4 * (6 - phase_num))
    bottom = height * (times_phase / 27.5)
    cropped = im.crop((left, top, right, bottom))
    cropped.save(img_path)


def organize_final_folder(img_num):
    """The function organizes all the outputs in the ×JUNC× folder:
        - Picture are moved to the main folder from sub folders.
        - Pptx files are moved into one folder called ×pptx files×.
        - A copy of the volume_calculator that was used to create the JUNC, is copied into that folder.
        """

    # TODO change vol calc to jucson file
    # vol_calc = os.getcwd() + r"\volume_calculator.xlsx"
    # shutil.copyfile(vol_calc, path + r"\volume_calculator.xlsx")

    # desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = output_directory + r"\×JUNC×"
    foldersList = ["×ID×", "×Diagram×", "×Table×"]
    os.makedirs(path + r"\×pptx files×")
    for cur_name in foldersList:
        files = os.listdir(path + "\\" + cur_name + "\\")
        pngFile = files[0]
        name_old_path = path + "\\" + cur_name + "\\" + pngFile
        name_new_path = path + "\\" + cur_name + ".png"
        os.rename(name_old_path, name_new_path)
        shutil.rmtree(path + "\\" + cur_name)
        pptx_old_path = path + "\\" + cur_name + ".pptx"
        pptx_new_path = path + r"\×pptx files×" + "\\" + cur_name + ".pptx"
        os.rename(pptx_old_path, pptx_new_path)
    img_table_path = path + r"\×Table×.png"
    crop_table(img_table_path, img_num)
