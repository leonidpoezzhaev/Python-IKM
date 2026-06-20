class Node:
    def __init__(self, coeff, degree):
        self.coeff = coeff
        self.degree = degree
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.var = 'x'

    def insert(self, coeff, degree):
        if coeff == 0:
            return

        new_node = Node(coeff, degree)
        if self.head is None:
            self.head = new_node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new_node

    def simplify(self):
        if self.head is None:
            return

        deg_map = {}
        cur = self.head
        while cur:
            deg = cur.degree
            deg_map[deg] = deg_map.get(deg, 0) + cur.coeff
            cur = cur.next

        deg_map = {d: c for d, c in deg_map.items() if c != 0}
        if not deg_map:
            self.head = None
            return

        sorted_degrees = sorted(deg_map.keys(), reverse=True)
        self.head = None
        for d in sorted_degrees:
            self.insert(deg_map[d], d)

    def to_list(self):
        result = []
        cur = self.head
        while cur:
            result.append((cur.coeff, cur.degree))
            cur = cur.next
        return result

    def __str__(self):
        if self.head is None:
            return "0"
        var = self.var
        terms = []
        cur = self.head
        while cur:
            c = cur.coeff
            d = cur.degree
            if c == 0:
                cur = cur.next
                continue

            if d == 0:
                term = str(c)

            elif d == 1:
                if c == 1:
                    term = var
                elif c == -1:
                    term = "-" + var
                else:
                    term = str(c) + var

            else:
                if c == 1:
                    term = var + "^" + str(d)
                elif c == -1:
                    term = "-" + var + "^" + str(d)
                else:
                    term = str(c) + var + "^" + str(d)

            terms.append(term)
            cur = cur.next

        result = terms[0]
        for t in terms[1:]:
            if t[0] == '-':
                result += " - " + t[1:]
            else:
                result += " + " + t
        return result

    def append_to_file(self, filename):
        with open(filename, 'a', encoding='utf-8') as f:
            f.write('\n' + str(self))

def parse(expr):
    expr = expr.replace(" ", "")
    if not expr:
        raise ValueError("Пустая строка. Введите многочлен.")

    allowed = set("0123456789+-^xy")
    for ch in expr:
        if ch not in allowed:
            raise ValueError("Недопустимый символ '" + ch + "'. Разрешены только цифры, +, -, ^, x, y.")

    if expr.count('x') > 0 and expr.count('y') > 0:
        raise ValueError("Используйте только одну переменную: либо x, либо y.")

    var = 'y' if 'y' in expr else 'x'

    if expr[0] in '+-^':
        raise ValueError("Выражение не может начинаться с оператора " + expr[0])

    if expr[-1] in '+-^':
        raise ValueError("Выражение не может заканчиваться оператором " + expr[-1])

    for i in range(len(expr)-1):
        if expr[i] in '+-' and expr[i+1] in '+-':
            raise ValueError("Два оператора подряд: " + expr[i:i+2])

        if expr[i] == '^' and expr[i+1] in '+-':
            raise ValueError("После ^ не может идти оператор")

    poly = LinkedList()
    poly.var = var

    terms = []
    current = ""
    i = 0
    while i < len(expr):
        if expr[i] in '+-' and i > 0:
            terms.append(current)
            current = expr[i]
        else:
            current += expr[i]
        i += 1

    if current:
        terms.append(current)

    for term in terms:
        if not term:
            continue

        sign = 1
        if term[0] == '-':
            sign = -1
            term = term[1:]
        elif term[0] == '+':
            term = term[1:]

        if not term:
            raise ValueError("Обнаружен пустой терм (например, '+ 2' или '- 2' без числа)")

        pos = term.find(var)
        if pos == -1:
            if not term.isdigit():
                raise ValueError("Некорректный свободный член: '" + term + "' (должно быть число)")
            coeff = sign * int(term)
            degree = 0

        else:
            coeff_str = term[:pos]
            if not coeff_str or coeff_str == '+':
                coeff = sign * 1
            elif coeff_str == '-':
                coeff = sign * -1
            else:
                if not coeff_str.isdigit():
                    raise ValueError("Некорректный коэффициент: '" + coeff_str + "' (должно быть число)")
                coeff = sign * int(coeff_str)

            if pos + 1 < len(term) and term[pos + 1] == '^':
                deg_str = term[pos + 2:]
                if not deg_str:
                    raise ValueError("После ^ должна быть степень")

                if not deg_str.isdigit():
                    raise ValueError("Степень должна быть целым числом, получено: '" + deg_str + "'")

                degree = int(deg_str)
                if degree < 0:
                    raise ValueError("Степень не может быть отрицательной: " + str(degree))
                if pos + 2 + len(deg_str) < len(term):
                    raise ValueError("Лишние символы после степени: '" + term[pos + 2 + len(deg_str):] + "'")
            else:
                degree = 1
                if pos + 1 < len(term):
                    raise ValueError("После переменной должен быть ^ или конец терма, найдено: '" + term[pos+1] + "'")

        poly.insert(coeff, degree)

    return poly

def menu():
    print("\n" + "=" * 50)
    print("        РАБОТА С МНОГОЧЛЕНАМИ (задание №8)")
    print("=" * 50)
    print("1. Ввести многочлен и вывести список")
    print("2. Привести подобные")
    print("3. Обработать файл")
    print("0. Выход")
    print("=" * 50)

def main():
    while True:
        menu()
        choice = input("Выберите действие: ").strip()
        if choice == '0':
            print("До свидания!")
            break

        elif choice == '1':
            expr = input("\nВведите многочлен: ").strip()
            try:
                poly = parse(expr)
                print("\nСписок (коэффициент, степень):", poly.to_list())
            except ValueError as e:
                print("\nОшибка ввода:", e)
            except Exception as e:
                print("\nНепредвиденная ошибка:", e)

        elif choice == '2':
            expr = input("\nВведите многочлен: ").strip()
            try:
                poly = parse(expr)
                poly.simplify()
                print("\nПосле приведения подобных:", poly)
            except ValueError as e:
                print("\nОшибка ввода:", e)
            except Exception as e:
                print("\nНепредвиденная ошибка:", e)

        elif choice == '3':
            fname = input("\nВведите имя файла: ").strip()
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                if not content:
                    print("\nФайл пуст.")
                    continue

                poly = parse(content)
                poly.simplify()
                poly.append_to_file(fname)
                print("\nМногочлен обработан и дописан в конец файла.")
                print("Результат:", poly)

            except FileNotFoundError:
                print("\nОшибка: файл не найден.")

            except ValueError as e:
                print("\nОшибка в содержимом файла:", e)

            except Exception as e:
                print("\nНепредвиденная ошибка:", e)

        else:
            print("\nНеверный пункт, выберите 0–3.")

if __name__ == "__main__":
    main()