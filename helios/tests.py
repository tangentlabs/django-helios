import unittest

from .utils import escape_query


class Quoting(unittest.TestCase):

    def test_query_quoting(self):
        orig_to_escaped = [('+', '\+'),
                           (' -', ' \-'),
                           ('++ +-- -+ ---', '\++ \+-- \-+ \---'),
                           ('+-', '\+-'),
                           ('+ aaa', '\+ aaa'),
                           ('aaa +', 'aaa \+'),
                           ('+aaa -aaa', '+aaa -aaa'),
                           ('{', '\{'),
                           (' {', ' \{'),
                           ('{!', '\{!'),
                           (' {!', ' \{!'),
                           ('{! aaa', '\{! aaa'),
                           ('aaa+ bbb+', 'aaa+ bbb+'),
                           ('AND', 'and'),
                           ('OR', 'or'),
                           ('||', '\||'),
                           ('|||', '|||'),
                           (' || |', ' \|| \|'),
                           ('&&', '\&&'),
                           ('&&&', '&&&'),
                           ('&& &', '\&& \&')]

        for orig, escaped in orig_to_escaped:
            self.assertEquals(escape_query(orig), escaped)
