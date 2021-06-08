import os
from lxml import etree
from copy import deepcopy
from shutil import copyfile, rmtree
import opcdiag


def duplicate_pptx_sheet(filename, slide_number, filename_output=None):
    """
    A method that duplicates a slide in a PowerPoint file

    Parameters
    ----------
    filename : string
        The filename contains the location of the original powerpoint file that
        will have a slide duplicated.

    slide_number : int
        The slide_number is the index of the slide that is supposed to be
        duplicated in the powerpoint file.
        Note: The index starts counting from 1 NOT 0

    filename_output : string
        The filename_output is the name of the file that will be created.
        Note: If the filename_output is not supplied, then the input file
              get's owerridden.

    Returns : nothing
    """

    if filename_output is None:
        filename_output = filename

    # Step 1. Extract the pptx file
    opc = OpcController()
    TEMP_FOLDER = filename.replace(".pptx", '')
    opc.extract_package(filename, TEMP_FOLDER)

    # Step 2. Find the next_slide_id
    slides_list = [x for x in os.listdir("{}/ppt/slides/".format(TEMP_FOLDER))
                   if '.xml' in x]
    slides_count = len(slides_list)
    next_slide_id = slides_count + 1

    # Step 3. Copy the oldslide and it's relationship
    xml_slide = "{}/ppt/slides/slide{}.xml"
    xml_slide_rel = "{}/ppt/slides/_rels/slide{}.xml.rels"
    copyfile(xml_slide.format(TEMP_FOLDER, slide_number),
             xml_slide.format(TEMP_FOLDER, next_slide_id))
    copyfile(xml_slide_rel.format(TEMP_FOLDER, slide_number),
             xml_slide_rel.format(TEMP_FOLDER, next_slide_id))

    # Step 4 Find the chartfile and related data files.
    # Get the chart#.xml file from the slide relation (hacky indeed)
    with open(xml_slide_rel.format(TEMP_FOLDER, next_slide_id)) as file:
        lines = [line for line in file.readlines() if '/charts/chart' in line]

    # Paths where the files are
    xml_chart = "{}/ppt/charts/chart{}.xml"
    xml_style = "{}/ppt/charts/style{}.xml"
    xml_colors = "{}/ppt/charts/colors{}.xml"
    xml_chart_rel = "{}/ppt/charts/_rels/chart{}.xml.rels"
    xml_xlsx = "{}/ppt/embeddings/Microsoft_Excel_Worksheet{}.xlsx"

    # This gets populated with lxml Elements, they will go into [Content_Types].xml
    content_types = [
        etree.XML('<Override PartName="/ppt/slides/slide{}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'.format(
            next_slide_id
        ))
    ]

    # If there are no charts in this slide, no need to do the files/data copying
    if len(lines) > 0:
        for line in lines:
            # Reset the filenames. The files are not always in the pptx file.
            style_filename = None
            colors_filename = None
            xlsx_filename = None

            # Step 5. Find the chart_id
            # example: chart1.xml, chart2.xml, chart3.xml
            chart_filename = line.split('Target="../charts/')[-1].replace('"/>\n', '')
            chart_id = int(chart_filename.replace('chart', '').replace('.xml', ''))

            # Step 6. Find the next_chart_id
            chart_list = [x for x in os.listdir("{}/ppt/charts/".format(TEMP_FOLDER))
                           if 'chart' in x]
            next_chart_id = len(chart_list) + 1

            # Step 7. Get the style#.xml, colors#.xml and #.xlsx filenames and ids
            with open(xml_chart_rel.format(TEMP_FOLDER, chart_id)) as file:
                for line in file.readlines():
                    if 'Target="style' in line:
                        style_filename = line.split('Target="')[-1].replace('"/>\n', '')
                        style_id = style_filename.replace('style', '').replace('.xml', '')
                    if 'Target="colors' in line:
                        colors_filename = line.split('Target="')[-1].replace('"/>\n', '')
                        colors_id = colors_filename.replace('colors', '').replace('.xml', '')
                    elif 'Target="../embeddings' in line:
                        xlsx_filename = line.split('Target="../embeddings/')[-1].replace('"/>\n', '')
                        xlsx_id = xlsx_filename.replace('Microsoft_Excel_Worksheet', '').replace('.xlsx', '')

            # Step 8. Copy the charts, styles, colors, xlsx and rel files.
            # Note: The "-1" id's are used later to skip checking if the id
            # exists. The replace method won't find the -1 ids, so it skips them.
            if style_filename is not None:
                next_style_id = len([f for f
                                     in os.listdir('{}/ppt/charts/'.format(TEMP_FOLDER))
                                     if 'style' in f]) + 1
                copyfile(xml_style.format(TEMP_FOLDER, style_id),
                         xml_style.format(TEMP_FOLDER, next_style_id))
                content_types.append(
                    etree.XML(
                          '<Override PartName="/ppt/charts/style{}.xml" ContentType="application/vnd.ms-office.chartstyle+xml"/>'.format(
                            next_style_id
                        )
                    )
                )
            else:
                style_id = "-1"
                next_style_id = "-1"

            if colors_filename is not None:
                next_colors_id = len([f for f
                                      in os.listdir('{}/ppt/charts/'.format(TEMP_FOLDER))
                                      if 'colors' in f]) + 1
                copyfile(xml_colors.format(TEMP_FOLDER, colors_id),
                         xml_colors.format(TEMP_FOLDER, next_colors_id))
                content_types.append(
                    etree.XML(
                          '<Override PartName="/ppt/charts/colors{}.xml" ContentType="application/vnd.ms-office.chartcolorstyle+xml"/>'.format(
                            next_colors_id
                        )
                    )
                )
            else:
                colors_id = "-1"
                next_colors_id = "-1"

            if xlsx_filename is not None:
                next_xlsx_id = len([f for f in os.listdir('{}/ppt/embeddings/'.format(TEMP_FOLDER))]) + 1
                copyfile(xml_xlsx.format(TEMP_FOLDER, xlsx_id),
                         xml_xlsx.format(TEMP_FOLDER, next_xlsx_id))
            else:
                xlsx_id = "-1"
                next_xlsx_id = "-1"

            copyfile(xml_chart.format(TEMP_FOLDER, chart_id),
                     xml_chart.format(TEMP_FOLDER, next_chart_id))
            copyfile(xml_chart_rel.format(TEMP_FOLDER, chart_id),
                     xml_chart_rel.format(TEMP_FOLDER, next_chart_id))

            # NOTE: All files exist at this stage, now we start replacing them
            #       with correct values/indexes.
            # Step 9. Replace the id's in the chart relationship file
            with open(xml_chart_rel.format(TEMP_FOLDER, next_chart_id), 'r') as chart_rel:
                xml_chart_rel_file = chart_rel.read()

            # This is where the "-1" id whon't be found and thusly skipped.
            xml_chart_rel_file = xml_chart_rel_file.replace(
                'style{}.xml'.format(style_id),
                'style{}.xml'.format(next_style_id)
            ).replace(
                'colors{}.xml'.format(colors_id),
                'colors{}.xml'.format(next_colors_id)
            ).replace(
                'Microsoft_Excel_Worksheet{}.xlsx'.format(xlsx_id),
                'Microsoft_Excel_Worksheet{}.xlsx'.format(next_xlsx_id)
            )

            with open(xml_chart_rel.format(TEMP_FOLDER, next_chart_id), 'w') as chart_rel:
                chart_rel.write(xml_chart_rel_file)

            # Step 10. Replace the Target attribute in the slide#.xml.rel
            with open(xml_slide_rel.format(TEMP_FOLDER, next_slide_id), 'r') as slide_rel:
                xml_slide_rel_file = slide_rel.read()

            xml_slide_rel_file = xml_slide_rel_file.replace(
                'chart{}.xml'.format(chart_id),
                'chart{}.xml'.format(next_chart_id)
            )

            with open(xml_slide_rel.format(TEMP_FOLDER, next_slide_id), 'w') as slide_rel:
                slide_rel.write(xml_slide_rel_file)

            # Step 11. Add the chart lxml Element into the content_types container.
            content_types.append(
                etree.XML(
                    '<Override PartName="/ppt/charts/chart{}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawingml.chart+xml"/>'.format(
                        next_chart_id
                    )
                )
            )


    # Step 12. Add the newly created content to the [Content_Types].xml file
    tree = etree.parse('{}/[Content_Types].xml'.format(TEMP_FOLDER))
    root = tree.getroot()
    for element in content_types:
        root.append(element)

    with open('{}/[Content_Types].xml'.format(TEMP_FOLDER), 'w') as file:
        # Hack :: Inject the top tag [<?xml ...] back into the file.
        #         (Can't do it with lxml?)
        file.writelines(
            "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>{}".format(
                etree.tostring(root)
            )
        )

    # Step 13. Find the next slide presentation relation id and add a new
    #          relation to the presentation.xml.rels relationship file
    tree = etree.parse('{}/ppt/_rels/presentation.xml.rels'.format(TEMP_FOLDER))
    root = tree.getroot()
    next_slide_rid = len(root.getchildren()) + 1
    root.append(
        etree.XML(
            '<Relationship Id="rId{}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{}.xml"/>'.format(
                next_slide_rid,
                next_slide_id
            )
        )
    )
    with open('{}/ppt/_rels/presentation.xml.rels'.format(TEMP_FOLDER), 'w') as file:
        # Hack :: Inject the top tag [<?xml ...] back into the file.
        #         (Can't do it with lxml?)
        file.writelines(
            "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>{}".format(
                etree.tostring(root)
            )
        )

    # Step 14. Add the new relation id (from Step 13) and a new id to the
    #          presentation.xml.
    tree = etree.parse('{}/ppt/presentation.xml'.format(TEMP_FOLDER))
    root = tree.getroot()
    sldIdLst = root.find(
        './/p:sldIdLst',
        {'p': "http://schemas.openxmlformats.org/presentationml/2006/main"}
    )
    sldId = deepcopy(sldIdLst.getchildren()[0])  # get the first child
    sldId.attrib['id'] = unicode(max([int(x.attrib['id']) for x in sldIdLst]) + 1)
    sldId.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'] = "rId{}".format(next_slide_rid)
    sldIdLst.append(sldId)

    with open('{}/ppt/presentation.xml'.format(TEMP_FOLDER), 'w') as file:
        # Hack :: Inject the top tag [<?xml ...] back into the file.
        #         (Can't do it with lxml?)
        file.writelines(
            "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>{}".format(
                etree.tostring(root)
            )
        )

    opc.repackage(TEMP_FOLDER, filename_output)
    rmtree(TEMP_FOLDER)