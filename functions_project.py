import re
from textblob import TextBlob

def my_map(function_to_apply, list_of_inputs):
    """
    Traverses a list, apply some function to each of the elements and collects the output.
    """
    
    new_list = []
    for i in list_of_inputs:
        new_list.append(function_to_apply(i))
        
    return new_list

def map_cleaned_strings(dfname, columnname):
    """
    Maps new values in a df-column. From a new created dictionary, with as Key the 'old' string value and 
    as Value the 'new'-string value. The 'new'-string values are extracted with the function convert_word().
    """
    dict_old_new = {}
    for i in dfname[columnname]:
        if type(i) != str:
            continue
        else:
            dict_old_new[i] = convert_word(i)

    dfname[columnname] = dfname[columnname].map(dict_old_new)
    
    return dfname[columnname]

def convert_word(word):
    """
    Strips a word from all punctuation, whitespace, and digits. Then converts the word into all lower case
    and convert all characters with accents to non-accent letters.
    """
    word = re.sub(r'[^\w\s]','',word).lower()
    word = re.sub(r'[àáâãäå]', 'a', word)
    word = re.sub(r'[èéêë]', 'e', word)
    word = re.sub(r'[ìíîï]', 'i', word)
    word = re.sub(r'[òóôõö]', 'o', word)
    word = re.sub(r'[ùúûü]', 'u', word)
    
    return word


