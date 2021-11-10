import Phaser
from Diagram import *
from Phaser_Output import PhsrOutput


def main(JUNC_Diagram):
    set_output_directory(JUNC_Diagram.OUTPUT)
    rearrange_folders()

    # new_phaser_list, new_excel_properties = Phaser.main()
    new_phaser_list = ['Morning', [0, 1515, 560, 820, 594, 0, 685, 0, 76, 0, 0, 0],
                       [0, 0, 1, 0, 1, 0, 0, 9, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [1800, 0, 1, 1, 0, 3, 3, 0, 0, 0, 1], [0, 120, 25, 4, 1, 0],
                       [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       1.0972413793103448, 1591.0,
                       {'AEr': 609.0, 'ANl': 560.0, 'ANt': 921.0, 'BEl': 76.0, 'BEr': 76.0, 'CNt': 594.0, 'CSt': 594.0,
                        'imageA': 921.0, 'imageB': 76.0, 'imageC': 594.0, 'imageD': 0.0, 'imageE': 0.0, 'imageF': 0.0},
                       1800, 'Evening', [0, 1749, 615, 743, 774, 0, 312, 0, 110, 0, 0, 0],
                       [0, 0, 1, 0, 1, 0, 0, 9, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       [1800, 0, 1, 1, 0, 3, 3, 0, 0, 0, 1], [0, 120, 25, 4, 1, 0],
                       [0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                       1.2820689655172415, 1859.0,
                       {'ANt': 1134.0, 'ASt': 774.0, 'BEl': 110.0, 'CEr': 312.0, 'CNl': 615.0, 'CNt': 615.0,
                        'imageA': 1134.0, 'imageB': 110.0, 'imageC': 615.0, 'imageD': 0.0, 'imageE': 0.0,
                        'imageF': 0.0},
                       1800, ['משה דיין', 'משה דיין', 'שמשון', 0], [0, 0, 0, 0, 0]]
    # insert here all the info from junc
    # print("new_phaser_list: ", new_phaser_list)
    # print("new_excel_properties: ", new_excel_properties)

    JUNC_Diagram.phsr_lst = PhsrOutput(new_phaser_list)
    JUNC_Diagram.xlprop = "new_excel_properties"
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
    return JUNC_Diagram
