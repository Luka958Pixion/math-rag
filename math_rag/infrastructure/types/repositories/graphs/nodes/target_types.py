from typing import TypeVar

from neomodel import AsyncStructuredNode, AsyncStructuredRel


TargetNodeType = TypeVar('TargetNodeType', bound=AsyncStructuredNode)
TargetRelType = TypeVar('TargetRelType', bound=AsyncStructuredRel)
