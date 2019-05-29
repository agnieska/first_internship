#!/usr/bin/env python
# coding: utf-8


import json
from pprint import pprint
import pandas as pd
import math
from .extract_tables import getAreas_pt,get_gimp_camelot_delta



################################################################
###                 Functions                                ###
################################################################


def save_json (dictionnary, filename) :
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(dictionnary, file)

def read_json (filename) :
    with open(filename, mode='r', encoding='utf-8') as file:
        return json.load(file)  


################################################################
#### Points and Pixels Conversion functions
################################################################


def point_to_pixel_dic (points):
    pixels ={}
    pixels["first_point"] = {}
    pixels["first_point"]["left"] = int(points[0] / 72 *110)
    pixels["first_point"]["bottom"] = int(points[1] / 72 *110)
    pixels["last_point"] = {}
    pixels["last_point"]["left"] = int(points[2] / 72 *110)
    pixels["last_point"]["bottom"] = int(points[3] / 72 *110)
    return pixels

def point_to_pixel_li (points, filename) :
    li = []
    pixels = {}
    for el in points :
        li.append(int(el * 72 / 110) )
    pixels[filename] = li
    return pixels




##########################################################################
####                          Css :  functions
##########################################################################


def read_header_html_files (filename_liste, path) :
    headerHTML_liste = {}
    for filename in filename_liste :    
        adress = path + filename
        with open (adress, encoding='utf-8', mode='r') as file :
            maliste = []
            line = file.readline()
            maliste.append(line)
            while (line != '') & (line != '<!-- Begin text definitions (Positioned/styled in CSS) -->\n') :       
                line = file.readline()
                maliste.append(line)
            headerHTML_liste[filename] = maliste
    return headerHTML_liste



def create_id_dictionnary (page_name, headerHTML) :
    maliste = []
    for line in headerHTML :
        if line[0]=='#' :
            maliste.append(line[1:-1])
    page_id_dict = {}
    for line in maliste :
        div_id = line.split('{')[0]
        div_value = '{' + line.split('{')[1]
        div_values_list = div_value[1:-2].split(';')
        div_values_dict ={}
        for el in div_values_list :
            k, v = el.split(':')
            div_values_dict[k] = v
        page_id_dict[div_id] = div_values_dict
    return page_id_dict


def get_bottom (div_id, page_id_dict) :
    if div_id != "id=not_found" :
        bottom =  page_id_dict[div_id]['bottom']
    else : bottom = "not_found"
    return bottom


def get_left (div_id,  page_id_dict) :
    if div_id != "id=not_found" :
        left = page_id_dict[div_id]['left']
    else : left = "not_found"
    return left

def get_integer_px (chaine_px) :
    if chaine_px != "not_found" :
        value =  int(chaine_px[:-2])
    else : 
        value = 0
    return value




########################################################################
####                       Body html : functions
########################################################################


def read_html_files_to_body_list (bodyHTML_liste, filename_liste, path) :
    if bodyHTML_liste == None :
        bodyHTML_liste = {}
    for filename in filename_liste :    
        adress = path + filename
        with open (adress, encoding='utf-8', mode='r') as file :
            line = file.readline()
            maliste = []
            while (line != '') & (line != '<!-- Begin text definitions (Positioned/styled in CSS) -->\n') :
                line = file.readline()
            maliste.append(line)
            while (line != '') & (line != '<!-- End text definitions -->\n') :                   
                line = file.readline()
                maliste.append(line)
        bodyHTML_liste[filename] = maliste
    return bodyHTML_liste


def get_value (chaine) :
    if chaine != '\n' :
        div_value = chaine.split('>')
        if len(div_value) > 1 :
            return div_value[1].strip(' </div>\n')
    return "br"

def get_id (chaine) :
    if 'id=' in chaine :
        div_id = chaine.split('>')[0].split('id="')[1].split('" ')[0]
        if div_id[len(div_id)-1] == '"' :
            div_id = div_id[:-1]
        return div_id
    else :
        return "id=not_found"

def get_class (chaine) :
    if 'class=' in chaine :
        div_class = chaine.split('>')[0].split('class=')[1].split(' ')[1]
        return div_class
    else :
        return "class=not_found"

def create_div_tuple (line, page_id_dict) :
    div_value = get_value(line)
    div_id = get_id(line)
    div_class = get_class(line)
    left = get_left(div_id, page_id_dict)
    bottom = get_bottom(div_id, page_id_dict)
    return ((div_value, div_id, div_class, left, bottom ))



############################################################################
####                        Table extraction functions
############################################################################


def coordinates_contains (coordinates, div_bottom, div_left) :  
    if div_bottom < coordinates["first_point"]["bottom"] and div_bottom > coordinates["last_point"]["bottom"] and div_left > coordinates["first_point"]["left"]  and div_left < coordinates["last_point"]["left"] :
        return True
    else :
        return False


def find_ids_with_coordinates (coordinates, page_id_dict) : 
    table__ids_list = []
    for div_id in page_id_dict :
        div_bottom = get_integer_px (get_bottom(div_id,page_id_dict ))
        div_left = get_integer_px (get_left(div_id,page_id_dict ))
        if coordinates_contains (coordinates, div_bottom, div_left) :
            table__ids_list.append(div_id)
    return table__ids_list     


def find_line(id_recherche, bodyHTML) :
    r = len(bodyHTML)-2
    for line_number in range(1, r):
        line = bodyHTML[line_number]
        div_id = get_id(line)
        if (id_recherche == div_id) :
            return line
    return "not found"



def create_tuples_list (table_ids_list, bodyHTML, page_id_dict) :
    tuples_list = []
    for div_id in table_ids_list :
        line = find_line(div_id, bodyHTML)
        t = create_div_tuple (line, page_id_dict)
        tuples_list.append(t)
    return tuples_list


def find_columns_and_lines_coordinates (tuples_list) :
    table_column_list = []
    table_lines_list = []
    for t in tuples_list : 
        table_column_list.append(arrondi(t[3],100))
    for t in tuples_list : 
        table_lines_list.append(arrondi(t[4],1))

    col = list(set(table_column_list))
    lin = list(set(table_lines_list))
    list.sort(col)
    list.sort(lin)
    list.reverse(lin)

    return col.copy(), lin.copy()

def arrondi (chainepx, ordre) :
    return (int(get_integer_px(chainepx)/ordre) * ordre) 


def affiche_tuples_only_lines (tuples_list) :
    tuples_copy = []
    for tup in tuples_list :
        value = tup[0]
        bottom = tup[4]
        tuples_copy.append((bottom, value))


def arrondir_pixels (tuples_list) :
    arrondi_tuples_list = []
    for tu in tuples_list :
        new_tu = (tu[0], tu[1], tu[2], arrondi(tu[3], 100), arrondi(tu[4], 1))
        arrondi_tuples_list.append(new_tu)
    return arrondi_tuples_list


def create_empty_lines_dict(lines) :
    empty_lines_dict = {}

    for dim in lines :
        empty_lines_dict [dim] = []   
    return empty_lines_dict


def create_table_content (arrondi_tuples_list, lines) :
    empty_lines_dict = create_empty_lines_dict(lines)
    for tu in arrondi_tuples_list : 
        empty_lines_dict[tu[4]].append(tu[0])
    tablelines_list = []
    for l in empty_lines_dict :
        tablelines_list.append(empty_lines_dict[l])
    return tablelines_list


def extract_table_content (coordinates, page_name, headerHTML, bodyHTML) :

    page_id_dict = create_id_dictionnary (page_name, headerHTML)

    table_ids_list = find_ids_with_coordinates (coordinates, page_id_dict)
    tuples_list = create_tuples_list(table_ids_list, bodyHTML, page_id_dict)
    affiche_tuples_only_lines (tuples_list) 
    
    columns, lines = find_columns_and_lines_coordinates (tuples_list)

    arrondi_tuples_list = arrondir_pixels (tuples_list)

    tablelines_list = create_table_content (arrondi_tuples_list, lines)
    return tablelines_list


def merge_lines(tablelines_list) :
    merge = []
    for line in tablelines_list :
        for chaine in line :
            merge.append(chaine)
    return merge
            

#######################################################################
####                       Table Reshape table functions
#######################################################################

def create_empty_lines_columns_dict (columns, lines) :
    empty_columns_dict = {}
    empty_lines_columns_dict = {}

    list.reverse(lines)
    
    for dim in columns :
        empty_columns_dict [dim] = []

    for dim in lines :
        empty_lines_columns_dict [dim] = empty_columns_dict 
    return empty_lines_columns_dict


def group_by_line_and_column (arrondi_tuples_list, columns, lines ) :
    lines_columns_dict = {}
    for tu in arrondi_tuples_list :
        value = tu[0]
        left = tu[3]
        bottom = tu[4]
        
        if bottom in lines_columns_dict.keys() :
            if left in lines_columns_dict[bottom].keys():
                lines_columns_dict[bottom][left].append(value)
            else :
                lines_columns_dict[bottom][left] = [value]
        else :
            lines_columns_dict[bottom] = {}
            lines_columns_dict[bottom][left] = [value]

    return lines_columns_dict


def add_white_cases () :
    pass


def create_table_with_columns (arrondi_tuples_list, columns, lines) :
    empty_lines_columns_dict = create_empty_lines_columns_dict(columns, lines)
    for l in empty_lines_columns_dict :
        for dim in empty_lines_columns_dict[l] :
            for tu in arrondi_tuples_list : 

                empty_lines_columns_dict[tu[4]][tu[3]].append(tu[0])

    tablelines_list = []  
    for l in empty_lines_columns_dict :
        tableline = []
        for dim in empty_lines_columns_dict[l] :
            column = empty_lines_columns_dict[l][dim].copy()
            tableline.append(column)
        tablelines_list.append(tableline)
    return tablelines_list


def extract_table_with_columns (coordinates, page_name,  bodyHTML_liste,  headerHTML_liste) :

    bodyHTML = bodyHTML_liste[page_name]
    header_HTML = headerHTML_liste[page_name]
    page_id_dict = create_id_dictionnary (page_name, headerHTML)

    table_ids_list = find_ids_with_coordinates (coordinates, page_id_dict)
    
    tuples_list = create_tuples_list(table_ids_list, bodyHTML, page_id_dict)
    affiche_tuples_only_lines (tuples_list)
    arrondi_tuples_list = arrondir_pixels (tuples_list)
    affiche_tuples_only_lines (arrondi_tuples_list)
    
    columns, lines = find_columns_and_lines_coordinates (arrondi_tuples_list)

    table = create_table_with_columns (arrondi_tuples_list, columns, lines)
    return table 



def group_by_line_and_column (arrondi_tuples_list, columns, lines ) :
    empty_lines_columns_dict = {}
    for tu in arrondi_tuples_list :
        value = tu[0]
        left = tu[3]
        bottom = tu[4]
        
        if bottom in empty_lines_columns_dict.keys() :
            if left in empty_lines_columns_dict[bottom].keys():
                empty_lines_columns_dict[bottom][left].append(value)
            else:
                empty_lines_columns_dict[bottom][left] = [value]
        else:
            empty_lines_columns_dict[bottom] = {}
            empty_lines_columns_dict[bottom][left] = [value]



def group_by_line_and_column2 (arrondi_tuples_list) :
    empty_lines_columns_dict = {}
    for tu in arrondi_tuples_list : 
        v = tu[0]
        l = tu[4]
        c = tu[3]
        empty_lines_columns_dict[l][c].append(v)


#################################################################################
##                                     Main
#################################################################################

def make_pixels_dict(coordinates_csv_filename, delta_csv_filename,output_dir_coordinates_buildvu_filename ):


#########################################################################
    #####           Load and read GIMP coordinates points
    #########################################################################

    points_df_gimp = pd.read_csv(coordinates_csv_filename, sep=",")
    points_dict_gimp = points_df_gimp.transpose().to_dict()


    #########################################################################
    #####           Conversion from gimp points to camelot points
    #########################################################################
    delta_x, delta_y  =  get_gimp_camelot_delta(None ,None,delta_csv_filename)

    points_dict_camelot = {}
    for index in points_dict_gimp :
        Xmin_gimp =  points_dict_gimp[index]['xmin']
        Ymin_gimp =  points_dict_gimp[index]['ymin']
        width =  points_dict_gimp[index]['width']
        height =  points_dict_gimp[index]['height'] 
        [Xmin_cam, Ymin_cam, Xmax_cam, Ymax_cam] = getAreas_pt(Xmin_gimp, Ymin_gimp, width, height, delta_x, delta_y).split(',')
        points_dict_camelot[index] = {}
        points_dict_camelot[index]['Xmin'] = int(Xmin_cam)
        points_dict_camelot[index]['Xmax'] = int(Xmax_cam)
        points_dict_camelot[index]['Ymin'] = int(Ymin_cam)
        points_dict_camelot[index]['Ymax'] = int(Ymax_cam)
        points_dict_camelot[index]['page'] = points_dict_gimp[index]['page'][:-4]
        points_dict_camelot[index]['tab'] = '0'
        points_dict_camelot[index]['table_id'] = points_dict_camelot[index]['page'] + '.'+ points_dict_camelot[index]['tab']+'.'
        points_dict_camelot[index]['nameHTML'] = points_dict_gimp[index]['page'][:-3] + "html"

    #########################################################################
    #####           Conversion from camelot points to buildvu pixels
    #########################################################################

    pixels_dict = {}
    points_dict = points_dict_camelot
    sorted_keys = (list(points_dict_camelot.keys()))
    list.sort(sorted_keys)
    for index in sorted_keys :
        points = [points_dict[index]["Xmin"], points_dict[index]["Ymin"], points_dict[index]["Xmax"], points_dict[index]["Ymax"] ]
        table_id = points_dict[index]["table_id"][:-1]
        if table_id in pixels_dict.keys() :
            while table_id in pixels_dict.keys():
                [page,  table] = table_id.split('.')
                t = int(table)
                t += 1
                table_id = page + "." + str(t)
        pixels = point_to_pixel_dic (points)
        pixels_dict [table_id] = {}
        pixels_dict [table_id]['coordinates'] = pixels
        pixels_dict [table_id]['table_id'] = table_id
        pixels_dict [table_id]['nameHTML'] = points_dict[index]['nameHTML']
        pixels_dict [table_id]['table'] = points_dict[index]['tab']
        pixels_dict [table_id]['page'] = points_dict[index]['page']

    save_json (pixels_dict, output_dir_coordinates_buildvu_filename)










def make_extract_for_test(coordinates_csv_filename, delta_csv_filename, buildvu_html_path, output_dir_html_tables, output_dir_coordinates_buildvu_filename):

    #########################################################################
    #####           Recuperer les tuples du html
    #########################################################################
    make_pixels_dict(coordinates_csv_filename, delta_csv_filename, output_dir_coordinates_buildvu_filename)
    pixels_dict = read_json(output_dir_coordinates_buildvu_filename)
    #print(pixels_dict.keys())
    filename_liste = []
    for table_id in pixels_dict :
        filename = pixels_dict[table_id]['nameHTML']
        filename_liste.append(filename) 
    filename_set = set(filename_liste)
    filename_liste = list(filename_set)
    list.sort(filename_liste)


    headerHTML_liste = {}
    headerHTML_liste = read_header_html_files (filename_liste, buildvu_html_path)


    bodyHTML_liste = {}
    bodyHTML_liste = read_html_files_to_body_list (bodyHTML_liste, filename_liste, buildvu_html_path)

    #########################################################################
    #####                     Extraction des tableaux page par page dans un dictionnaire
    #########################################################################
    tables_content_dict = pixels_dict.copy()


    for table_id in tables_content_dict :
        coordinates = tables_content_dict[table_id]['coordinates']
        fileHTML = tables_content_dict [table_id]['nameHTML']
        bodyHTML = bodyHTML_liste[fileHTML]
        headerHTML = headerHTML_liste[fileHTML]
        table_content = extract_table_content (coordinates, fileHTML, headerHTML, bodyHTML) 

        tables_content_dict[table_id]['table_body'] = table_content






    save_json (tables_content_dict, output_dir_html_tables)




