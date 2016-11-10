import ast
import inspect
import copy
import astor


def removeArgument(functree, idx):
    functree.args.args.pop(idx)
    
def argumentName(functree, idx):
    return functree.args.args[idx].arg

def astFromFunction(func):
    tree = compile(inspect.getsource(func), '<string>', 'exec', ast.PyCF_ONLY_AST)
    return tree.body[0]
    
def astFromLambdaString(lambda_string):
    tree = compile(lambda_string, '<string>', 'exec', ast.PyCF_ONLY_AST)
    return tree.body[0].value
    
def functionFromAst(functree):
    locale_scope = {}
    moduletree = ast.copy_location(ast.Module([functree]), functree)
    exec(compile(moduletree, '<string>', 'exec'), {}, locale_scope)
    return locale_scope[tuple(locale_scope.keys())[0]]

    
class Rewriter(ast.NodeTransformer):
    def __init__(self, *args):
        super().__init__()        
        self.subs = {}
        self.names = {}

    def write(self, functree):
        for idx, substitute in self.subs.items():
            self.names[argumentName(functree, idx)] = substitute
        newtree = self.visit(functree)
        for i in self.subs.keys():
            removeArgument(functree, i)
        return newtree
    
    
class InlineVariableRewriter(Rewriter):
    def __init__(self, *args):
        super().__init__()
        for i, substitute in enumerate(args):
            if substitute is not None:
                assert(isinstance(substitute, ast.expr))
                self.subs[i] = substitute
    
    def visit_Name(self, node):
        if node.id in self.names:
            return ast.copy_location(copy.deepcopy(self.names[node.id]), node)
        return node
            
    
        
class InlineCallRewriter(Rewriter):
    def __init__(self, *args):
        super().__init__()
        for i, substitute in enumerate(args):
            if substitute is not None:
                assert(isinstance(substitute, (ast.Lambda, ast.FunctionDef)))
                self.subs[i] = substitute
    
    def visit_Name(self, node):
        assert( node.id not in self.names )
        return node
        
    def visit_Call(self, node):
        print(node.func.id)
        if isinstance(node.func, ast.Name) and node.func.id in self.names:
            functree = copy.deepcopy(self.names[node.func.id])
            newtree = InlineVariableRewriter(*node.args).write(functree)
            return ast.copy_location(newtree.body, node)
        return node
        
class EmbedClosure:
    def __init__(self, **kwargs):
        self.argNames = list(kwargs.keys())
        self.argValues = [kwargs[k] for k in self.argNames]
        
    def write(self, functree):
        argList = [ast.copy_location(ast.arg(a, None), functree) for a in self.argNames]
        nameExpr = ast.copy_location(ast.Name(functree.name, ast.Load()), functree)
        returnExpr = ast.copy_location(ast.Return(nameExpr), functree)
        newfunctree = ast.FunctionDef(
            '_wrap',
            ast.arguments(argList, None, [], [], None, []),
            [functree, returnExpr],
            [], None)
        newfunctree = ast.copy_location(newfunctree, functree)
        return functionFromAst(newfunctree)(*self.argValues)
        


def f(a, b):
    return a + 1

tree = compile(inspect.getsource(f), '<string>', 'exec', ast.PyCF_ONLY_AST)
print(tree.body[0].name)
# print(tree.body[0].args.args[0].arg)
# print(tree.body[0].body[0].value.right.func.id)
# ('name', 'args', 'body', 'decorator_list', 'returns')

def f(a, b):
    return a + b
functree = astFromFunction(f)
newtree = InlineVariableRewriter(astFromLambdaString('lambda: 2 * 2').body).write(functree)
print(functionFromAst(newtree)(100))

def f(a, b):
    return a + b(a)
functree = astFromFunction(f)
newtree = InlineCallRewriter(None, astFromLambdaString('lambda x: x * 3')).write(functree)
# print(astor.to_source(newtree))
print(functionFromAst(newtree)(100))

newtree = InlineVariableRewriter(astFromLambdaString('lambda: 2 * 2').body).write(newtree)
print(functionFromAst(newtree)())

# tree = ast.FunctionDef('_wrap', ast.arguments(['a'], None, None, None, None, []), [ast.Return(ast.Name('a', ast.Store()))], [], None)
# print(astor.to_source(tree))


f = EmbedClosure(int=int, c=1).write(astFromFunction(f))
