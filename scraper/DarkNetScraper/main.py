from DarkNetScraper.parsers.string_parsers import parse_depth
from .output.colors import ColoredText
import argparse, sys
from . import version
from .parsers.verifier import validate_link
from .binder import Binder
from .config import CONFIG_IP, CONFIG_PORT

# DarkNetScraper CLI class
class DarkNetScraper:
    binder = None
    collection = None

    def __init__(self, args):
        self.args = args
        self.get_header()
        if args.version:
            print("DarkNetScraper Version: " + version.__version__)
            sys.exit()
        self.binder = Binder(ip=args.ip, port=args.port, args=args)


    def get_header(self):
        license_msg = ColoredText("LICENSE: GNU Public License v3", "red")
        banner = r"""
                    ██████╗  █████╗ ██████╗ ██╗  ██╗███╗   ██╗███████╗████████╗
                    ██╔══██╗██╔══██╗██╔══██╗██║ ██╔╝████╗  ██║██╔════╝╚══██╔══╝
                    ██║  ██║███████║██████╔╝█████╔╝ ██╔██╗ ██║█████╗     ██║   
                    ██║  ██║██╔══██║██╔══██╗██╔═██╗ ██║╚██╗██║██╔══╝     ██║   
                    ██████╔╝██║  ██║██║  ██║██║  ██╗██║ ╚████║███████╗   ██║   
                    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   
                                                                               
                    ███████╗ ██████╗██████╗  █████╗ ██████╗ ███████╗██████╗    
                    ██╔════╝██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗   
                    ███████╗██║     ██████╔╝███████║██████╔╝█████╗  ██████╔╝   
                    ╚════██║██║     ██╔══██╗██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗   
                    ███████║╚██████╗██║  ██║██║  ██║██║     ███████╗██║  ██║   
                    ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝   V{VERSION}
                                                           """.format(VERSION=version.__version__)
        banner = ColoredText(banner, "red")

        title = r"""
                                        {banner}
                        #######################################################
                        #  DarkNetScraper - Dark Web Scraper                  #
                        #  Author - swhiteh4t                                 #
                        #  Help : use -h for help text                        #
                        #######################################################
                                    {license_msg}
                """

        title = title.format(license_msg=license_msg, banner=banner)
        print(title)

    def run(self):
        args = self.args
        # If url flag is set then check for accompanying flag set. Only one
        # additional flag can be set with -u/--url flag
        if validate_link(args.url):
            self.binder.run(parse_depth(args.depth), url=args.url)
        else:
            print("usage: Use the -h flag for information of the usage.")
            sys.exit(1)
        print("\n\n")
    
    def stop(self):
        self.binder.stop()

def get_arguments():
    """
    Parses user flags passed to DarkNetScraper
    """
    parser = argparse.ArgumentParser(prog="DarkNetScraper", description="Crawl and inspect the content of Tor pages")
    parser.add_argument("--version", action="store_true", help="Show current version of DarkNetScraper")
    #parser.add_argument("--update", action="store_true", help="Pulls the lastest version from github")
    #parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("-u", "--url", help="Specify a website link to crawl")
    parser.add_argument("-s", "--save", action="store_true", help="Save results in a file")
    parser.add_argument("-m", "--mail", action="store_true", help="Get e-mail addresses from the crawled sites") 
    parser.add_argument("-t", "--telephone", action="store_true", help="Get phone numbers from the crawled sites")
    parser.add_argument("-a","--additional", action="store_true", help="Get crypto address & aws domains")
    parser.add_argument("-d","--depth", help="Specify max depth of crawler (default 1)", default=1)
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows more output info.")
    parser.add_argument("-c", "--classify", action="store_true", help="Manually label each crawled page (dataset building mode).")
    parser.add_argument("--ip", default=CONFIG_IP, help="IP of the Tor SOCKS proxy (default %(default)s)")
    parser.add_argument("--port", type=int, default=CONFIG_PORT, help="Port of the Tor SOCKS proxy (default %(default)s)")
    parser.add_argument("-p","--predict", action="store_true", help="Predict the page category with the fine-tuned BERT model.")
    #parser.add_argument(
    #    "-cs", "--classifyshow", action="store_true", help="Classify and show statistics of the obtained webpages using NLP module"
    #)
    parser.add_argument("-anon", "--anonimity", action="store_true", help="Sets a random user agent and new circuit for each request.")
    #To be done integrate with VPN/ProxyChains
    return parser.parse_args()


if __name__ == '__main__':
    try:
        args = get_arguments()
        dark_scraper = DarkNetScraper(args)
        dark_scraper.run()
        dark_scraper.stop()
    except KeyboardInterrupt:
        print("Interrupt received! Exiting cleanly...")
