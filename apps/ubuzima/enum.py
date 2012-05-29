#!/usr/bin/env python

"""
Copyright (C) 2011 Cameron Hayne (macdev@hayne.net)
This is published under the MIT Licence:
----------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from operator import attrgetter

class EnumClass(object):
    """
    EnumClass is the superclass of all enum classes created by
    the 'Enum' function below.
    Each such subclass represents a set of named values.
    """

    def __new__(cls, name, value=None):
        # I presume that 'value' is an immutable object
        # but not sure how to enforce this
        existingObj = cls.get(name)
        if existingObj:
            if value is None or value == existingObj.value:
                return existingObj
            else:
                raise TypeError("can't overwrite an existing enum")
        else:
            if value is None: # e.g. MyEnumType('foo')
                existingNames = cls.names()
                if existingNames:
                    # probably trying to refer to an existing enum object
                    # but got the name wrong
                    raise ValueError(("'%s' is not a valid enum name"
                                      + " (Must be one of: %s)")
                                      % (name, str(existingNames)))
                else:
                    # probably trying to create an enum object
                    # without specifying a value, just a name
                    raise ValueError("must supply value for enum")
            # create a new instance of 'cls'
            obj = super(EnumClass, cls).__new__(cls)
            # and assign 'name' & 'value' (via the superclass)
            super(EnumClass, obj).__setattr__('name', name)
            super(EnumClass, obj).__setattr__('value', value)
            # assign 'obj' as a class attribute for 'name' in 'cls'
            setattr(cls, name, obj)
            return obj

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        # I presume that the 'value' is not a mutable object
        return self

    def __setattr__(self, name, value):
        raise TypeError("can't modify an enum")

    def __delattr__(self, name):
        raise TypeError("can't modify an enum")

    # no need for __cmp__ or __hash__ since above methods ensure immutability

    def __str__(self):
        return self.name

    @classmethod
    def addAlias(cls, name, existingName):
        """
        Add 'name' as an alias for 'existingName'.
        'name' is a string.
        'existingName' is the name of one of the existing enum objects.
        This is intended as a way to maintain backward compatibility
        when the enum names get changed.
        Example of use:
            Vehicles.addAlias('horselessCarriage', 'car')
            # Now old code referring to Vehicles.horselessCarriage
            # will get the same object as Vehicles.car
            # i.e. Vehicles.horselessCarriage.name is 'car'
            # But Vehicles.names() does not include 'horselessCarriage'
        """
        existingNames = cls.names()
        if name in existingNames:
            raise ValueError("The name '%s' is already in use." % name)
        if existingName not in existingNames:
            raise ValueError(("'%s' is not one of the existing enum names."
                              + " (Must be one of: %s)")
                              % (existingName, str(existingNames)))
        existingObj = cls.get(existingName)
        setattr(cls, name, existingObj)

    @classmethod
    def get(cls, name):
        """
        Return the enum instance with the specified name.
        Return None if there is no such instance.
        """
        return getattr(cls, name.strip(), None)

    @classmethod
    def getByValue(cls, value):
        """
        Return an enum instance that has the specified value.
        Return None if there is no such instance.
        Note that there may be more than one enum instance with the same value
        and in that case this method returns whichever one it finds first.
        """
        for obj in cls.objects():
            if obj.value == value:
                return obj
        return None

    @classmethod
    def listOfNamesToListOfEnums(cls, listOfNames):
        """
        Convert a list of strings (names of enums of this class)
        into a list of enum instances.
        Example of use:
            listOfNames = ['red', 'blue']
            listOfEnums = Colours.listOfNamesToListOfEnums(listOfNames)
            # would give [Colours.red, Colours.blue]
        """
        listOfEnums = [cls(name) for name in listOfNames]
        return listOfEnums

    @classmethod
    def commaSepStrToEnumList(cls, commaSepNamesStr):
        enumList = list()
        commaSepNamesStr = commaSepNamesStr.lstrip('[ ')
        commaSepNamesStr = commaSepNamesStr.rstrip(' ]')
        names = commaSepNamesStr.split(',')
        for name in names:
            name = name.strip()
            enumObj = cls.get(name)
            if enumObj is not None:
                enumList.append(enumObj)
        return enumList

    @classmethod
    def objects(cls):
        objs = set() # need to use set since might have aliases
        for obj in cls.__dict__.values():
            if isinstance(obj, cls):
                objs.add(obj)
        objList = sorted(objs, key=attrgetter('value'))
        return objList

    @classmethod
    def names(cls):
        objList = cls.objects()
        nameList = [obj.name for obj in objList]
        return nameList
# -----------------------------------------------------------------------------

def Enum(classname, **kargs):
    """
    Create a new class named as specifed in the first argument,
    and then create instances of this class with the name/value pairs of
    the subsequent (keyword) arguments.
    Return the newly created class object.
    The values can be anything (not necessarily integers)
    but should be immutable objects (e.g. shouldn't be a list).
    Examples of use:
        >>> Colours = Enum('Colours', red=1, green=2, blue=3)
        >>> Colours.green.name
        'green'

        >>> print Colours.green
        green

        >>> Colours.green.value
        2

        >>> Colours.names()
        ['red', 'green', 'blue']

        >>> Colours.get('blue').value
        3

        >>> Colours.getByValue(3).name
        'blue'

        >>> Colours('blue').value
        3

        >>> Colours.addAlias('bleu', 'blue')
        >>> Colours.names()
        ['red', 'green', 'blue']

        >>> Colours.bleu.value
        3

        >>> [x.name for x in Colours.objects()]
        ['red', 'green', 'blue']

        >>> listOfNames = ['red', 'blue']
        >>> [x.name for x in Colours.listOfNamesToListOfEnums(listOfNames)]
        ['red', 'blue']

        >>> commaSepStr = "red, blue"
        >>> [x.name for x in Colours.commaSepStrToEnumList(commaSepStr)]
        ['red', 'blue']


        >>> Numbers = Enum('Numbers', pi=3.1415926, e=2.71828)
        >>> isinstance(Numbers, type)
        True

        >>> Numbers.names()
        ['e', 'pi']

        >>> round(Numbers.e.value, 3)
        2.718

        >>> x = Numbers.pi
        >>> x is Numbers('pi')
        True

        >>> Numbers('phi')
        Traceback (most recent call last):
            ...
        ValueError: 'phi' is not a valid enum name (Must be one of: ['e', 'pi'])

        >>> Numbers.e.value = 42
        Traceback (most recent call last):
            ...
        TypeError: can't modify an enum
    """

    # create a new class derived from EnumClass
    cls = type(classname, (EnumClass,), dict())
    for name in kargs.keys():
        # create an instance of 'cls' for each keyword arg
        obj = cls(name, kargs[name])
    # return the newly created class to the caller
    return cls

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import doctest
    doctest.testmod()

