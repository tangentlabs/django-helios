import requests
from collections import defaultdict
from urlparse import urlsplit, urlunsplit

try:
    import simplejson as json
except ImportError:
    import json


class SolrException(Exception):
    pass


class SolrFacetResult(object):
    def __init__(self, fieldname, results):
        self.fieldname = fieldname
        self.results = results


class SolrResults(object):
    def __init__(self, docs, hits, highlighting=None, facets=None, spellcheck=None, stats=None, qtime=None, debug=None):
        self.docs = docs
        self.hits = hits
        self.highlighting = highlighting or {}
        facets = facets or {}
        self.spellcheck = spellcheck or {}
        self.stats = stats or {}
        self.qtime = qtime
        self.debug = debug or {}

        self.facets = []

        for k, v in facets.get('facet_fields', {}).iteritems():
            pairs = zip(v[0::2], v[1::2])
            self.facets.append(SolrFacetResult(k, pairs))

        facet_queries_buckets = defaultdict(list)

        for k, v in facets.get('facet_queries', {}).iteritems():
            if k.find('{') == 0:
                close_brace = k.find('}')
                k = k[close_brace + 1:]
            fieldname = k[:k.find(':')]
            bucket = k[k.find(':') + 1:]
            facet_queries_buckets[fieldname].append((bucket, v))

        for k, pairs in facet_queries_buckets.iteritems():
            self.facets.append(SolrFacetResult(k, pairs))

    def __len__(self):
        return len(self.docs)

    def __iter__(self):
        return iter(self.docs)


class SolrConnection(object):

    def __init__(self, url, handler='dismax'):
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
        return requests.get(path, params=params)

    def search(self, q, **kwargs):
        params = {'q': q}
        params.update(kwargs)

        response = self._select(params)
        result = response.json
        if not result:
            raise SolrException(response.content) 

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
        pass

    def delete(self, id=None, query=None, queries=None):
        pass

    def commit(self):
        pass

    def optimize(self):
        pass
