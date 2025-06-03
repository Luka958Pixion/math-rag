from neomodel import AsyncStructuredRel, StringProperty, UniqueIdProperty


class AppliesToRel(AsyncStructuredRel):
    uid = UniqueIdProperty(required=True)
    description = StringProperty()
