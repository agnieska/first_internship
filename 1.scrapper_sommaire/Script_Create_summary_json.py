import numpy
import pandas as pd
from pprint import pprint
import json

################################################################################
#### Read Save
################################################################################

def save_json (mydict, filename) :
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(mydict, file)

def read_json (filename) :
    with open(filename, encoding='utf-8') as file:
        summary_dict = json.load(file)
    return summary_dict

def read_csv_convert_todictionnary(csv_filename) :
    df=pd.read_csv(csv_filename)
    rows_count = df.shape[0]
    return df.T.to_dict(), rows_count

def read_summarycsv_convert_todictionnary(csv_filename) :
    df=pd.read_csv(csv_filename)
    df['Last_Page'] = 0
    df['Type'][61] = 'CHAPTER'
    df['Chapter_number'][61] = 10
    df['Section_number'][61] = 0
    rows_count = df.shape[0]
    return df.T.to_dict(), rows_count

########################################################################################
#####              Enrichissement du sommmaire (id, pagelist, parent, child)
########################################################################################

def calcul_last_page (summary_dict, rows_count):
    i = 0
    while i < rows_count-1 : 
        if summary_dict[i]['Type'] == 'SUB-CHAPTER' :
            #pprint("subchapter : i =" + str(i))
            summary_dict[i]['Last_Page'] = summary_dict[i+1]['Page']-1
            if summary_dict[i]['Last_Page'] < summary_dict[i]['Page'] :
                summary_dict[i]['Last_Page'] = summary_dict[i]['Page']
        else :
            #pprint("chapter : i =" + str(i))
            j = i+1
            while summary_dict[j]['Type'] =='SUB-CHAPTER' :
                j = j + 1
            #pprint("j= " + str(j))
            summary_dict[i]['Last_Page'] = summary_dict[j]['Page']-1
        i = i + 1
        summary_dict[rows_count-1]['Last_Page'] = 568
    return summary_dict

def calcul_pagelist (summary_dict, rows_count) :   
    for item in summary_dict :
        summary_dict[item]['Pagelist'] = []
    for item in summary_dict :
        summary_dict[item]['Pagelist'] = list(range(summary_dict[item]['Page'], summary_dict[item]['Last_Page']+1))  
    return summary_dict


def create_id (summary_dict, rows_count) :
    for item in summary_dict : 
        summary_dict[item]['Id'] = ""
    for item in summary_dict : 
        summary_dict[item]['Id'] = str(summary_dict[item]['Chapter_number']) + "."+ str(summary_dict[item]['Section_number'])
    return summary_dict


def calcul_parent_child (summary_dict, rows_count) :   
    for item in summary_dict :
        summary_dict[item]['Parent'] = None
        summary_dict[item]['Children_ids'] = []
    for item in summary_dict :
        if summary_dict[item]['Type'] == 'SUB-CHAPTER':
            summary_dict[item]['Parent'] = str(float(summary_dict[item]['Chapter_number']))  
    for i in range (0, len(summary_dict)) :
        if summary_dict[i]['Type'] == 'CHAPTER' :
            if i < (len(summary_dict)-1) :
                pprint("chapter i = " + str(i))
                j = i + 1
                while summary_dict[j]['Type'] == 'SUB-CHAPTER' : 
                    pprint("subchapter j = " + str(j))
                    summary_dict[i]['Children_ids'].append(summary_dict[j]['Id'])
                    j = j + 1
    return summary_dict

#################################################################################
#####                   Structure Arbre Parent - Child
#################################################################################

def split_summary_dict (summary_dict) :
    chapter_dict = {} 
    subchapter_dict = {}
    for item in summary_dict :
        if summary_dict[item]['Type'] == 'CHAPTER':
            ch_id = summary_dict[item]['Id']
            chapter_dict[ch_id] = summary_dict[item]
        else :
            sch_id = summary_dict[item]['Id']
            subchapter_dict[sch_id] = summary_dict[item]
    return chapter_dict, subchapter_dict


def create_summary_tree (chapter_dict, subchapter_dict) :
    summary_dict_tree = chapter_dict.copy()
    for chapter in summary_dict_tree :
        pprint("chapter : " + str(chapter))
        children_list = summary_dict_tree[chapter]['Children_ids']
        pprint("children list : " + str(children_list))
        children_dict = {} 
        for child_id in children_list :
            pprint("child id : " + str(child_id))
            for subchapter in subchapter_dict :
                pprint("subchaper : " + str(subchapter))
                if subchapter_dict[subchapter]['Id'] == child_id :
                    pprint("subchapter_dict[subchapter] : " + str(subchapter_dict[subchapter]))
                    cle = subchapter_dict[subchapter]['Id']
                    children_dict[cle] = subchapter_dict[subchapter].copy()
                    pprint("children_dict[subchapter] : " + str(children_dict[cle]))
        pprint("children_dict : " + str(children_dict))
        summary_dict_tree[chapter]['Children_tree'] = children_dict
    return summary_dict_tree




#################################################################################
#####                                Main                              
#################################################################################

def main () :

    # Lecture du csv, conversion en dictionnaire
    csv_filename = "sommaire.csv"
    summary_dict, rows_count = read_summarycsv_convert_todictionnary(csv_filename)

    # Enrichissement du sommaire des notes (id, pagelist, parent, child)
    summary_dict = calcul_last_page (summary_dict, rows_count)
    summary_dict = calcul_pagelist (summary_dict, rows_count)
    summary_dict = create_id (summary_dict, rows_count)
    summary_dict = calcul_parent_child (summary_dict, rows_count)

    # Save summary as flat dataframe
    save_json (summary_dict, 'summary.json')

    # Split summary into Chapters and subchapters
    chapter_dict, subchapter_dict = split_summary_dict (summary_dict)
    
    # Saving Chapters and subchapters
    save_json(chapter_dict, "notes.json")
    save_json(subchapter_dict, "subnotes.json")
    
    
    # Create Parent - child structure for Chapters and subchapters
    summary_dict_tree  = create_summary_tree (chapter_dict, subchapter_dict)
    # Save Parent-Child Structure
    save_json (summary_dict_tree, 'summary_tree.json')

