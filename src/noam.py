import argparse
from lexer import lexer
import sys

def setup_parser():
    parse = argparse.ArgumentParser(description='Does Lexical Analysis\
                                    and breaks the code down into tokens')
    parse.add_argument('--html_cfg', dest='config_file_location',\
                        help='Location of the json config file', required=False)
    parse.add_argument('--out_html', dest='out_html_location',\
                        help='Location of the output html file', required=False)
    parse.add_argument('--out_dot', dest='out_dot_location',\
                        help='Location of the output dot file', required=True)                   
    parse.add_argument('--input', dest='in_file_location',\
                       help='Location of the input go file', required=True)
    return parse



parser = setup_parser()
res    = parser.parse_args()

html_config  = str(res.config_file_location)
output_html  = str(res.out_html_location)
output_dot   = str(res.out_dot_location)
input_file   = str(res.in_file_location)

if html_config == 'None':
    html_config = 'config/html_config/color3.json'

if output_html == 'None':
    output_html = 'bin/default_html'

if output_dot == 'None':
    output_dot = 'bin/default_dot'


# call lexer
lexer.Lexer(html_config, input_file, output_html)
