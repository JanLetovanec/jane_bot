""" Helper library for grammar functionality """
from requests_html import HTMLSession

"""
Polls https://en.oxforddictionaries.com/definition/ ...
for results
"""

# global variable, caches reasults
cache = {}


class Entry:
    """
    Holds Parsed ALL info about a word
    """
    def __init__(self):
        self.subEntries = []
        self.phrases = []
        self.phrasalVerbs = []

    def parse_window(self, site):
        if self.get_bad_result(site) is not None:
            return self.get_bad_result(site)
        self.parse_definition_section(site)
        self.parse_phrases_section(site)
        self.parse_p_verbs(site)
        return None

    def parse_definition_section(self, site):
        pos_parts = site.html.find("section.gramb", first=False)
        for posPart in pos_parts:
            pos = posPart.find(".pos", first=True).text
            sub_entry_elems = posPart.find(".semb > li", first=False)

            for element in sub_entry_elems:
                sub_entry = SubEntry()
                sub_entry.parse_sub_entry(pos, element)
                self.subEntries.append(sub_entry)

    def parse_phrases_section(self, site):
        phrases_section = site.html.find("section.etymology", first=True)
        if phrases_section is None:
            print("Missing phrases")
            return
        titles = phrases_section.find("ul > li > div > p > span.ind > .phrase")
        bodies = phrases_section.find("ul > ul.semb")

        for index in range(0, len(titles)):
            if (index >= len(titles)) or (index >= len(bodies)):
                print("Inconsistent phrases")
                break
            phrase = Phrase()
            phrase.parse_phrase(titles[index], bodies[index])
            self.phrases.append(phrase)

    def parse_p_verbs(self, site):
        phrases_section = site.html.find("section.etymology")
        if len(phrases_section) < 2:
            print("Missing phrasal verb section")
            return

        pv_section = phrases_section[1]
        pv_titles = pv_section.find("ul.gramb > li.phrase_sense")
        pv_bodies = pv_section.find("ul.gramb > ul.semb")
        if len(pv_titles) != len(pv_bodies):
            print("Inconsistent phrasal verbs")
            return

        for index in range(0, len(pv_titles)):
            pv = PhrasalVerbs()
            pv.parse_pv(pv_titles[index], pv_bodies[index])
            self.phrasalVerbs.append(pv)

    def get_bad_result(self, site):
        result = []
        similar_list = site.html.find(".search-results", first=True)
        if similar_list is None:
            return None
        else:
            similar_list = similar_list.find("li > a", first=False)
            for element in similar_list:
                result.append(element.text)
        return result


class SubEntry:
    """
    Holds parsed info about 1 meaning of word
    """

    def __init__(self):
        self.pos = ""
        self.definition = ""
        self.synonyms = []
        self.examples = []
        self.subEntries = []

    def parse_sub_entry(self, pos, element):
        self.pos = pos

        definition = element.find("span.ind", first=True)
        if definition is not None:
            self.definition = definition.text

        for example in element.find(".ex"):
            self.examples.append(example.text)

        synonyms = element.find(".synonyms > div.exg", first=True)
        if synonyms is not None:
            synonyms = synonyms.find(".exs")
            for synonym_group in synonyms:
                self.synonyms += synonym_group.text.split(",")

        sub_entries = element.find("ol.subSenses > li.subSense")
        for s_entry in sub_entries:
            new_entry = SubEntry()
            new_entry.parse_sub_entry(pos, s_entry)
            self.subEntries.append(new_entry)


class Phrase:
    """
    Holds info about a phrase
    """
    def __init__(self):
        self.title = ""
        self.definition = ""
        self.examples = []
        self.synonyms = []

    def parse_phrase(self, title, body):
        definition_part = body.find("div.trg > p", first=True)
        examples_part = body.find(".ex")
        if (title is None) or (body is None):
            return None
        self.title = title.text
        self.definition = definition_part.text
        for example in examples_part:
            self.examples.append(example.text)


class PhrasalVerbs:
    """
    Holds info about verbs
    """
    def __init__(self):
        self.title = ""
        self.subPVerbs = []

    def parse_pv(self, title, body):
        self.title = title.text
        meanings = body.find("li.phrase_sense")
        for meaning in meanings:
            pv_meaning = SubPhrasalVerb()
            pv_meaning.parse_main(meaning)
            self.subPVerbs.append(pv_meaning)


class SubPhrasalVerb:
    def __init__(self):
        self.definition = ""
        self.examples = []
        self.synonyms = []
        self.subPVerbs = []

    def parse_main(self, body):
        definition = body.find("div.trg > p > span.ind", first=True)
        if definition is None:
            print("Missing phrasal verb definition")
            return
        self.definition = definition.text

        main_example = body.find("li > div.trg > div.exg > div.ex", first=True)
        examples = body.find("li > div.trg > div.examples > div > ul > li.ex")
        if main_example is not None:
            self.examples.append(main_example.text)
        for ex in examples:
            self.examples.append(ex.text)

        synonyms = body.find("li > div.trg > div.synonyms > div.exg > div.exs")
        for syn in synonyms:
            self.synonyms += syn.text.split(",")

        sub_senses = body.find("li > div.trg > ol.subSenses > li.subSense")
        for sub_pb in sub_senses:
            spv = SubPhrasalVerb()
            spv.parse_sub(sub_pb)
            self.subPVerbs.append(spv)

    def parse_sub(self, body):
        definition = body.find("span.ind", first=True)
        if definition is None:
            print("Missing phrasal verb definition")
            return
        self.definition = definition.text

        main_example = body.find("li > div.exg > div.ex", first=True)
        examples = body.find("li > div.examples > div > ul > li.ex")
        if main_example is not None:
            self.examples.append(main_example.text)
        for ex in examples:
            self.examples.append(ex.text)

        synonyms = body.find("li > div.synonyms > div.exg > div.exs")
        for syn in synonyms:
            self.synonyms += syn.text.split(",")


def cache_clear():
    global cache
    cache = {}


def cache_add(word, entry):
    global cache
    cache[word] = entry


def get_entry(word):
    """ Gets all definitions for a given word """
    global cache
    if word in cache.keys():
        return cache[word], None

    site = get_window(word)
    if site is None:
        print("HTTP error")
        return
    e = Entry()
    error = e.parse_window(site)
    if error is not None:
        return e, error
    cache_add(word, e)
    return e, None


def get_window(word):
    session = HTMLSession()
    url = 'https://en.oxforddictionaries.com/definition/' + word
    site = session.get(url)
    return site


def bad_spelling(word, error):
    string = "I am sorry, but it seems I do not recognise: " + word + ".\n"
    string += "Did you mean one of these:\n"
    string += "```"
    for w in error:
        string += w + "\n"
    string += "```"
    return string


""" Printers and getters """


def sub_print(sub_entry, index, sub_index):
    pos = sub_entry.pos
    definition = sub_entry.definition
    if len(sub_entry.examples) >= 1:
        example = sub_entry.examples[0]
    else:
        example = ""
    synonyms = sub_entry.synonyms

    string = ""
    string += "\t{}.{}. - ({}) {}\n".format(index, sub_index, pos, definition)
    string += "\tExample: {}\n".format(example)
    string += "\tSynonyms: {}\n".format(", ".join(synonyms))
    return string


def pprint_definitions(entry):
    strings = []
    sub_entries = entry.subEntries
    for index in range(1, len(sub_entries) + 1):
        string = ""
        ent = sub_entries[index - 1]
        pos = ent.pos
        definition = ent.definition
        if len(ent.examples) >= 1:
            example = ent.examples[0]
        else:
            example = ""
        synonyms = ent.synonyms
        subs = ent.subEntries

        string += "```\n"
        string += "{}. ({}) - {}\n".format(index, pos, definition)
        string += "Example: {}\n".format(example)
        string += "Synonyms: {}\n".format(", ".join(synonyms))
        for sub_index in range(1, len(subs) + 1):
            string += sub_print(subs[sub_index - 1], index, sub_index)
        string += "```\n"
        strings.append(string)
    return strings


def print_phrases(entry):
    strings = []
    for phrase in entry.phrases:
        string = "```"
        string += "{}\n".format(phrase.title)
        if len(phrase.examples) >= 1:
            string += "Example: {}\n".format(phrase.examples[0])
        else:
            string += "Example: \n"
        string += "Synonyms: {}\n".format(", ".join(phrase.synonyms))
        string += "```"
        strings.append(string)
    return strings


""" API """


def serve(word, option="def"):
    print("Polling:", word, option)
    e, err = get_entry(word)
    if err is not None:
        return [bad_spelling(word, err)]
    print("Lookup: cached - ", word, option)

    if option == "def":
        strings = pprint_definitions(e)
    elif option == "phrase":
        strings = print_phrases(e)
    elif option == "clear":
        cache_clear()
        print("Lookup: cache cleared")
        strings = ["Ok, memory cleared."]
    else:
        print("Lookup: bad options")
        strings = ["I am sorry, I do not quite get, what you want.\n",
                   "Valid options are: def, phrase, pv, clear"]

    return strings
