# Nice to have when needing to extract parts of a JSON file as a dict

import sys
from pprint import pprint
from tests.util import jsonfile_to_dict

pprint(jsonfile_to_dict(sys.argv[1]))