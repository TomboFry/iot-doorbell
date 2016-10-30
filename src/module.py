from abc import ABCMeta, abstractmethod
from os.path import dirname, basename, isfile, join
import glob
import imp

def load_modules(dir, known_plugins):
    path = join(dirname(__file__), dir, "*.py")
    modules = glob.glob(path)

    names = [ basename(f)[:-3] for f in modules if isfile(f) ]
    modlist = dict(zip(names, modules));

    mods = []
    for name in modlist.keys():
        mods.append(imp.load_source(name, modlist[name]))

    return mods

class DingPlugin(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def __init__(self, app):
        pass

    @abstractmethod
    def init(self, users):
        pass

    @abstractmethod
    def load(self, collection):
        pass

    @abstractmethod
    def ding(self, event):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    @abstractmethod
    def get_name(self):
        pass
