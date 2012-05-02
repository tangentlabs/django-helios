

class BaseFacet(object):

    def __init__(self, name, multiselect=False, mincount=0, limit=10, sort='count', missing=False, **kwargs):
        self.name = name
        self.multiselect = multiselect
        self.limit = limit
        self.sort = sort
        self.mincount = mincount
        self.missing = missing
        self.active = []
        self.values = []
        self.tag_name = name.lower().replace(' ','')

    def get_index_field(self):
        """
        Returns the name of the field used in the search index
        """
        return self.formfield_name()

    def add_to_query(self, query):
        index_field = self.get_index_field()
        if self.multiselect:
            index_field = '{!ex=%s}%s' % (self.tag_name, index_field)
        query.add_field_facet(index_field)

    def filter_query(self, query, values):
        if values:
            value_str = ' OR '.join([self.transform_form_value(x) for x in values])
            query.add_narrow_query('{!tag=%s}%s:(%s)' % (self.tag_name, self.get_index_field(), value_str))

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
