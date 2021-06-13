import os.path
from Main_Diagram import *


def create_new_table_templates_file():
    """The function creates a new copy of the Table templates; that will be the file to start working on
    It saves the new copy in the base directory"""
    src = os.getcwd() + r"\Table_template\Table_templates.pptx"
    prs_tbl = Presentation(src)
    prs_tbl.save("Table_new_template.pptx")


def del_slides_table(pres, chosen_type):
    """The function gets the Table file and the chosen type of table and deletes all slides that don't match that
    number """
    i = len(pres.slides)
    while i > 0:
        if i != chosen_type:
            rId = pres.slides._sldIdLst[i - 1].rId
            pres.part.drop_rel(rId)
            del pres.slides._sldIdLst[i - 1]
        i -= 1
    pres.save("Del_Table.pptx")


def save_table(pres):
    """The function gets the final Table pptx file and saves it in the created ×JUNC× folder on the desktop"""
    desktop_table = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    path = desktop_table + "\×JUNC×"
    save_export_path = path + r'\×Table×.pptx'
    pres.save(save_export_path)
    export_png_table(save_export_path)


def export_png_table(path):
    """The function creates a folder and exports a png photo of the table to that folder; before that,
    it calls 'fix_text_table' """
    f = os.path.abspath(path)
    fix_text_table(path)
    powerpoint = cli.CreateObject('Powerpoint.Application')
    powerpoint.ActivePresentation.Export(f, 'PNG')
    powerpoint.ActivePresentation.Close()


def fix_text_table(received_table):
    """The function fixes an issue occurs when trying to apply TEXT_TO_FIT_SHAPE in the other functions.
    It uses a different type of library (not python-pptx) that acts like VBA"""
    App = win32com.client.Dispatch("PowerPoint.Application")
    App.Visible = True
    Pres = App.Presentations.Open(received_table)
    App.CommandBars.ExecuteMso("SlideReset")
    Pres.Save()


def delete_temp_table_pres():
    """The function deletes all the temporary powerpoint files created while creating the final one"""
    prs_to_del = ["Table_new_template.pptx", "Del_Table.pptx", "Vol_Table.pptx", "Info_Table.pptx", "Dirc_Table.pptx"]
    for temp_prs in prs_to_del:
        if os.path.exists(temp_prs):
            os.remove(temp_prs)
