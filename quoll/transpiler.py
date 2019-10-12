from collections import defaultdict
from typing import Any, List, Dict
import ast
from ast import AST, dump, NodeTransformer, copy_location, Call, Name, Load, With, FunctionDef, NameConstant, Index, Subscript, arg, Expression, If, Suite, Attribute
from functools import partial
from dataclasses import dataclass, field

from astpretty import pprint

import quoll.config

@dataclass
class TranslationContext:

  boilerplate_alias: str = 'bp'

  allocation_found: bool = False

  measurement_hoisting_table: List[list] = field(default_factory=lambda: [])

  allocation_context: List[list] = field(default_factory=lambda: [])

  inside_class_body: bool = False

  _UNIQUE_NAME_COUNTER: Dict[str, int] = field(default_factory=lambda: defaultdict(lambda: 0))

  # TODO: Improve to be unique per scope. Now it is globally unique per compilation.
  def newname(self, name):
    count = self._UNIQUE_NAME_COUNTER[name]
    self._UNIQUE_NAME_COUNTER[name] += 1

    if count == 0:
      return name

    return f'{name}_{count}'


class Translator(NodeTransformer):

  _context: TranslationContext

  def __init__(self, context: TranslationContext):
    self._context = context


class ControlledComputer(Translator):

  def __init__(self, *args, control_param_name, **kwargs):
    super().__init__(*args, **kwargs)
    self._control_param_name = control_param_name

  def visit_Call(self, node: Call):
    if _is_operation_call(node):
      node.func = copy_location(_wrap_in_controlled(node.func), node)
      node.args.insert(0, copy_location(
        Name(self._control_param_name, ctx=Load()), node.args[0]))
      return node

    if _is_variant_call(node):
      functor_application = node.func
      if _identify_signature(functor_application) == 'Id':
        node.func = copy_location(_wrap_in_controlled(node.func), node)
        node.args.insert(0, copy_location(
          Name(self._control_param_name, ctx=Load()), node.args[0]))

      else:
        node.args[0] = copy_location(_extend_control_data(
          node.args[0], self._control_param_name), node.args[0])

    self.generic_visit(node)
    return node


class AdjointComputer(Translator):

  def visit_Call(self, node):
    if _is_operation_call(node):
      node.func = copy_location(_wrap_in_adjoint(node.func), node)
      return node

    self.generic_visit(node)
    return node

  def visit_Subscript(self, node):
    if _is_functor_application(node):
      return copy_location(_wrap_in_adjoint(node), node)

    self.generic_visit(node)
    return node


def _wrap_in_adjoint(node):
  return _wrap_in_functor(node, 'Adjoint')

def _wrap_in_controlled(node):
  return _wrap_in_functor(node, 'Controlled')

def _wrap_in_functor(node, name):
  wrapper = ast.parse(f'{name}[_]', mode='single').body[0].value
  wrapper.slice.value = node
  return wrapper

def _extend_control_data(original_control_data_node, extension_name):
  extended = ast.parse(f'(_) & {extension_name}').body[0].value
  extended.left = original_control_data_node
  return extended

def _is_operation_call(call):
  return isinstance(call.func, Name)


# TODO: A variant is the result of applying a functor to an operation.
def _is_variant_call(call):
  return isinstance(call.func, Subscript)\
    and _is_functor_application(call.func)

def _is_functor_application(subscript):
  return isinstance(subscript.value, Name)\
    and subscript.value.id in ['Adjoint', 'Controlled']\
    and isinstance(subscript.slice, Index)\
    and isinstance(subscript.slice.value, (Name, Attribute))

def _identify_signature(functor_application):
  if not isinstance(functor_application, Subscript):
    return 'Id'

  if isinstance(functor_application.value, Name)\
    and functor_application.value.id == 'Controlled':
    return 'Controlled'

  return _identify_signature(functor_application.slice)


class BodyTranslator(Translator):

  def visit_ClassDef(self, node):
    self._context.inside_class_body = True
    self.generic_visit(node)
    self._context.inside_class_body = False
    return node

  def visit_Module(self, node):
    first_node = node.body[0]
    import_boilerplate = copy_location(
      _import_boilerplate(self._context.boilerplate_alias), first_node)
    node.body.insert(0, import_boilerplate)

    self.generic_visit(node)
    return node

  def visit_With(self, node):
    if _is_allocation(node):
      self._context.measurement_hoisting_table.append([])
      self._context.allocation_context.append([])
      self._context.allocation_context[-1] = [node.body, -1]
      # Replace measurement calls with variables
      for index, old_node in enumerate(node.body):
        self._context.allocation_context[-1][1] = index
        node.body[index] = self.visit(old_node)

      # Create measurement proxies, execute and return measurements
      new_nodes = []
      proxy_to_measure_names = {}
      for index, (_, m_node, m_name) in enumerate(self._context.measurement_hoisting_table[-1]):
        proxy_name = f'_mp{index + 1}'
        proxy_to_measure_names[proxy_name] = m_name
        new_nodes.append(self._assign_proxy(m_node, proxy_name, node))

      new_nodes.append(self._assign_measurements(proxy_to_measure_names, node))

      # Insert at the proper point in the current allocation
      insertion_point = self._context.measurement_hoisting_table[-1][0][0]
      node.body[insertion_point:insertion_point] = new_nodes

      self._context.allocation_context.pop()
      self._context.measurement_hoisting_table.pop()
      return node

    self.generic_visit(node)
    return node

  def visit_If(self, node: If):
    if _is_control(node):
      control_name = self._context.newname('__control')
      # TODO: Add support for elif/else clauses
      assert len(node.orelse) == 0, 'Still no support for elif/else clauses'
      context_node = _control_context_node(node, control_name)
      # TODO: Add support for a more general combination of things that happen
      # inside a Quoll statement or control what can appear in these structures
      # and fail when needed.
      controlled_body = ControlledComputer(self._context, control_param_name=control_name).visit(Suite(node.body)).body
      context_node.body = controlled_body
      return context_node

    return self.generic_visit(node)

  def visit_Call(self, node: Call):
    self.generic_visit(node)
    if _is_measurement(node):
      m_name = f'_m{len(self._context.measurement_hoisting_table[-1]) + 1}'
      self._context.measurement_hoisting_table[-1].append((self._context.allocation_context[-1][1], node, m_name))
      return copy_location(_replace_measurement(m_name), node)

    return node

  def visit_FunctionDef(self, node: FunctionDef):
    if _is_qdef(node):
      fix_location = partial(copy_location, old_node=node)
      node.body = self.generic_visit(Suite(node.body)).body
      new_nodes = [node]
      if _auto_adjoint(node):
        adjoint_implementation = fix_location(self._compute_adjoint(node))
        adjoint_implementation.body.reverse()
        new_nodes.append(adjoint_implementation)
        new_nodes.extend(
          map(fix_location, _wire_adjoints(node, adjoint_implementation))
        )

      if _auto_controlled(node):
        controlled_implementation = fix_location(self._compute_controlled(node))
        new_nodes.append(controlled_implementation)
        new_nodes.extend(
          map(fix_location, _wire_controlled(node, controlled_implementation))
        )

      return new_nodes

    self.generic_visit(node)
    return node

  def _compute_adjoint(self, node: FunctionDef):
    import copy
    adjoint = copy.deepcopy(node)
    adjoint.name = f'{node.name}_adj'
    if adjoint.name[0] != '_':
      adjoint.name = f'_{adjoint.name}'
    adjoint.decorator_list = []
    AdjointComputer(self._context).visit(adjoint)
    return adjoint

  def _compute_controlled(self, node: FunctionDef):
    import copy
    adjoint = copy.deepcopy(node)
    adjoint.name = f'{node.name}_ctl'
    if adjoint.name[0] != '_':
      adjoint.name = f'_{adjoint.name}'
    control_param_name = self._context.newname('__control')
    parameter_position = 0
    if self._context.inside_class_body:
      parameter_position = 1
    adjoint.args.args.insert(
      parameter_position, copy_location(arg(control_param_name, annotation=None), node))
    adjoint.decorator_list = []
    ControlledComputer(
      self._context, control_param_name=control_param_name).visit(adjoint)
    return adjoint


  def _assign_proxy(self, m_node: Call, proxy_name: str, node: Call):
    return copy_location(_assign_to_proxy(m_node, proxy_name), node)

  def _assign_measurements(self, proxy_to_measure_names, node):
    proxy_names = tuple(proxy_to_measure_names.keys())
    measure_names = tuple(proxy_to_measure_names.values())
    return copy_location(_assign_to_measurements(self._context.boilerplate_alias, proxy_names, measure_names), node)


def _is_qdef(node: FunctionDef):
  return len(node.decorator_list) > 0\
    and isinstance(node.decorator_list[-1], Call)\
    and isinstance(node.decorator_list[-1].func, Name)\
    and node.decorator_list[-1].func.id == 'qdef'


def _wire_adjoints(node: FunctionDef, adjoint_node: FunctionDef):
  node_name = node.name
  adjoint_node_name = adjoint_node.name
  return [
    ast.parse(f'setattr({node_name}, \'__adj__\', {adjoint_node_name})').body[0],
    ast.parse(f'setattr({adjoint_node_name}, \'__adj__\', {node_name})').body[0]
  ]

def _wire_controlled(node: FunctionDef, controlled_node: FunctionDef):
  node_name = node.name
  controlled_node_name = controlled_node.name
  return [
    ast.parse(f'setattr({node_name}, \'__ctl__\', {controlled_node_name})').body[0],
    ast.parse(f'setattr({controlled_node_name}, \'__ctl__\', {controlled_node_name})').body[0]
  ]



def _auto_adjoint(node: FunctionDef):
  return _some_kw_match('adj', True, node.decorator_list[-1].keywords)

def _auto_controlled(node: FunctionDef):
  return _some_kw_match('ctl', True, node.decorator_list[-1].keywords)

def _some_kw_match(name, value, kwargs):
  def id_is_adj(kw):
    return kw.arg == name and isinstance(kw.value, NameConstant) and kw.value.value == value

  return any(map(id_is_adj, kwargs))


def _is_measurement(node: Call):
  return isinstance(node.func, Name) and node.func.id == 'measure'


def _is_allocation(node: With):
  return isinstance(node.items[0].context_expr, Call) and isinstance(node.items[0].context_expr.func, Name) and node.items[0].context_expr.func.id == 'allocate'


def _is_control(node: If):
  return isinstance(node.test, Call) and isinstance(node.test.func, Name) and node.test.func.id == 'superposition'


def _import_boilerplate(alias: str ='bp'):
  return ast.parse(f'import quoll.boilerplate as {alias}', mode='single').body[0]


def _control_context_node(node: If, control_param_name: str) -> With:
  context_node = ast.parse(f'with superposition(_) as {control_param_name}: ...', mode='exec').body[0]
  context_node.items[0].context_expr.args[0] = node.test.args[0]
  return context_node

def _replace_measurement(name: str):
  return ast.parse(name, mode='single').body[0].value


def _assign_to_proxy(m_node, proxy_name):
  assign_node = ast.parse(f'{proxy_name} = _').body[0]
  assign_node.value = m_node
  return assign_node


def _assign_to_measurements(bp_alias, proxy_names, measure_names):
  last_comma = ',' if len(measure_names) == 1 else ''
  return ast.parse(f'({", ".join(measure_names) + last_comma}) = {bp_alias}.execute({", ".join(proxy_names)})').body[0]

@quoll.config.show_python
def translate(source: str, path: str) -> AST:
  module = ast.parse(source)
  context = TranslationContext()
  BodyTranslator(context).visit(module)
  return module