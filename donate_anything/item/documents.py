"""
Elasticsearch with Django in the form of "documents"
"""
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from donate_anything.item.models import Item


@registry.register_document
class ItemDocument(Document):
    class Index:
        name = "items"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Item
        fields = ["name", "image"]
