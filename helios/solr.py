import requests
from urlparse import urlsplit, urlunsplit

try:
    import simplejson as json
except ImportError:
    import json


class SolrResults(object):
    def __init__(self, docs, hits, highlighting=None, facets=None, spellcheck=None, stats=None, qtime=None, debug=None):
        self.docs = docs
        self.hits = hits
        self.highlighting = highlighting or {}
        self.facets = facets or {}
        self.spellcheck = spellcheck or {}
        self.stats = stats or {}
        self.qtime = qtime
        self.debug = debug or {}

    def __len__(self):
        return len(self.docs)

    def __iter__(self):
        return iter(self.docs)



class SolrConnection(object):

    def __init__(self, url, handler='dismax'):
        self.session = requests.session()
        self.decoder = json.JSONDecoder()
        self.url = url
        self.handler = handler
        self.scheme, netloc, path, query, fragment = urlsplit(url)
        self.base_url = urlunsplit((self.scheme, netloc, '', '', ''))
        netloc = netloc.split(':')
        self.host = netloc[0]

        if len(netloc) == 1:
            self.host, self.port = netloc[0], None
        else:
            self.host, self.port = netloc[0], int(netloc[1])

    def _select(self, params):
        params['wt'] = 'json'
        path = '%s/select' % self.url
        return self.session.get(path, params=params)


    def search(self, q, **kwargs):
        params = {'q': q}
        params.update(kwargs)

        response = self._select(params)
        result = self.decoder.decode(response.content)

        result_kwargs = {}

        if result.get('debug'):
            result_kwargs['debug'] = result['debug']

        if result.get('highlighting'):
            result_kwargs['highlighting'] = result['highlighting']

        if result.get('facet_counts'):
            result_kwargs['facets'] = result['facet_counts']

        if result.get('spellcheck'):
            result_kwargs['spellcheck'] = result['spellcheck']

        if result.get('stats'):
            result_kwargs['stats'] = result['stats']

        if 'QTime' in result.get('responseHeader', {}):
            result_kwargs['qtime'] = result['responseHeader']['QTime']

        return SolrResults(result['response']['docs'], result['response']['numFound'], **result_kwargs)


    def add(self, docs):
        pass

    def _update(self, message):
        path = '%s/update/' % self.url

    def delete(self, id=None, query=None, queries=None):
        pass

    def commit(self):
        pass

    def optimize(self):
        pass