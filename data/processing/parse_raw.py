import re


# parse the aliases field into a list
def parse_aliases(text):
    list = text.split(",")
    while "" in list:
        list.remove("")
    return list


# Define exhibit location codes
def get_location_code(location):
    if location == 'This exhibit is not currently on view.':
        return 'NOT ON VIEW'
    elif 'Gallery' in location:
        for n in range(6):
            code = str(n)
            if 'Gallery ' + code in location:
                if 'Mezzanine' in location:
                    return 'Gallery ' + code + ' (Mezzanine)'
                elif 'Black Box' in location:
                    return 'Gallery ' + code + ' (Black Box)'
                elif 'Wattis Studio' in location:
                    return 'Gallery ' + code + ' (Studio)'
                else:
                    return 'Gallery ' + code
    elif 'Entrance' in location:
        return 'Entrance'
    elif 'Crossroads' in location:
        return 'Crossroads'
    elif 'Plaza' in location:
        return 'Plaza'
    elif 'Atrium' in location:
        return 'Atrium'
    elif 'Bay Walk' in location:
        return 'Bay Walk'
    elif 'jetty' in location.lower():
        return 'Jetty'


# Regex pattern for CSS? language drop-down element in description field
has_lang_settings = r"\.btn-language(.+)Language(\s+Español)?(\s+繁體中文)?(\s+Filipino)?"


def remove_lang_settings(text):
    lang_settings = re.match(has_lang_settings, text, flags=re.DOTALL)
    if lang_settings:
        proc_text = re.sub(lang_settings.group(0), "", text).strip()
    else:
        proc_text = text
    return proc_text


