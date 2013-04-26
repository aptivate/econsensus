import factory

from django.contrib.auth.models import User
from publicweb.models import Decision
from organizations.models import Organization, OrganizationUser


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User

    # Have factoryboy add a sequenced number, n, to username for uniqueness
    username = factory.Sequence(lambda n: 'user%s' % n)


class OrganizationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Organization


class OrganizationUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = OrganizationUser

    user = factory.SubFactory(UserFactory)
    organization = factory.SubFactory(OrganizationFactory)


class DecisionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Decision

    organization = factory.SubFactory(OrganizationFactory)
