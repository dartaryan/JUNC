import Phaser
from Diagram import *
from Phaser_Output import PhsrOutput

JUNC_Diagram = Diagram()
set_output_directory(JUNC_Diagram.OUTPUT)
rearrange_folders()

new_phaser_list, new_excel_properties = Phaser.main()

# insert here all the info from junc
print("new_phaser_list: ", new_phaser_list)
print("new_excel_properties: ", new_excel_properties)

JUNC_Diagram.phsr_lst = PhsrOutput(new_phaser_list)
JUNC_Diagram.xlprop = new_excel_properties
print("-----")
JUNC_Diagram.push_arr()
JUNC_Diagram.push_vol()
JUNC_Diagram.push_general_info()
JUNC_Diagram.push_lrt_info()
JUNC_Diagram.push_street_names()

create_new_diagram_template_file()

prs = Presentation("Diagram_new_template.pptx")
del_slides(prs, JUNC_Diagram.get_type_of_junc_for_choosing_slide())
prs = Presentation("Del_Diagram.pptx")
JUNC_Diagram.add_street_name_and_lrt(prs)
prs = Presentation("Street_Diagram.pptx")
JUNC_Diagram.add_morning_volumes(prs)
prs = Presentation("Morn_Diagram.pptx")
JUNC_Diagram.add_evening_volumes(prs)
prs = Presentation("Eve_Diagram.pptx")
JUNC_Diagram.add_direction_arrows(prs)
prs = Presentation("Dirc_Diagram.pptx")
save_diagram(prs)
delete_temp_diagram_pres()
