from helios.forms.fields import MultipleCharField


class FacetResult(object):
    def __init__(self, facet, results, values):
        self.facet = facet
        self.results = results
        self.values = values


class BaseFacet(object):
    def __init__(self, name, **kwargs):
        self.name = name
        self.form_fieldname = kwargs.pop('form_fieldname', None) or self.name.lower()
        self.solr_fieldname = kwargs.pop('solr_fieldname')
        self.multiselect_or = kwargs.pop('multiselect_or', None)
        self.active = []
        self.selected_values = []

    def build_params(self, params):
        return params

    def final_query_field(self):
        index_field = self.solr_fieldname
        if self.multiselect_or:
            index_field = '{!ex=%s}%s' % (self.form_fieldname, index_field)
        return index_field

    def filter_query(self, query):
        if self.selected_values:
            value_str = ' OR '.join([self.transform_form_value(x) for x in self.selected_values])
            query.add_filter('{!tag=%s}%s' % (self.form_fieldname, self.solr_fieldname), '(%s)' % value_str)

    def formfield(self):
        """
        Returns a form field for this facet
        """
        return MultipleCharField(required=False)

    def label_from_value(self, value):
        return value

    def facet_sortkey(self, value):
        return 0

    def transform_form_value(self, value):
        """
        Converts the cleaned form value into a format suitable for Solr's fq parameter
        """
        return '"%s"' % value

    def set_selected_values(self, values):
        self.selected_values = values

    def update(self, facet_results):
        """
        Updates the facet with the results of the search query and form data
        """
        self.values = []

        if facet_results:
            facet_values = sorted(facet_results.results, key=self.facet_sortkey)

            for x in facet_values:
                t = {
                    'label': self.label_from_value(x[0]),
                    'query': x[0],
                    'count': x[1],
                    'selected':  x[0] in self.selected_values,
                    }

                if t['selected']:
                    self.active.append({
                        'value': t['label'],
                        'query': t['query'],
                        })
                self.values.append(t)

            # Deal with any selected facets that fall outside of the selected range
            for x in set(self.selected_values) - set([x[0] for x in facet_values]):
                t = {
                    'label': self.label_from_value(x),
                    'query': x,
                    'count': 1,
                    'selected':  x in self.selected_values,
                    }

                if t['selected']:
                    self.active.append({
                        'value': t['label'],
                        'query': t['query'],
                        })
                self.values.append(t)


    def formfield_name(self):
        return None

    def facet_key(self):
        return self.formfield_name()


class FieldFacet(BaseFacet):
    def __init__(self, name, **kwargs):
        self.limit = kwargs.pop('limit', 10)
        self.sort = kwargs.pop('sort', None)
        self.mincount = kwargs.pop('mincount', 1)
        self.missing = kwargs.pop('missing', None)
        self.offset = kwargs.pop('offset', None)

        super(FieldFacet, self).__init__(name, **kwargs)

    def build_params(self, params):
        params = super(FieldFacet, self).build_params(params)
        params['facet.field'].append(self.final_query_field())

        if self.sort:
            params['f.%s.facet.sort' % self.solr_fieldname] = self.sort
        if self.limit:
            params['f.%s.facet.limit' % self.solr_fieldname] = self.limit
        if self.offset:
            params['f.%s.facet.offset' % self.solr_fieldname] = self.offset
        if self.mincount:
            params['f.%s.facet.mincount' % self.solr_fieldname] = self.mincount
        if self.missing:
            params['f.%s.facet.missing' % self.solr_fieldname] = self.missing

        return params


class QueryFacet(BaseFacet):
    def __init__(self, name, **kwargs):
        self.choices = kwargs.pop('choices')
        super(QueryFacet, self).__init__(name, **kwargs)

    def build_params(self, params):
        params = super(QueryFacet, self).build_params(params)

        for choice in self.choices:
            query = '%s:%s' % (self.final_query_field(), choice[1])
            params['facet.query'].append(query)

        return params

    def _bucket_to_query(self, bucket):
        limits = bucket[1:-1].split(' ')
        return '%s-%s' % (limits[0] if limits[0] != '*' else '', limits[2] if limits[2] != '*' else '')

    def transform_form_value(self, value):
        try:
            start, end = value.split('-')
        except ValueError:
            start = '*'
            end = '*'

        if start in ['', '*']:
            start = '*'
        else:
            try:
                float(start)
            except ValueError:
                start = '*'
        if end in ['', '*']:
            end = '*'
        else:
            try:
                float(end)
            except ValueError:
                # Probably a hacking attempt
                end = '*'

        return "[%s TO %s]" % (start, end)

    def update(self, facet_results):
        self.values = []
        result_dict = dict(facet_results.results)
        for label, query in self.choices:
            try:
                count = result_dict[query]
            except KeyError:
                count = 0
            if count > 0:
                t = {
                    'label': label,
                    'query': self._bucket_to_query(query),
                    'count': count,
                    'selected': self._bucket_to_query(query) in self.selected_values,
                    }
                if t['selected']:
                    self.active.append({
                        'value': t['label'],
                        'query': t['query'],
                        })
                self.values.append(t)