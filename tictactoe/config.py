from datetime import datetime
from inspect import signature


deepmind_home = 'C:/Users/John/deepmind'


class CachedInstance(type):
    """For unique instances of a class.  Use like this:
        class X(metaclass=CachedInstance):
            def __init__(self, vara, varb):
                self.vara = vara
                self.varb = varb
            etc.
        Ref: https://stackoverflow.com/questions/50820707/python-class-instances-unique-by-some-property
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Use inspection to form an explicit dict of args by name,
        #   whether those args are supplied positionally, or by name, or by default
        explicit_args = {}
        poppable_args = list(args)
        for name, parm in signature(cls.__init__).parameters.items():
            if name == 'self':
                continue
            if len(poppable_args):
                val = poppable_args.pop(0)
            elif name in kwargs:
                val = kwargs[name]
            else:
                val = parm.default
            explicit_args[name] = val
        # Class itself and explicit dict of args in alpha order,
        #   form key to determine uniqueness of object to be instantiated
        index = cls, tuple(sorted(explicit_args.items()))
        # index = cls, args, tuple(sorted(kwargs.items()))
        if index not in cls._instances:
            cls._instances[index] = super(CachedInstance, cls).__call__(*args, **kwargs)
        return cls._instances[index]


def log(msg=''):
    print('%s %s' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg))

