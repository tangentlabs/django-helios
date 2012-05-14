from helios.forms.fields import MultipleCharField


class FacetResult(object):
    def __init__(self, facet, results, values):
        self.facet = facet
        self.results = results
        self.values = values


class BaseFacet(object):

    def __init__(self, name, solr_fieldname, form_fieldname=None, multiselect_or=None, mincount=None, limit=None, sort=None, offset=None, missing=None, **kwargs):
        self.name = name
        self.form_fieldname = form_fieldname or self.name.lower()
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
        index_field = self.solr_fieldname
        if self.multiselect_or:
            index_field = '{!ex=%s}%s' % (self.form_fieldname, index_field)
        return index_field

    def filter_query(self, query):
        if self.selected_values:
            value_str = ' OR '.join([self.transform_form_value(x) for x in self.selected_values])
            query.add_filter('{!tag=%s}%s' % (self.form_fieldname, self.solr_fieldname), value_str)

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
    pass