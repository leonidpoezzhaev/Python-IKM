class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None

class Tree:
    def __init__(self):
        self.root = None

    def __str__(self):
        return self._to_str(self.root)

    def _to_str(self, node):
        if node is None:
            return ''

        if isinstance(node.data, (int, float)):
            return str(int(node.data)) if isinstance(node.data, float) and node.data.is_integer() else str(node.data)

        if isinstance(node.data, str) and node.data.isalpha():
            return node.data

        if node.data == '~':
            return '(-' + self._to_str(node.right) + ')'
        return '(' + self._to_str(node.left) + ' ' + node.data + ' ' + self._to_str(node.right) + ')'

    def evaluate(self, vars_dict=None):
        if vars_dict is None:
            vars_dict = {}
        return self._eval(self.root, vars_dict)

    def _eval(self, node, vars_dict):
        if node is None:
            return 0
        if isinstance(node.data, (int, float)):
            return float(node.data)
        if isinstance(node.data, str) and node.data.isalpha():
            if node.data not in vars_dict:
                raise ValueError(f"Переменная '{node.data}' не задана")
            return vars_dict[node.data]

        if node.data == '~':
            return -self._eval(node.right, vars_dict)

        l = self._eval(node.left, vars_dict)
        r = self._eval(node.right, vars_dict)
        if node.data == '+': return l + r
        if node.data == '-': return l - r
        if node.data == '*': return l * r
        if node.data == '/':
            if r == 0: raise ZeroDivisionError("Деление на ноль")
            return l / r
        raise ValueError(f"Неизвестный оператор {node.data}")

    def collect_variables(self):
        return self._collect(self.root)

    def _collect(self, node):
        if node is None:
            return set()
        if isinstance(node.data, str) and node.data.isalpha():
            return {node.data} | self._collect(node.left) | self._collect(node.right)
        return self._collect(node.left) | self._collect(node.right)

    def simplify(self):
        new_root = self._simplify(self.root)
        new_tree = Tree()
        new_tree.root = new_root
        return new_tree

    def _simplify(self, node):
        if node is None:
            return None
        left = self._simplify(node.left) if node.left else None
        right = self._simplify(node.right) if node.right else None

        if node.data in ('+', '-'):
            new = self._try_rules(left, right, node.data)
            if new is not None:
                return new

        new = Node(node.data)
        new.left = left
        new.right = right
        return new

    def _try_rules(self, a, b, op):
        if a is None or b is None or a.data != '*' or b.data != '*':
            return None

        # (f1 * f3) ± (f2 * f3) -> ((f1 ± f2) * f3)
        if self._equal(a.right, b.right):
            s = Node(op); s.left = a.left; s.right = b.left
            m = Node('*'); m.left = s; m.right = a.right
            return m

        if self._equal(a.left, b.left):
            s = Node(op); s.left = a.right; s.right = b.right
            m = Node('*'); m.left = s; m.right = a.left
            return m

        # (f1 * f2) ± (f1 * f3) -> (f1 * (f2 ± f3))
        if self._equal(a.left, b.left):
            s = Node(op); s.left = a.right; s.right = b.right
            m = Node('*'); m.left = a.left; m.right = s
            return m

        if self._equal(a.right, b.right):
            s = Node(op); s.left = a.left; s.right = b.left
            m = Node('*'); m.left = a.right; m.right = s
            return m

        return None

    def _equal(self, x, y):
        if x is None and y is None: return True
        if x is None or y is None: return False
        if x.data != y.data: return False
        return self._equal(x.left, y.left) and self._equal(x.right, y.right)


def parse_expr(s):
    s = s.replace(' ', '')
    i = 0
    n = len(s)

    def peek():
        return s[i] if i < n else None

    def next():
        nonlocal i
        c = peek()
        i += 1
        return c

    def expr():
        nonlocal i
        node = term()
        while peek() in ('+', '-'):
            op = next()
            right = term()
            new = Node(op)
            new.left = node
            new.right = right
            node = new
        return node

    def term():
        nonlocal i
        node = factor()
        while peek() in ('*', '/'):
            op = next()
            right = factor()
            new = Node(op)
            new.left = node
            new.right = right
            node = new
        return node

    def factor():
        nonlocal i
        c = peek()
        if c == '-':
            next()
            node = Node('~')
            node.right = factor()
            return node
        if c == '(':
            next()
            node = expr()
            if next() != ')':
                raise SyntaxError("Ожидалась ')'")
            return node
        if c is None:
            raise SyntaxError("Неожиданный конец")
        if c.isdigit() or c == '.':
            num = ''
            while peek() is not None and (peek().isdigit() or peek() == '.'):
                num += next()
            val = float(num) if '.' in num else int(num)
            return Node(val)
        if c.isalpha() and c.islower():
            next()
            return Node(c)
        raise SyntaxError(f"Недопустимый символ: {c}")

    root = expr()
    if peek() is not None:
        raise SyntaxError("Лишние символы")
    return root


def main():
    tree = Tree()

    while True:
        print("\n==================================================")
        print("        УПРОЩЕНИЕ ВЫРАЖЕНИЙ (задание №20)")
        print("==================================================")
        print("1. Ввести выражение")
        print("2. Вычислить значение (с подстановкой)")
        print("3. Упростить выражение")
        print("0. Выход")
        print("==================================================")
        choice = input("Выберите действие: ").strip()

        if choice == '1':
            expr = input("\nВведите выражение: ").strip()
            if not expr:
                print("Ошибка: пустое выражение")
                continue

            try:
                tree.root = parse_expr(expr)
                print("Выражение принято:", tree)
            except Exception as e:
                print("Ошибка:", e)

        elif choice == '2':
            if tree.root is None:
                print("Сначала введите выражение")
                continue
            vars_set = tree.collect_variables()
            values = {}

            if vars_set:
                print("\nПеременные:", ', '.join(sorted(vars_set)))
                for v in sorted(vars_set):
                    while True:
                        val = input(f"  {v} = ")
                        if val == '':
                            print("Введите число")
                            continue
                        try:
                            values[v] = float(val)
                            break
                        except ValueError:
                            print("Некорректное число, попробуйте снова")
            try:
                res = tree.evaluate(values)
                print("Результат:", res)
            except Exception as e:
                print("Ошибка:", e)

        elif choice == '3':
            if tree.root is None:
                print("Сначала введите выражение")
                continue
            try:
                simplified = tree.simplify()
                print("\nБыло:", tree)
                print("Стало:", simplified)
                ans = input("Заменить текущее выражение на упрощённое? (y/n): ").lower()
                if ans == 'y':
                    tree = simplified
            except Exception as e:
                print("\nОшибка упрощения:", e)

        elif choice == '0':
            print("\nПрограмма выключена.")
            break

        else:
            print("\nНеверный пункт, введите 0-3")


if __name__ == "__main__":
    main()