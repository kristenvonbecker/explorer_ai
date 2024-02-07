import os
import json
from fuzzywuzzy import fuzz, process
import random


# proj_home = os.getenv("PROJ_HOME")
proj_home = '/Users/vonbecker/ML_Bootcamp_code/Capstone/explorer_ai'
exhibits_filepath = os.path.join(proj_home, "modeling/rasa/actions/knowledgebase/institutional/exhibits.json")

with open(exhibits_filepath, "r") as f:
    exhibits = json.load(f)

exhibit_ids = [exhibit["id"] for exhibit in exhibits]  # what is this for?

name_aliases = []
alias_id_lookup = {}

for exhibit in exhibits:
    exhibit["aliases"].insert(0, exhibit["title"])
    name_aliases += exhibit["aliases"]
    if exhibit["id"] in alias_id_lookup.keys():
        alias_id_lookup[exhibit["id"]] += exhibit["aliases"]
    else:
        alias_id_lookup.update({
            exhibit["id"]: exhibit["aliases"]
        })


def get_exhibit_alias_matches(alias, threshold=75, scorer=fuzz.WRatio):
    matches = process.extract(alias, name_aliases, scorer=scorer, limit=3)
    matches.sort(key=lambda item: item[1], reverse=True)
    good_matches = [match for (match, score) in matches if score >= threshold]
    return good_matches


def get_exhibit_ids(alias):
    ids = []
    for exhibit_id, aliases in alias_id_lookup.items():
        if alias in aliases:
            ids.append(exhibit_id)
    return ids


def get_exhibit_name(exhibit_id):
    exhibit_name = alias_id_lookup[exhibit_id][0]
    return exhibit_name


location_dict = {
    "Gallery 1": "Bernard and Barbro Osher Gallery 1: Human Phenomena",
    "Gallery 2": "Gallery 2: Tinkering",
    "Gallery 3": "Bechtel Gallery 3: Seeing & Reflections",
    "Gallery 4": "Gordon and Betty Moore Gallery 4: Living Systems",
    "Gallery 5": "Gallery 5: Outdoor Exhibits",
    "Gallery 6": "Fisher Bay Observatory Gallery 6: Observing Landscapes",
    "Entrance": "the Exploratorium entrance",
    "Crossroads": "Crossroads: Getting Started",
    "Bay Walk": "the Koret Foundation Bay Walk",
    "Plaza": "the Plaza",
    "Atrium": "the Ray and Dagmar Dolby Atrium",
    "Jetty": "the San Francisco Marina Jetty",
    "NOT ON VIEW": "NOT ON VIEW"
}


def get_exhibit_location(exhibit_id):
    location_code = [exhibit["location"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    location = location_dict.get(location_code)
    return location, location_code


def get_exhibit_creator(exhibit_id):
    names = [exhibit["creators"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    return names


def get_exhibit_date(exhibit_id):
    year = [exhibit["year"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    return year


def get_about_exhibit(exhibit_id):
    short_sum = [exhibit["short-summary"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    medium_sum = [exhibit["medium-summary"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    fun_facts = [exhibit["fun-facts"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    return short_sum, medium_sum, fun_facts


def get_related_exhibit(exhibit_id):
    related_ids = [exhibit["related_exhibits"] for exhibit in exhibits if exhibit["id"] == exhibit_id][0]
    return related_ids


def get_fave_exhibit():
    rand_id = random.choice(exhibit_ids)
    rand_exhibit = [exhibit["title"] for exhibit in exhibits if exhibit["id"] == rand_id][0]
    fun_facts = []
    for exhibit in exhibits:
        if exhibit["id"] == rand_id:
            fun_facts += exhibit["fun-facts"]
    if fun_facts:
        rand_fun_fact = random.choice(fun_facts)
    else:
        rand_fun_fact = None
    return rand_id, rand_exhibit, rand_fun_fact
