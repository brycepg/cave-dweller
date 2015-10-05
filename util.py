class classproperty(object):
    def __init__(self, getter, setter=None):
        self._getter = getter
        self._setter = setter

    def setter(self, setter):
        self._setter = setter

    def __get__(self, obj, cls = None):
        return self._getter(cls)

    def __set__(self, *args):
        print(args)


