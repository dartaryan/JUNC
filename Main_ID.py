from ID import *


def main():
    new_info = JUNC_Table.phsrlst.ID_INFO
    JUNC_ID = ID(new_info)
    JUNC_ID.push_id_info(JUNC_Diagram)
    create_new_id_templates_file()
    id_prs = Presentation("id_template.pptx")
    JUNC_ID.add_info(id_prs)
    id_prs = Presentation("id_info.pptx")
    save_id(id_prs)
    delete_temp_id_pres()
    organize_final_folder(JUNC_Table.IMG)


if __name__ == "__main__":
    main()
