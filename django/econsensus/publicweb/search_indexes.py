from haystack import indexes
from publicweb.models import Decision


class DecisionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='author')
    description = indexes.CharField(model_attr='description')

    def get_model(self):
        return Decision
