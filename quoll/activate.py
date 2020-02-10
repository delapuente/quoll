from types import ModuleType
from importlib.machinery import SourceFileLoader
from contextlib import suppress

from abm.loaders import AbmLoader
import abm.activate

from quoll.transpiler import translate, TranslationContext, BodyTranslator

class QuollLoader(AbmLoader, SourceFileLoader):

  extensions = ('.qll', '.quoll')

  def source_to_code(self, data, path, *, _optimize=-1):
    source = data.decode('utf-8')
    ast = translate(source, path)
    return super().source_to_code(ast, path, _optimize=_optimize)

QuollLoader.register()

with suppress(NameError):
  ip = get_ipython()
  context = TranslationContext()
  ip.ast_transformers.append(BodyTranslator(context))