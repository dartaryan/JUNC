from Table import *


def main(DiagramInput):
    set_output_directory(DiagramInput.OUTPUT)
    JUNC_Table = Table(DiagramInput)
    JUNC_Table.push_deter_vol()
    JUNC_Table.push_section_info()
    JUNC_Table.push_arrow_imgs()

    create_new_table_templates_file()
    prs = Presentation("Table_new_template.pptx")
    del_slides_table(prs, JUNC_Table.get_type_of_table_for_choosing_slide())
    prs = Presentation("Del_Table.pptx")
    JUNC_Table.add_deter_volumes(prs)
    prs = Presentation("Vol_Table.pptx")
    JUNC_Table.add_table_info(prs)
    prs = Presentation("Info_Table.pptx")
    JUNC_Table.add_table_arrows(DiagramInput, prs)
    prs = Presentation("Dirc_Table.pptx")
    save_table(prs)
    delete_temp_table_pres()
    return JUNC_Table
