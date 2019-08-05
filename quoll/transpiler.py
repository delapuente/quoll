from typing import Any
import ast
from ast import AST, dump, NodeTransformer, copy_location, Call, Name, Load, Expr, With
from dataclasses import dataclass, field

from astpretty import pprint

from quoll.unparser import unparse

@dataclass
class TranslationContext:

  boilerplate_alias: str = 'bp'

  allocation_found: bool = False

  measurement_hoisting_table: list = field(default_factory=lambda: [])

  allocation_context: list = field(default_factory=lambda: [])


class Translator(NodeTransformer):

  _context: TranslationContext

  def __init__(self, context: TranslationContext):
    self._context = context


class BodyTranslator(Translator):

  def visit_Module(self, node):
    first_node = node.body[0]
    import_boilerplate = copy_location(
      _import_boilerplate(self._context.boilerplate_alias), first_node)
    node.body.insert(0, import_boilerplate)

    self.generic_visit(node)
    return node

  def visit_With(self, node):
    if _is_allocation(node):
      self._context.allocation_context = [node.body, -1]
      # Replace measurement calls with variables
      for index, old_node in enumerate(node.body):
        self._context.allocation_context[1] = index
        self.visit(old_node)

      # Create measurement proxies, execute and return measurements
      new_nodes = []
      proxy_to_measure_names = {}
      for index, (_, m_node, m_name) in enumerate(self._context.measurement_hoisting_table):
        proxy_name = f'_mp{index + 1}'
        proxy_to_measure_names[proxy_name] = m_name
        new_nodes.append(self._assign_proxy(m_node, proxy_name, node))

      new_nodes.append(self._assign_measurements(proxy_to_measure_names, node))

      # Insert at the proper point in the current allocation
      insertion_point = self._context.measurement_hoisting_table[0][0]
      node.body[insertion_point:insertion_point] = new_nodes

      return node

    return node

  def visit_Call(self, node: Call):
    self.generic_visit(node)
    if _is_measurement(node):
      m_name = f'_m{len(self._context.measurement_hoisting_table) + 1}'
      self._context.measurement_hoisting_table.append((self._context.allocation_context[1], node, m_name))
      return copy_location(_replace_measurement(m_name), node)

    return node

  def _assign_proxy(self, m_node: Call, proxy_name: str, node: Call):
    return copy_location(_assign_to_proxy(m_node, proxy_name), node)

  def _assign_measurements(self, proxy_to_measure_names, node):
    proxy_names = tuple(proxy_to_measure_names.keys())
    measure_names = tuple(proxy_to_measure_names.values())
    return copy_location(_assign_to_measurements(self._context.boilerplate_alias, proxy_names, measure_names), node)


def _is_measurement(node: Call):
  return isinstance(node.func, Name) and node.func.id == 'measure'

def _is_allocation(node: With):
  return isinstance(node.items[0].context_expr, Call) and isinstance(node.items[0].context_expr.func, Name) and node.items[0].context_expr.func.id == 'allocate'

def translate(source: str) -> AST:
  module = ast.parse(source)
  context = TranslationContext()
  BodyTranslator(context).visit(module)
  #print(unparse(module))
  return module


def _import_boilerplate(alias: str ='bp'):
  return ast.parse(f'import quoll.boilerplate as {alias}', mode='single').body[0]

def _replace_measurement(name: str):
  return ast.parse(name, mode='single').body[0].value

def _assign_to_proxy(m_node, proxy_name):
  assign_node = ast.parse(f'{proxy_name} = _').body[0]
  assign_node.value = m_node
  return assign_node

def _assign_to_measurements(bp_alias, proxy_names, measure_names):
  return ast.parse(f'{", ".join(measure_names)} = {bp_alias}.execute({", ".join(proxy_names)})').body[0]