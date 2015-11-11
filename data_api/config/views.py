import os
import base64

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ParseError

from etcdc.client import Client
from etcdc.errors import NotAFile


class ConfigEntryAPIView(APIView):

    resource_name = 'config-entries'
    etcd_client = None

    def get_etcd_client(self):
        if self.etcd_client is None:
            self.etcd_client = Client(settings.ETCD_SERVICE_HOST, port='2379')
        return self.etcd_client

    def construct_id(self, path):
        path_bytes = base64.urlsafe_b64encode(str.encode(path))
        return bytes.decode(path_bytes)

    def construct_path(self, id):
        try:
            path_bytes = base64.urlsafe_b64decode(id)
        except Exception:
            raise ParseError(detail='Bad id: {}'.format(id))
        return bytes.decode(path_bytes)

    def get_config_entry(self, path, key, value):
        entry = {}
        entry['type'] = 'config-entries'
        entry['id'] = self.construct_id(os.path.join(path, key))
        attributes = {}
        attributes['path'] = path
        attributes['key'] = key
        attributes['value'] = value
        entry['attributes'] = attributes
        return entry


class ConfigEntryList(ConfigEntryAPIView):
    categories = ['collector']

    def get(self, request, format=None):
        config_entries = []
        for category in self.categories:
            path = os.path.join('/', 'data', category)
            try:
                items = self.get_items(path)
            except KeyError:
                items = {}
            for key, value in items.items():
                entry = self.get_config_entry(path, key, value)
                config_entries.append(entry)
        return Response(config_entries)

    def get_items(self, key):
        items = {}
        client = self.get_etcd_client()
        for key in client.get_keys(key, recursive=True):
            try:
                items[os.path.basename(key)] = client.get(key).value
            except NotAFile:
                pass
        return items


class ConfigEntryDetail(ConfigEntryAPIView):

    def get(self, request, id, format=None):
        client = self.get_etcd_client()
        path = self.construct_path(id)

        try:
            value = client.get(path).value
        except KeyError:
            raise NotFound(detail='Key {} not found'.format(path))
        key = os.path.basename(path)
        return Response(self.get_config_entry(path, key, value))

    def patch(self, request, id, format=None):
        client = self.get_etcd_client()
        path = self.construct_path(id)
        value = request.data['value']
        client.set(path, value)
        return Response()
