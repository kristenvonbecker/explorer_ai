import re
from nltk.tokenize import sent_tokenize


# PROCESSING TEXT RESPONSES FROM PRE-TRAINED MODELS

# Define regex patterns for parsing OpenAI completion responses

# text begins with a fragment
frag_start = r"^([a-z][^\n]*)"

# pattern for itemization by -hash marks, - hash marks plus space, 3. enumeration
# ending in a newline or EOF
item_pattern = r"(- *|\d. )?(.*?)(\n)*(?:$|\n)"

# pattern for non-alphanumeric tokens
non_alphanum = r"\W+"


# Check whether a string is composed of only non-alphanum chars
def is_non_alphanum(text):
    match = re.match(non_alphanum, text)
    if match:
        return True if match.group(0) == text else False
    else:
        return False


# Remove fragment start from a response
def remove_frag_start(text):
    proc_text = re.sub(frag_start, "", text).strip()
    return proc_text


# Find items in a response which forms a list or collection
def find_items(text, short=True):
    if short:
        item_list = text.split(",")
    else:
        item_list = [text]
    item_list = [item.strip() for item in item_list if item and not is_non_alphanum(item)]
    item_list_rev = []
    for item in item_list:
        sub_items = re.findall(item_pattern, item)
        sub_items = [x[1] for x in sub_items if x[1]]
        sents = sent_tokenize(item)
        if len(sub_items) > 1:
            item_list_rev += [sub_item[1] for sub_item in sub_items]
        elif len(sents) > 1 and not short:
            item_list_rev += [sent for sent in sents]
        else:
            item_list_rev.append(item)
    item_list = [item.strip() for item in item_list_rev if item]
    item_list = [item for item in item_list if not is_non_alphanum(item)]
    if short:
        item_list = [item for item in item_list if len(item) < 30]
    return item_list


# Process exhibit keywords
def process_keywords(existing_list, new_list):
    proc_list = existing_list + new_list
    proc_list = [x.lower() for x in proc_list]
    proc_list = list(set(proc_list))
    return proc_list


# Parse byline entities into creators and years
def get_creators(entities):
    creators = [entity["name"] for entity in entities if entity["type"] == "PERSON"]
    return creators


def get_year(entities):
    years = [entity["name"] for entity in entities if entity["type"] in ["DATE", "NUMBER"]]
    year = int(years[0]) if years else None
    return year
