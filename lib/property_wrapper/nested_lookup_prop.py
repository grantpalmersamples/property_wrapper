"""
Contains tools for creating wrapper classes around subscriptable data
of a predictable structure.
"""

from collections import namedtuple

from property_wrapper.nested_lookup import nget, nset, ndel


class NestedLookupProperty(property):
    """
    A property pointing to a value in a subscriptable data structure.
    """

    def __init__(self, path, fget=None, fset=None, fdel=None, doc=None):
        """
        Initialize a nested lookup property with a path and the
        desired getter, setter, and deleter.

        :param path: The list of consecutive keys used to access this
        property in a predicable structure
        :param fget: The function used as a getter for the property
        :param fget: The function used as a setter for the property
        :param fdel: The function used as a deleter for the property
        """

        self.path = path
        super().__init__(fget, fset, fdel, doc)


# TODO: Try to find a way to make it possible for end users to access
# and expand upon the default property methods
class _NestedLookupPropertyFactory:
    """
    A factory for creating named nested lookup properties to be
    attached to classes.

    Creates property methods pointing to the path at the given name in
    the class's property mapping.
    """

    doc = '{} underlying data held by the \'{}\' property'
    lookup_error_msg = 'broken property: \'{}\''
    type_error_msg = 'cannot {}'.format(doc)

    def build_fget(self, name):
        """
        Build a getter for a property of the given name.

        At runtime, reference the property mapping of the class that
        will contain this property to obtain the lookup path.

        :param name: The name that the property will have within the
        intended class and within the property mapping.
        :return: The get method
        """

        action_str = 'get'

        def fget(self):
            try:
                return nget(self, self._prop_map[name])
            except (LookupError, TypeError) as e:
                if isinstance(e, LookupError):
                    msg = self.lookup_error_msg.format(name)
                elif isinstance(e, TypeError):
                    msg = self.type_error_msg.format(action_str, name)
                raise AttributeError(msg) from e

        fget.__doc__ = self.doc.format(action_str.title(), name)

        return fget

    def build_fset(self, name):
        """
        Build a setter for a property of the given name.

        At runtime, reference the property mapping of the class that
        will contain this property to obtain the lookup path.

        :param name: The name that the property will have within the
        intended class and within the property mapping.
        :return: The fset method
        """

        action_str = 'set'

        def fset(self, value):
            try:
                nset(self, self._prop_map[name], value)
            except (LookupError, TypeError) as e:
                if isinstance(e, LookupError):
                    msg = self.lookup_error_msg.format(name)
                elif isinstance(e, TypeError):
                    msg = self.type_error_msg.format(action_str, name)
                raise AttributeError(msg) from e

        fset.__doc__ = self.doc.format(action_str.title(), name)

        return fset

    def build_fdel(self, name):
        """
        Build a deleter for a property of the given name.

        At runtime, reference the property mapping of the class that
        will contain this property to obtain the lookup path.

        :param name: The name that the property will have within the
        intended class and within the property mapping.
        :return: The fdel method
        """

        action_str = 'delete'

        def fdel(self):
            try:
                ndel(self, self._prop_map[name])
            except (LookupError, TypeError) as e:
                if isinstance(e, LookupError):
                    msg = self.lookup_error_msg.format(name)
                elif isinstance(e, TypeError):
                    msg = self.type_error_msg.format(action_str, name)
                raise AttributeError(msg) from e

        fdel.__doc__ = self.doc.format(action_str.title(), name)

        return fdel

    def __call__(self, name, path, fget=True, fset=True, fdel=True, doc=None):
        """
        Create a named nested lookup properties to be attached to a
        wrapper class.

        The class must have an attribute _prop_map containing the name
        of the property as a key mapping to the lookup path for the
        property within the data wrapped by the class.

        :param name: The name of the property
        :param path: A list of keys representing the lookup path to the
        desired value in the underlying data
        :param fget: The getter for the property.  Set to `False` to
        prevent retrieval of the property.  Defaults to `True`, which
        indicates that the getter should be generated by the factory.
        :param fset: The setter for the property.  Set to `False` to
        prevent assignment of the property.  Defaults to `True`, which
        indicates that the setter should be generated by the factory.
        :param fdel: The deleter for the property.  Set to `False` to
        prevent deletion of the property.  Defaults to `True`, which
        indicates that the deleter should be generated by the factory.
        :param doc: The doc for the property
        :return: A NestedLookupProperty
        """

        if fget is True:
            fget = self.build_fget(name)
        if fset is True:
            fset = self.build_fset(name)
        if fdel is True:
            fdel = self.build_fdel(name)
        return NestedLookupProperty(path, fget=fget, fset=fset, fdel=fdel,
                                    doc=doc)


NestedLookupPropertySpec = namedtuple('NestedLookupPropertySpec',
                                      ['path', 'fget', 'fset', 'fdel', 'doc'])
NestedLookupPropertySpec.__doc__ = """
A spec for a property to be made by a nested lookup property factory.
Impossible to use a builder since property members are readonly.
"""


def make_spec(path, fget=True, fset=True, fdel=True, doc=None):
    """
    Create a spec for a nested lookup property.

    :param path: A list of keys representing the lookup path to the
    desired value in the underlying data
    :param fget: The getter for the property.  Set to `False` to
    prevent retrieval of the property.  Defaults to `True`.
    :param fset: The setter for the property.  Set to `False` to
    prevent assignment of the property.  Defaults to `True`.
    :param fdel: The deleter for the property.  Set to `False` to
    prevent deletion of the property.  Defaults to `True`.
    :param doc: The doc for the property
    :return: A NestedLookupPropertySpec to be processed by a
    factory
    """

    return NestedLookupPropertySpec(path, fget, fset, fdel, doc)


class NestedLookupPropertyWrapperMeta(type):
    """
    Add properties when passed a keyword arg called 'props' containing
    a mapping of property names to nested lookup property specs.
    """

    def __new__(mcs, name, bases, dct, **kwargs):
        """
        Create a new instance of a nested lookup wrapper class.

        Refer to documentation of metaclasses.
        """
        if 'props' in kwargs:
            make_nlp = _NestedLookupPropertyFactory()
            # create an empty property mapping for the class
            prop_map = dct['_prop_map'] = {}
            # props is the dictionary mapping property names to specs
            for k, v in kwargs['props'].items():
                nlp = make_nlp(k, *v)
                # hook up the name and path in the property mapping
                prop_map[k] = nlp.path
                # add the property to the class's dict
                dct[k] = nlp
        return super().__new__(mcs, name, bases, dct)


class NestedLookupPropertyWrapper(metaclass=NestedLookupPropertyWrapperMeta):
    """
    The base class for wrapper classes.  Uses a metaclass to add
    properties when passed a keyword arg called 'props' containing
    a mapping of property names to nested lookup property specs.
    """
