def quote(val):
    '''
    Quote a value for safe usage with Solr
    '''
    if isinstance(val, (str, unicode)):
        val = val.replace('\\', u'\\\\').replace('"', '\\"')
        return u'"%s"' % (val,)
    else:
        return unicode(val)


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
