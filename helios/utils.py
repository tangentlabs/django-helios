import re


def quote(val):
    '''
    Quote a value for safe usage with Solr
    '''
    if isinstance(val, (str, unicode)):
        val = val.replace('\\', u'\\\\').replace('"', '\\"')
        return u'"%s"' % (val,)
    else:
        return unicode(val)


def escape_query(query):
    '''
    Quote query to play nice with Solr query parser.
    '''
    reg = r'''(^ ([+-]+? | {!?) (?=\s|$) |
               (?<=\s) ([+-]+? | {!?) (?=\s|$))'''
    return re.sub(reg, r'\\\g<0>', query.lower(), flags=re.VERBOSE)


class OneOf(object):
    '''
    Will match any of the provided values.

        (val1 OR val2 OR ...)
    '''
    def __init__(self, *values):
        self.values = values

    def __unicode__(self):
        return u'(%s)' % (u' OR '.join(quote(v) for v in self.values))


class AllOf(object):
    '''
    Will only match if all of the provided values match

        (val1 AND val2 AND ...)
    '''
    def __init__(self, *values):
        self.values = values

    def __unicode__(self):
        return u'(%s)' % (u' AND '.join(quote(v) for v in self.values))


class InRange(object):
    '''
    Will match a range
    '''
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def __unicode__(self):
        return u'[%s TO %s]' % (self.start, self.stop)
