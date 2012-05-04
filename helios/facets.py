from helios.forms.fields import MultipleCharField


class FacetResult(object):
    def __init__(self, facet, results, values):
        self.facet = facet
        self.results = results
        self.values = values


class BaseFacet(object):

    def __init__(self, name, fieldname, solr_fieldname, multiselect_or=False, mincount=0, limit=10, sort='count', offset=0, missing=False, **kwargs):
        self.name = name
        self.form_fieldname = form_fieldname
        self.solr_fieldname = solr_fieldname
        self.multiselect_or = multiselect_or
        self.limit = limit
        self.sort = sort
        self.mincount = mincount
        self.missing = missing
        self.active = []
        self.values = []
        self.offset = offset

    def add_to_query(self, query):
        query.add_field_facet(self.final_query_field())

    def final_query_field(self):
        index_field = solr_fieldname
        if self.multiselect_or:
            index_field = '{!ex=%s}%s' % (self.form_fieldname, index_field)
        return index_field

    def filter_query(self, query, values):
        if values:
            value_str = ' OR '.join([self.transform_form_value(x) for x in values])
            query.add_narrow_query('{!tag=%s}%s:(%s)' % (self.form_fieldname, self.get_index_field(), value_str))

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

    def update(self, facet_data, values):
        """
        Updates the facet with the results of the search query and form data
        """
        self.values = []

        if facet_data['fields'].get(self.facet_key(), None):
             facet_values = sorted(facet_data['fields'][self.facet_key()], key=self.facet_sortkey)

            for x in facet_values:
                t = {
                    'label': self.label_from_value(x[0]),
                    'query': x[0],
                    'count': x[1],
                    'selected':  x[0] in values,
                    }

                if t['selected']:
                    self.active.append({
                        'value': t['label'],
                        'query': t['query'],
                        })
                self.values.append(t)

            # Deal with any selected facets that fall outside of the selected range
            for x in set(values) - set([x[0] for x in facet_values]):
                t = {
                    'label': self.label_from_value(x),
                    'query': x,
                    'count': 1,
                    'selected':  x in values,
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