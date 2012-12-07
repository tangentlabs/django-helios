from .utils import quote, escape_query


class Searcher(object):

    def __init__(self, connection=None, extra=None):
        self.connection = connection
        self.extra = extra or {}

    def get_search_params(self, filters=None, facets=None, offset=0, rows=10,
                          sort=None, fl=None, **kwargs):
        filters = filters or []
        facets = facets or []

        params = {}

        for field, value in filters:
            fqs = params.get('fq', [])
            query = u'%s:%s' % (field, value)
            fqs.append(query.encode('utf-8'))
            params['fq'] = fqs

        if facets:
            params['facet.field'] = []
            params['facet.query'] = []
            params['facet'] = 'true'
            for facet in facets:
                facet.build_params(params)

        params['rows'] = rows
        params['start'] = offset

        if fl:
            params['fl'] = ','.join(fl)

        if sort:
            params['sort'] = sort

        params.update(self.extra)
        params.update(kwargs)

        return params

    def search(self, **kwargs):
        q = kwargs.pop('q', '*:*')
        return self.connection.search(q, **self.get_search_params(**kwargs))

    def new_query(self):
        return Query(self)


class Query(object):

    def __init__(self, searcher):
        self.searcher = searcher
        self.filters = []
        self.facets = []
        self.sorts = []
        self.q = '*:*'
        self.start = 0
        self.end = 10
        self.fl = None

    def set_limits(self, start, end):
        self.start = start
        self.end = end

    def add_filter(self, field, value):
        self.filters.append((field, quote(value)))

    def add_facet(self, facet):
        self.facets.append(facet)

    def add_sort(self, field):
        direction = 'asc'

        if field[0] == '-':
            direction = 'desc'
            field = field[1:]
        self.sorts.append((field, direction))

    def set_q(self, q):
        self.q = escape_query(q)

    def set_fl(self, *fl):
        self.fl = fl

    def run(self, **extra):
        sort = ', '.join(['%s %s' % (x[0], x[1]) for x in self.sorts])

        kwargs = {
            'q': self.q,
            'facets': self.facets,
            'filters': self.filters,
            'offset': self.start,
            'rows': self.end - self.start,
            'fl': self.fl,
        }

        if sort:
            kwargs['sort'] = sort

        if extra:
            kwargs.update(extra)

        return self.searcher.search(**kwargs)
