from types import ModuleType
from importlib.machinery import SourceFileLoader

from abm.loaders import AbmLoader
import abm.activate

from quoll.transpiler import translate

class QuollLoader(AbmLoader, SourceFileLoader):

  extensions = ('.py', '.qll', '.quoll')

  def source_to_code(self, data, path, *, _optimize=-1):
    source = data.decode('utf-8')
    ast = translate(source, path)
    return super().source_to_code(ast, path, _optimize=_optimize)

QuollLoader.register(override_builtins=True)