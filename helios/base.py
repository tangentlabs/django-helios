

class DisMaxConfig(object):
    def __init__(self, qf, pf, bq=None, bf=None, ps=None, qs=None, mm='2<-25%', tie='0.1'):
        self.qf = qf
        self.pf = pf
        self.mm = mm
        self.ps = ps
        self.qs = qs
        self.tie = tie
        self.bq = bq
        self.bf = bf

    def get_qf(self):
        return ' '.join(['%s^%s' % (x[0], x[1]) for x in self.qf])

    def get_pf(self):
        return ' '.join(['%s^%s' % (x[0], x[1]) for x in self.pf])


class Searcher(object):

    def __init__(self, **kwargs):
        self.connection = kwargs.pop('connection')

    def get_search_params(self, **kwargs):
        print kwargs


        filters = kwargs.pop('filters', [])
        facets = kwargs.pop('facets', [])
        offset = kwargs.pop('offset', 0)
        rows = kwargs.pop('rows', 10)
        sort = kwargs.pop('sort', None)

        params = {}

        for filter in filters:
            fqs = params.get('fq', [])
            query = '%s:%s' % (filter[0], filter[1])
            fqs.append(query)

        for facet in facets:
            params['facet'] = 'true'
            params.get('facet.field', []).append(facet.final_query_field())
            params['f.%s.sort' % facet.field] = facet.sort
            params['f.%s.limit' % facet.field] = facet.limit
            params['f.%s.offset' % facet.field] = facet.offset
            params['f.%s.mincount' % facet.field] = facet.mincount
            params['f.%s.missing' % facet.field] = facet.missing

        params['rows'] = rows
        params['start'] = offset

        if sort:
            params['sort'] = sort

        return params

    def search(self, **kwargs):
        q = kwargs.pop('q', '*:*')

        results = self.connection.search(q, **self.get_search_params(**kwargs))



        return self.connection.search(q, **self.get_search_params(**kwargs))

    def new_query(self):
        return Query(self)


class DisMaxSearcher(Searcher):

    def __init__(self, **kwargs):
        self.config = kwargs.pop('config')
        super(DisMaxSearcher, self).__init__(**kwargs)

    def get_search_params(self, **kwargs):
        params = super(DisMaxSearcher, self).get_search_params(**kwargs)

        params.update({
            'defType': 'dismax',
            'qf': self.config.get_qf(),
            'pf': self.config.get_pf(),
            'mm': self.config.mm,
            'tie': self.config.tie,
        })
        return params


class Query(object):
    def __init__(self, searcher):
        self.searcher = searcher
        self.filters = []
        self.facets = []
        self.sorts = []
        self.q = '*:*'
        self.start = 0
        self.end = 10

    def set_limits(self, start, end):
        self.start = start
        self.end = end

    def add_filter(self, field, value):
        self.filters.append((field, value))

    def add_facet(self, facet):
        self.facets.append(facet)

    def add_sort(self, field):
        direction = 'asc'

        if field[0] == '-':
            direction = 'desc'
            field = field[1:]
        self.sorts.append((field, direction))

    def set_q(self, q):
        self.q = q

    def run(self):
        sort = ', '.join(['%s %s' % (x[0], x[1]) for x in self.sorts])

        kwargs = {
            'q': self.q,
            'facets': self.facets,
            'filters': self.filters,
            'offset': self.start,
            'rows': self.end - self.start
        }

        if sort:
            kwargs['sort'] = sort

        return self.searcher.search(**kwargs)