from .colors import ColoredText
from ..parsers.parser import Parser


def print_generic(data=None, key=None):
    keys = {
        'email' : 'Emails',
        'crypto' : 'Crypto',
        'ip4' : 'IPv4',
        'ip6' : 'IPv6',
        'cloud': 'Cloud domains',
        'phone': 'Phone Numbers'
    }
    if key in keys:
        print(ColoredText("[ * ] " + keys[key], 'green'))
        if len(data) > 0:
            for v in data:
                print(ColoredText("[ - ] " + v, 'white'))
        else: 
            print(ColoredText("[ - ] No " + keys[key] + " found ", 'white'))
        print("\n")

def handle_response_code(code):
    if code >= 300 and code < 400:
        print(ColoredText("[ - ] Moved to a new location", 'white'))
    elif code == 404:
        print(ColoredText("[ - ] Requested site not found", 'red'))
    elif code == 401:
        print(ColoredText("[ - ] Unauthorized", 'red'))
    elif code == 400:
        print(ColoredText("[ - ] Bad request", 'red'))
    else:
        print(ColoredText("[ - ] Request failed", 'red'))
    print(ColoredText("[ - ] Status code: " + str(code), 'white'))

    '''Helper funcitons'''
def print_phone(parser):
    print_generic(key='phone', data=parser.get_phone_numbers())
    
def print_mail(parser):
    print_generic(key='email', data=parser.get_emails())
    
def print_summary(parser):
    summary = parser.get_sumary(0.15)
    print(ColoredText(summary,'darkmagenta'))
    return len(summary) < 10

def print_metaatr(meta):
    print(ColoredText("[ - ] Meta tags",'magenta'))
    print(ColoredText("[ - ] " + Parser.get_meta(meta)+"\n",'magenta'))
def print_additonal( p : Parser):
    keys = ['ip4' ,'ip6' ,'cloud', 'crypto']
    ip4,ip6,cloud,crypto = p.get_additional()
    values = [ip4 ,ip6,cloud,crypto]
    for key,value in zip(keys,values):
        print_generic(key=key,data=value)   
def print_content(p: Parser):
    print(ColoredText(p.content,'darkmagenta'))
    
def resolve_categorize(i):
    categories = {
    "0": "Empty",
    "1" : "Pornography",
    "2" : "Bitcoin related services",
    "3" : "Drugs",
    "4" : "Violence",
    "5" : "C. Credit Cards",
    "6" : "C. Money",
    "7" : "C. Personal",
    "8" : "Piracy",
    "9" : "Hacking",
    "10" : "Malware",
    "11" : "Ilegal Marketplace",
    "12" : "Services",
    "14" : "Fraud",
    "15" : "Human-Trafficking",
    "16" : "Leaked documents",
    "17" : "Directory/Wiki",
    "18" : "Art & Music",
    "19" : "Casino & Gambling",
    "20" : "Privacy",
    "21" : "Cryptocurrency",
    "22" : "Forum",
    "23" : "Marketplace",
    "24" : "Library & Books",
    "25" : "Journalism",
    "26" : "Personal",
    "27" : "Politics",
    "28" : "Religion",
    "29" : "Hosting & Software"}
    return categories.get(str(i).strip(), "Empty")

def print_prediction(probabilities,predicted_class,predicted_label,label_resolver):
    # Print the results
    # Print the results in a table format
    print(ColoredText("Category   |    Probability",'cyan'))
    print(ColoredText("-----------|----------------",'cyan'))
    for category_id, category_label in label_resolver.items():
        probability_percentage = probabilities[category_id] * 100
        percentage = "{:.2f}".format(probability_percentage)
        print(ColoredText(f"{category_label:11}|     {percentage}",'cyan'))
    print("\n[ * ] Predicted label:", predicted_label)
