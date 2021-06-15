"""Custum TraitType."""
from traitlets import TraitType
from traitlets.utils.descriptions import describe, class_of


def _trait_info(self, obj) -> str:
    """Return trait info string.

    Parameters
    ----------
    obj : [type]
        [description]

    Returns
    -------
    str
        trait info string
    """
    trait = "trait" if obj is None else f"trait of {class_of(obj)} instance"
    return f"The '{self.name}' {trait} expected {self.info()}"


def _describe_str(article, value):
    """Custum describe function.

    Parameters
    ----------
    article : [type]
        [description]
    value : [type]
        [description]

    Returns
    -------
    [type]
        [description]
    """
    return describe('the', value, name=f"'{value}'")


class ModeString(TraitType):
    """`notebook` or `lab`."""

    modes = ["notebook", "lab"]
    info_text = "Mode String"

    def validate(self, obj, value) -> str:
        """Validate value."""
        if isinstance(value, str):
            value = value.strip()
            if value in self.modes:
                return value
        self.error(obj, value)
