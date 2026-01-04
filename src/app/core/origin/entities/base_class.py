from pydantic import BaseModel, ConfigDict
from typing import *


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class BaseClass(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,  # Allow both snake_case and camelCase when parsing
    )


# class BaseClass():
#     """
#     Base class for all entities.
#     This class can be extended to create specific entities.
#     It provides a common interface and shared functionality.
#     """

#     def __init__(self, **kwargs):
#         """
#         Initialize the base class with keyword arguments.
#         """
#         if kwargs:
#             self.__set_data(**kwargs)

#     def __set_data(self, **kwargs):
#         """
#         Initialize the base class with keyword arguments.
#         """
#         for key, value in kwargs.items():
#             if hasattr(self, key):
#                 setattr(self, key, value)

#     def __repr__(self):
#         return f"{self.__class__.__name__}({', '.join(f'{k}={v!r}' for k, v in self.__dict__.items())})"
