from helios.solr import SolrConnection
from django.conf import settings

class HeliosConnectionMiddleware(object):
    def process_request(self, request):
        url = settings.HELIOS_SOLR_URL
        request.solr_connection = SolrConnection(url)