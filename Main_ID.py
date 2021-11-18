import Main_Table
import Main_Diagram
from ID import *
from Diagram import Diagram

Input_Diagram = Diagram()


def set_Diagram(DiagramInput):
    global Input_Diagram
    Input_Diagram = DiagramInput


def main():
    JUNC_Diagram = Main_Diagram.main(Input_Diagram)
    JUNC_Table = Main_Table.main(JUNC_Diagram)
    set_id_output_directory(JUNC_Diagram.OUTPUT)
    JUNC_ID = JUNC_Diagram.ID
    create_new_id_templates_file()
    id_prs = Presentation("id_template.pptx")
    JUNC_ID.add_info(id_prs)
    id_prs = Presentation("id_info.pptx")
    save_id(id_prs)
    delete_temp_id_pres()
    organize_final_folder(JUNC_Table.IMG)
    return ("Done!")

if __name__ == "__main__":
    main()
