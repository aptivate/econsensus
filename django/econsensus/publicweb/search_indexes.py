from haystack import indexes
from publicweb.models import Decision


class DecisionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    organization = indexes.CharField(model_attr="organization")

    def get_model(self):
        return Decision
