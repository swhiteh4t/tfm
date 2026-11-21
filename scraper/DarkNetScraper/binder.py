from DarkNetScraper.nlp.darkbert import DarkBert
from DarkNetScraper.output.printer import print_phone, print_additonal, print_mail, print_metaatr, print_summary, print_content, resolve_categorize
from .torconnector import TorConnector
from .extractors.extractor import Extractor
from .parsers.parser import Parser
from .output.colors import ColoredText
from .datamodels import DBConnector
from .config import CONFIG_IP,CONFIG_PORT
import os,json, random

class Binder:
    connector = None
    args = None
    visited = None

    def __init__(self,ip=CONFIG_IP,port=CONFIG_PORT,args=args):
        self.args = args
        random_agent = True if args.anonimity else False
        self.connector  = TorConnector(ip=ip, port=port, random_agent=random_agent)
        self.connector.renew_tor_identity()
        #Show IP
        if args.verbose:
            print(ColoredText("[ * ] Initating the database ", 'blue'))
            #TODO: Implement the graphs
            self.connector.check_my_ip()
        self.db = DBConnector()
        if os.path.exists('visited.json'):
            self.visited = set(json.loads(open('visited.json').read()))
        else:
            self.visited = set() #Load the set
        if args.predict:
            self.bert = DarkBert()

    def run(self, depth, url=None):
        if depth <= 0 or url is None or url in self.visited:
            return
        
        print(ColoredText("[ * ] Making request to " + url,"white"))
        html = self.connector.query(url=url)
        self.visited.add(url)

        if html is None:
            return 
        e = Extractor(html=html)
        e.extract_do_all()
        print(ColoredText("[ - ] Title : " +e.title,'magenta'))
        p = Parser(e.content_raw)
        if self.args.verbose:
            print_metaatr(e.meta)
            if print_summary(p):
                print_content(p)
        #Renew the identity in each request
        if self.args.anonimity or random.randint(1,10) % 10 == 0:
            self.connector.renew_tor_identity()
            if self.args.verbose:
                self.connector.check_my_ip()
        if self.args.mail:
            print_mail(p)
        if self.args.telephone:
            print_phone(p)
        if self.args.additional:
            print_additonal(p)
        if self.args.predict:
            self.bert.predict(p.content)
        
        #Save to database
        #self.db.save_to_file()
        if self.args.classify:
            inp = input(ColoredText("[ ! ] Introduce the category : ",'cyan'))
            category = resolve_categorize(inp)
            if category != "Empty":
                print(ColoredText("Categorized as "+category,'cyan'))
                self.db.add_entry_generate(
                    title=Parser.remove_non_alphanum(e.title),
                    content=p.content,
                    category=category

          )
        else:
            self.db.add_entry(
            title=Parser.remove_non_alphanum(e.title),
            content=p.content,
            category="", #Trained model response
            summary="" #Trained model response
            )
        #Traverse other links recursive
        for link in e.links:
            self.run(depth=int(depth)-1,url=link)
        #Proccess with machine learning
    

    def stop(self):
        print(ColoredText("[ * ] Commiting changes to the Database...",'blue'))
        if self.args.classify:
            self.db.save_to_file()
        with open('visited.json', 'w') as file:
            file.write(json.dumps(self.visited, cls=SetEncoder))
        self.db.save_db()

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
