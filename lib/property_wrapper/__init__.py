"""
Contains tools for creating wrapper classes around subscriptable data
of a predictable structure.

Public attributes:
PropertyWrapper -- the base class for wrapper classes
make_spec prop -- a function for creating specs for properties
"""

# alias the two public attributes for the context in which they are
# to be used
from property_wrapper.nested_lookup_prop import \
    NestedLookupPropertyWrapper as PropertyWrapper, make_spec as prop
