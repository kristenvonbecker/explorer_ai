import pandas as pd
import re
from unidecode import unidecode


apos_pattern = r"(\w+)(\s)*'S "
paren_pattern = r"(\((?!born).+?\)),? "
plural_pattern = r"(plural .+?), "
alias_pattern = r"(?:also called|also spelled) (.+?), "
cat_pattern = r"(?!in full)(?:in|In) (.+?), (?:or (.+?), (.+?), )?"
aka_pattern = r"(?:Latin in full|in full|byname of|original name) (.+?), "
bd_pattern = r"\(born (\w+ \d{1,2}, \d{4})(?:, )(.*?)(?:—died (\w+ \d{1,2}, \d{4})(?:, )(.*?))?\), "
x_sp_pattern = r"\s{2,}"
sp_punc_pattern = r"\s+([.,\:\-])"


def clean_par_0(paragraph, title, decode=False):
    title = title.strip(" ,")  # strip commas and extra whitespace from titles
    title = title.replace(u"\u2019", "'")  # replace unicode single smart quote in title
    paragraph = paragraph.replace(u"\u2019", "'").strip()  # replace unicode single smart quote in text

    # remove extra spaces
    x_space = re.search(x_sp_pattern, paragraph)
    if x_space:
        paragraph = re.sub(x_space.group(0), " ", paragraph)

    # remove spaces before punctuation
    paragraph = re.sub(r"\s+([.,\:\-])", r"\1", paragraph)

    # unidecode text
    if decode:
        title = unidecode(title)
        paragraph = unidecode(paragraph)

    # convert title to title-case
    title_split = title.split()
    if len(title_split) > 1:
        title_tc = ' '.join([title_split[0].title()] + title_split[1:])
    else:
        title_tc = title.title()

    # convert format of beginning of text; e.g.
    # "expert system, a computer program..." is converted to "Expert system: a computer program..."
    title_comma = re.escape(title) + r"(\s)*,(\s)*"
    title_colon = title_tc + ": "
    paragraph = re.sub(title_comma, title_colon, paragraph)

    prefix = title_colon
    contents = []

    # convert Prisoner'S or Prisoner 'S to Prisoner's
    apos_title = re.search(apos_pattern, title)
    if apos_title:
        title = title.replace(apos_title.group(0), apos_title.group(1) + "'s")
    apos_text = re.search(apos_pattern, paragraph)
    if apos_text:
        paragraph = paragraph.replace(apos_text.group(0), apos_text.group(1) + "'s")

    # collect parenthetical information and format nicely
    # Q: loop this to check for more than one paren group?
    paren_info = re.search(re.escape(prefix) + paren_pattern, paragraph)
    if paren_info:
        contents.append(paren_info.group(1).strip("()"))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(paren_info.group(0), prefix, 1)

    plural = re.search(re.escape(prefix) + plural_pattern, paragraph)
    if plural:
        contents.append(plural.group(1))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(plural.group(0), prefix, 1)

    alias_name = re.search(re.escape(prefix) + alias_pattern, paragraph)
    if alias_name:
        contents.append("or " + alias_name.group(1).strip())
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(alias_name.group(0), prefix, 1)
        aliases = [x.strip() for x in alias_name.group(1).split(" or ")]
    else:
        aliases = []

    category = re.search(re.escape(prefix) + cat_pattern, paragraph)
    if category:
        if category.group(3):
            cat_name = category.group(1) + "/" + category.group(2) + " " + category.group(3)
            contents.append("in " + cat_name)
        else:
            cat_name = category.group(1)
            contents.append("in " + cat_name)
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(category.group(0), prefix, 1)
        grouping = [x.strip() for x in cat_name.split(" and ")]
    else:
        grouping = []

    aka_name = re.search(re.escape(prefix) + aka_pattern, paragraph)
    if aka_name:
        contents.append("aka " + aka_name.group(1))
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(aka_name.group(0), prefix, 1)

    birth_death = re.search(re.escape(prefix) + bd_pattern, paragraph)
    if birth_death:
        contents.append("born " + birth_death.group(1) + " in " + birth_death.group(2))
        if birth_death.group(3):
            contents.append("died " + birth_death.group(3) + " in " + birth_death.group(4))
            is_person = 2
        else:
            is_person = 1
        paren = "(" + "; ".join(contents) + ")"
        prefix = " ".join([title_tc, paren]) + ": "
        paragraph = paragraph.replace(birth_death.group(0), prefix, 1)
    else:
        is_person = 0

    title_paren_pattern = r"\(.+?\)"
    title_paren_text = re.search(title_paren_pattern, title)
    if title_paren_text:
        title = title.replace(title_paren_text.group(0), '').strip()

    return paragraph, title, aliases, grouping, is_person


def clean_par_n(paragraph, decode=False):
    paragraph = paragraph.replace(u"\u2019", "'").strip()  # replace unicode single smart quote in text

    # remove extra spaces
    x_space = re.search(x_sp_pattern, paragraph)
    if x_space:
        paragraph = re.sub(x_space.group(0), " ", paragraph)

    # remove spaces before punctuation
    paragraph = re.sub(r"\s+([.,\:\-])", r"\1", paragraph)

    # unidecode text
    if decode:
        paragraph = unidecode(paragraph)

    # convert Prisoner'S or Prisoner 'S to Prisoner's
    apos_text = re.search(apos_pattern, paragraph)
    if apos_text:
        paragraph = paragraph.replace(apos_text.group(0), apos_text.group(1) + "'s")

    return paragraph
