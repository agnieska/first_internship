
from pprint import pprint
import pandas as pd
import json
import time
import datetime
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter,TextConverter, XMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io


def read_json (filename) :
    with open(filename, encoding='utf-8') as file:
        summary_dict = json.load(file)
    return summary_dict  

def save_json (summary_dict, filename) :
    if not filename :
        filename = "myjson.json"
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(summary_dict, file)


#############################################################################
####                    Mapping between Pages et Chapters
#############################################################################


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
    
    #pprint(chapter_dict)
    #pprint(subchapter_dict)
    return chapter_dict, subchapter_dict




def create_maps (pdf_pagelist, chapter_dict, subchapter_dict) :
    chapter_page_map = {}
    subchapter_page_map = {}
    pprint('print parameter pagelist')
    pprint(pdf_pagelist)
    pprint('print empty chapter_page_map')
    pprint(chapter_page_map)
    pprint('print empty subchapter_page_map')
    pprint(subchapter_page_map)
    
    for page in pdf_pagelist :
        pprint('for page in pagelist print page')
        pprint(page)
        chapter_page_map[page] = '0.0'
        subchapter_page_map[page] = []
    
    pprint('print chapter_page_map')
    pprint(chapter_page_map)
    pprint('print subchapter_page_map')
    pprint(subchapter_page_map)
    
    for chapter_number in chapter_dict :
        pprint('print chapter_number')
        pprint(chapter_number)
        pages = chapter_dict[chapter_number]['Pagelist']
        pprint('print pages')
        pprint(pages)
        for page in pages :
            pprint('for page in pages print page')
            pprint(page)
            if page < max(pdf_pagelist) :
                #chapter_page_map[page] = chapter_dict[chapter_number]['Id']
                chapter_page_map[page] = chapter_number
        
    for subchapter_number in subchapter_dict :
        pages = subchapter_dict[subchapter_number]['Pagelist']
        for page in pages :
            if page < max(pdf_pagelist) :
                #subchapter_page_map[page].append(subchapter_dict[subchapter_number]['Id'])
                subchapter_page_map[page].append(subchapter_number)
    
    #pprint(subchapter_page_map[10])
    #pprint(chapter_page_map[10])
    return chapter_page_map, subchapter_page_map 



###############################################################################
####              Read pdf file and convert to list of text bodys
###############################################################################

def convert_to_text(case, input_fname, output_fname, pages=None):
       
    reader = open(input_fname, 'rb')
    manager = PDFResourceManager()
    output_stream = io.StringIO()
    converter = TextConverter(manager, output_stream, codec='utf-8', laparams=LAParams())   
    interpreter = PDFPageInterpreter(manager, converter)  
    
    if not pages: page_nums_set = set();
    else: page_nums_set = set(pages); 
    pages_pdf_selection = PDFPage.get_pages(reader, page_nums_set, caching=True, check_extractable=True)
    
    for page in pages_pdf_selection:
        interpreter.process_page(page)
    
    converted_text_page = output_stream.getvalue()
    """
    if case == 'text' : 
        writer = open(output_fname, "w")
    if case == 'HTML' : 
        writer = open(output_fname, "wb")
    writer.write(converted_text_page);
    """  
    reader.close(); converter.close(); output_stream.close(); #writer.close();
    return converted_text_page



#########################################################################################
####       Create json files containing text body and indexes for each pdf page
#########################################################################################

def create_final_dict (pdf_pagelist, chapter_dict, subchapter_dict, chapter_page_map, subchapter_page_map, bodyTXT_liste, publication_date, indexation_date) :
    final_dict = {}
    for i in pdf_pagelist :
        pprint("page numero : " + str(i))
        dict_key = str(chapter_page_map[i])
        pprint("type : "+ str(type(dict_key)))
        pprint("chapter_page_map[i] : " + str(chapter_page_map[i]))
        
        chapter_title = chapter_dict[dict_key]['Title']
        pprint("chapter  title  :" + str(chapter_title))
        chapter_id = chapter_dict[dict_key]['Id']
        pprint("chapter id : " + str(chapter_id))
        
        pprint("subchapter_page_map[i] :" + str(subchapter_page_map[i])) 
        subchapter_keys_liste = subchapter_page_map[i]
        pprint("subchapter keys_liste : " + str(subchapter_keys_liste))
        
        subchapter_ids = []
        subchapter_titles = []
        sisters = []
        for n in subchapter_keys_liste :
            subchapter_ids.append(subchapter_dict[n]['Id'])
            subchapter_titles.append(subchapter_dict[n]['Title'])
            sisters = subchapter_dict[n]['Pagelist']
        pprint("subchapter ids : " + str(subchapter_ids))
        pprint("subchapter titles : " + str(subchapter_titles))
        
        
        final_dict[i+1] = { 'body':bodyTXT_liste[i],  
                           'chapter_title': chapter_title, 
                           'chapter_num': chapter_id, 
                           'subchapter_title' : subchapter_titles, 
                           'subchapter_num' : subchapter_ids , 
                           "pdf_page" : i+1,
                           "html_id" : str(i+1) + ".html",
                           "html_class" : "",
                           "sisters" : sisters,
                           "document_title" : "Raport annuel societe generale 2018",
                           "document_id" : 1,
                           "chronology": i,
                           "indexation_date": str(indexation_date),
                           "publication_date": str(publication_date)
          }

    return final_dict

def create_files_json (final_dict) :
    for page_number in final_dict :
        page_dict = final_dict[page_number]
        pprint(page_dict)
        filename = "json_html_files/bv_page"+ str(page_number) + ".json"
        #filename = "json_text_files/page"+ str(page_number) + ".json"
        pprint(filename)
        with open(filename, mode='w', encoding='utf-8') as file:
            json.dump(page_dict, file)
       # writer = open(filename, 'utf-8', "w")
       # writer.write (json_stream)
       # writer.close()



###############################################################################
####              Main
###############################################################################

def _main ():
    filename = "summary.json"
    summary_dict = read_json (filename)
    if summary_dict != None :
        pprint("summary json has been loaded with " + str(len(summary_dict)) + " items")
        chapter_dict, subchapter_dict = split_summary_dict (summary_dict)
        save_json (chapter_dict, 'chapters.json')
        pprint("chapters json has been saved ")
        save_json (subchapter_dict,'subchapters.json')
        pprint("subchapters json has been saved ")
        
        # mapping pages : chapters
        pdf_pagelist = list(range(0, 568))
        chapter_page_map, subchapter_page_map = create_maps (pdf_pagelist, chapter_dict, subchapter_dict)
        bodyTXT_liste = []
        ### si le fichier "body" existe (conversion prealable)
        #filename = "body_all_text.json"
        #bodyTXT_liste = read_json (filename)
        
        ## extraction du pdf

        filePDF = "rapport_sg.pdf" # input 
        for page in pdf_pagelist : 
            li = [page]
            bodyTXT = convert_to_text('text', filePDF, None , pages=li)
            bodyTXT_liste.append(bodyTXT)
        pprint("body list has been created with " + str(len(bodyTXT_liste)) + " items")
        
        ### sauvegarder pour reutiliser apres
        #save_json (bodyTXT_liste, filename='body_all_text.json')
        #pprint("saved body_all_text.json")
        
        indexation_date = datetime.date.today()
        indexation_date = datetime.datetime.strftime(indexation_date, "%d/%m/%Y")
        publication_date = datetime.date(2018,6,30)
        publication_date = datetime.datetime.strftime(publication_date, "%d/%m/%Y")
        final_dict = create_final_dict (pdf_pagelist, chapter_dict, subchapter_dict, chapter_page_map, subchapter_page_map, bodyTXT_liste, publication_date, indexation_date)
        create_files_json (final_dict)
    else : 
        pprint ("problem with loading summary.json file")
