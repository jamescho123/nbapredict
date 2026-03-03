import ast
import os

file_path = r'c:\Users\hp\OneDrive\文档\GitHub\nbapredict\app_pages\User_Management.py'

with open(file_path, 'r', encoding='utf-8') as f:
    source = f.read()

tree = ast.parse(source)

class Visitor(ast.NodeVisitor):
    def visit_If(self, node):
        # customized check for the specific if block
        # line 48: if current_user:
        if isinstance(node.test, ast.Name) and node.test.id == 'current_user':
            print(f"Found 'if current_user:' at line {node.lineno}")
            print(f"Body contains {len(node.body)} statements.")
            for child in node.body:
                 print(f"  Statement type: {type(child).__name__} at line {child.lineno}")
                 if isinstance(child, ast.With):
                     print(f"    This is a 'with' block.")
                     if hasattr(child, 'items') and child.items:
                        item = child.items[0]
                        if hasattr(item.context_expr, 'id'):
                           print(f"    Context expr: {item.context_expr.id}")
            
    def visit_Attribute(self, node):
        if node.attr == 'get':
            print(f"Found .get call at line {node.lineno}")
            if hasattr(node.value, 'id'):
                print(f"  Called on variable: {node.value.id}")

visitor = Visitor()
visitor.visit(tree)
