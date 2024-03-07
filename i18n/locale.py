import json

language = 'en'
translations = None

def get_text():
    global translations
    with open(f'i18n/{language}.json','r', encoding='utf-8') as fb:
        translations = json.load(fb)

    return translations

def get(key):
    global translations
    if translations is None:
        get_text()
    
    sections = translations
    content = key.split('.')
    for index, option in enumerate(content):
        if option in sections:
            if index == len(content)-1:
                return sections.get(option)
            else:
                sections = sections.get(option)
    return ""