import re
from pydantic import ConstrainedStr

class CprNo(ConstrainedStr):
    regex = re.compile(r"^\d{10}$")
