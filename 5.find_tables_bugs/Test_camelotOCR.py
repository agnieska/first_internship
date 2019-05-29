

import json
from pprint import pprint
import pathlib 



################################################################
###                 Functions                                ###
################################################################

def save_json (dictionnary, filename) :
    with open(filename, mode='w', encoding='utf-8') as file:
        json.dump(dictionnary, file)

def read_json (filename) :
    with open(filename, mode='r', encoding='utf-8') as file:
        return json.load(file)  

def is_numeric(chaine) :
    if chaine == '' :
        return 0
    if chaine == '\n' :
        return 0
    if chaine == '-' :
        return 0

    desired = ['0','1','2','3','4','5','6','7','8','9',' ',',','%','(',')','-', '.']
    for c in chaine :
        if c not in desired :
            return 0
    if is_date(chaine) :
        return 2
    return 1

def is_date (chaine) :
    deux_points = len([c for c in chaine if c == '.'])
    deux_slash = len([c for c in chaine if c == '/'])
    deux_tires = len([c for c in chaine if c == '-'])
    annees = ['2015','2016', '2017', '2018', '2019', '2020']
    has_year = False
    for annee in annees :
        if annee in chaine :
            has_year = True
    if (deux_points == 2 or deux_slash == 2 or deux_tires == 2) and (has_year == True) :
        return True
    else :
        return False

def count_slash_n(item) :
    counter = 0
    for lettre in str(item) :
        if lettre == '\n':
            counter += 1
    return counter

def merge_lines(tablelines_list) :
    merge = []
    for line in tablelines_list :
        for chaine in line :
            merge.append(chaine.strip(' '))
    return merge

################################################################
###           Read and prepare camelot data to compare       ###
################################################################

def read_and_prepare_camelot (camelot_json_filename):    
    camelot_json = read_json(camelot_json_filename)
    camelot_tables_list = [camelot_json[item]['pdf_page'] for item in camelot_json]

    camelot_dict = {}
    for item in camelot_json :
        table_id = camelot_json[item]['pdf_page']
        camelot_dict[table_id] = {}
        camelot_dict[table_id]['table_id'] = table_id 
        tablelines = camelot_json[item]['data']
        camelot_dict[table_id]['table_body'] = merge_lines(tablelines)
    

    return camelot_dict, camelot_tables_list

#################################################################
###           Read and prepare buildvu data to compare        ###
#################################################################

def read_and_prepare_buildvu (buildvu_json_filename) :
    buildvu_json = read_json(buildvu_json_filename)

    buildvu_dict = {}
    for item in buildvu_json :
        table_id = buildvu_json[item]['table_id']
        buildvu_dict[table_id] = {}
        buildvu_dict[table_id]['table_id'] = table_id 
        tablelines = buildvu_json[item]['table_body']
        buildvu_dict[table_id]['table_body'] = merge_lines(tablelines) #tablelines
             
    buildvu_tables_list = list(buildvu_dict.keys())

    
    return buildvu_dict, buildvu_tables_list 

##################################################################
####                Test1: compare the lists of tables         ###
##################################################################

def compare_tables_lists (camelot_tables_list, buildvu_tables_list ) :
    result = True
    #print("Test1 : Comparing the names of tables between buildvu and camelot")
    c = len(camelot_tables_list)
    b = len (buildvu_tables_list)
    tables_camelot_str = (" " + str(c) + " tables found ")
    tables_buildvu_str = (" " + str(b) + " tables found ")
    
    if c != b :
        result = False
    else : 
        list.sort(camelot_tables_list)
        list.sort(buildvu_tables_list)
        i = 0
        j = 0
        while i < c and j < b :
            if camelot_tables_list[i] < buildvu_tables_list[j] :
                #print ("camelot table " + camelot_tables_list[j] + " not found in buildvu ")
                i += 1
                result = False
            elif camelot_tables_list[i] > buildvu_tables_list[j] :
                #print ("buildvu table "+ buildvu_tables_list[j] + " not found in camelot")
                j += 1
                result = False
            else :
                #print("  found table  " + camelot_tables_list[i])
                i += 1
                j += 1
    
    #result_str = "tables are equals : " + str(result)
    
    #print( tables_camelot_str + tables_buildvu_str + result)
    return tables_camelot_str, tables_buildvu_str, result

###########################################################################################
###                       Remove false positifs
###########################################################################################
def remove_false_positifs (test_results_dict, table_id, counter_ko, counter_ok, counter_ko_texte, counter_ko_numeric) :

        # test_results_dict = read_json("../test/test_results.json") :

        table = table_id
        textes = test_results_dict[table]['not_found']['textes']
        #print(textes)
        numeric = test_results_dict[table]['not_found']['numeric']
        to_much = test_results_dict[table]['to_much']
        #print(to_much)
        i = 0  
        while i < len(textes) :
            chaine1 = textes[i]
            #print("textes : " + chaine1)
            #print(type(chaine1))
            j = 0 
            found = False
            while j < len(to_much) and found == False :
                chaine2 = to_much[j]
                #print("to_much : " + chaine2)
                #print(type(chaine2))
                if "\n" not in chaine2 and chaine1 in chaine2 :
                    #print("is in ")
                    ch = chaine2.replace(chaine1, "")
                    #print("after replace : " + ch)
                    found = True
                    counter_ko_texte -= 1
                    counter_ko -= 1 
                    counter_ok += 1
                    to_much[j] = ch
                    textes[i] = ""
                else :
                    #print("is not in")
                    j = j + 1
            i = i + 1  
        i = 0  
        while i < len(numeric) :
            chaine1 = numeric[i]
            #print("textes : " + chaine1)
            #print(type(chaine1))
            j = 0 
            found = False
            while j < len(to_much) and found == False :
                chaine2 = to_much[j]
                #print("to_much : " + chaine2)
                #print(type(chaine2))
                if "\n" not in chaine2 and chaine1 in chaine2 and chaine1 in ['1', '2', '3', '4', '(1)', "(2)", '(3)']  :
                    #print("is in ")
                    ch = chaine2.replace(chaine1, "")
                    #print("after replace : " + ch)
                    found = True
                    counter_ko_numeric -= 1
                    counter_ko -= 1 
                    counter_ok += 1
                    to_much[j] = ch
                    numeric[i] = ""
                else :
                    #print("is not in")
                    j = j + 1
            i = i + 1 
        
        return test_results_dict, counter_ko, counter_ok, counter_ko_texte, counter_ko_numeric
    
#################################################################################################
###      Test 2 : Taking an element from buildvu div and searching in camelot table           ###
#################################################################################################

def compare_divs (camelot_dict, buildvu_dict) :
    #print("Test2 : Taking an element from html table (buildvu) and trying to find it in excel table (camelot) \n")
    table_ko = 0
    table_ok = 0
    test_results_dict = {}
    test_scores_list = []
    for table_id in buildvu_dict :
        counter_ko = 0
        counter_ok = 0
        counter_ko_numeric = 0
        counter_ko_texte = 0
        counter_ko_date = 0
        test_results_dict[table_id] = {}
        test_results_dict[table_id]['not_found'] = {'numeric' : [], 'textes' : [], 'dates' : []}
        data_b = buildvu_dict[table_id]['table_body'].copy()
        data_c = camelot_dict[table_id]['table_body'].copy()


        if len(data_b)>0 :
            for chaine in data_b :
                if chaine in data_c :
                    counter_ok += 1
                    data_c.remove(chaine)
                else :

                    if is_numeric(chaine) == 1 :
                        ch = str(chaine).replace(" ","")
                        if ch in data_c :
                            counter_ok += 1
                            data_c.remove(ch)
                        else :
                            counter_ko += 1
                            counter_ko_numeric += 1
                            test_results_dict[table_id]['not_found']['numeric'].append(chaine)
                    elif is_numeric(chaine) == 2 :
                        counter_ko += 1
                        counter_ko_date += 1
                        test_results_dict[table_id]['not_found']['dates'].append(chaine)
                    else :
                        counter_ko += 1
                        counter_ko_texte += 1
                        test_results_dict[table_id]['not_found']['textes'].append(chaine)

            test_results_dict[table_id]['to_much'] = [item for item in data_c if item != ""]
            test_remained = test_results_dict[table_id]['to_much']
            counter_remained = len(test_remained)
            concat = 0
            for item in test_remained :
                slash = count_slash_n(str(item))
                if slash > 0 :
                    concat = concat + slash + 1
            
            #print("\nTest 3 : Remove false positifs \n")
            test_results_dict, counter_ko, counter_ok, counter_ko_texte, counter_ko_numeric = remove_false_positifs (test_results_dict, table_id, counter_ko, counter_ok, counter_ko_texte, counter_ko_numeric)
            
            if counter_ko > 0 :
                table_ko += 1
            else :
                table_ok += 1

            table_score = int(counter_ko / (counter_ok + counter_ko) * 100)
            test_results_dict[table_id]['error_score'] = table_score
            
            #print("table " + table_id + "   not found : " + str(table_score) + "%" + "  numbers: " + str(counter_ko_numeric) + "" + "  textes: " + str(counter_ko_texte)+ "" + "   dates: " + str(counter_ko_date)+ " remained : " + str(counter_remained) + " merged: "+ str(concat))
            test_scores_list.append("table " + table_id + "   not found : " + str(table_score) + "%" + "  numbers: " + str(counter_ko_numeric) + "" + "  textes: " + str(counter_ko_texte)+ "" + "   dates: " + str(counter_ko_date)+ " remained : " + str(counter_remained) + " merged: "+ str(concat))
        else :
            test_scores_list.append("table " + table_id  + "  est vide ")
            #print("table " + table_id  + "  est vide ")

    #print("total bad tables : " + str(table_ko))
    #print(" total good tables : " + str(table_ok))
    good_tables_str = str(table_ok)
    bad_tables_str =  str(table_ko)
    return test_scores_list, test_results_dict, good_tables_str, bad_tables_str
    



#####################################################################################
###                                    Main                                       ###    
#####################################################################################

def make_test (camelot_json_filename, buildvu_json_filename, test_scores_filename, test_details_filename) :
    
    # Load and prepare to compare
    camelot_dict, camelot_tables_list = read_and_prepare_camelot (camelot_json_filename)
    buildvu_dict, buildvu_tables_list = read_and_prepare_buildvu (buildvu_json_filename)
    
    # Test 1
    tables_camelot_str, tables_buildvu_str, result_bool = compare_tables_lists (camelot_tables_list, buildvu_tables_list ) 
    #print("All tables found = " +str(result))
    
    # Test2
    test_scores_list, test_details_dict, good_tables_str, bad_tables_str = compare_divs (camelot_dict, buildvu_dict)
    
    # Save results
    save_json(test_scores_list, test_scores_filename)
    save_json(test_details_dict, test_details_filename)
    
    return tables_camelot_str, tables_buildvu_str, result_bool, good_tables_str, bad_tables_str
    

#make_test ("../test/camelot_tables.json", "../test/buildvu_tables.json", "../test/test_scores.json", "../test/test_details.json")





