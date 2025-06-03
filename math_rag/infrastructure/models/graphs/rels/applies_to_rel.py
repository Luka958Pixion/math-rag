from neomodel import AsyncStructuredRel, StringProperty


class AppliesToRel(AsyncStructuredRel):
    description = StringProperty()
