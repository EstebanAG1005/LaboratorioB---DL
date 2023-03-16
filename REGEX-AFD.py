from copy import deepcopy
import time
from graphviz import Digraph


class RegexNode:

    # Funcion para obtener los valores dentro de los parentesis
    @staticmethod
    def recortar_corchetes(regex):
        while regex[0] == "(" and regex[-1] == ")":
            regex = regex[1:-1]
        return regex

    # Funcion que revisa el regex para ver si es concatenacion
    @staticmethod
    def concatenacion(c):
        return c == "(" or RegexNode.es_letra(c)

    # Funcion que revisa si es parte del alfabeto
    @staticmethod
    def es_letra(c):
        return c in alfabeto

    # Se inicializan los valores
    def __init__(self, regex):
        self.nullable = None
        self.firstpos = []
        self.lastpos = []
        self.item = None
        self.position = None
        self.Hijos = []

        # Chquea si es una hoja
        if len(regex) == 1 and self.es_letra(regex):
            # Si es una hoja
            self.item = regex
            # Chequa si contiene epsilon
            if usar_epsilon:
                if self.item == epsilon:
                    self.nullable = True
                else:
                    self.nullable = False
            else:
                self.nullable = False
            return

        # Si es un nodo interno
        # Encontrar los operadores más a la izquierda en los tres operadores

        kleene = -1
        or_p = -1
        concatenation = -1
        i = 0

        # Obtener el resto de los terminos
        while i < len(regex):
            if regex[i] == "(":
                # Bloque compuesto de parentsis
                nivel_brackets = 1
                # hace skip del termino
                i += 1
                while nivel_brackets != 0 and i < len(regex):
                    if regex[i] == "(":
                        nivel_brackets += 1
                    if regex[i] == ")":
                        nivel_brackets -= 1
                    i += 1
            else:
                # Pasa al siguiente caracter
                i += 1

            # Se encuentra una concatenación en la iteración anterior y es el ultimo termino
            if i == len(regex):
                break

            # Chquea si es una concatenacion
            if self.concatenacion(regex[i]):
                if concatenation == -1:
                    concatenation = i
                continue
            # Chequea si es kleene
            if regex[i] == "*":
                if kleene == -1:
                    kleene = i
                continue
            # Chequea si tiene un or
            if regex[i] == "|":
                if or_p == -1:
                    or_p = i

        # Setea la opeacion por prioridad
        if or_p != -1:
            # Encuentra un or
            self.item = "|"
            self.Hijos.append(RegexNode(self.recortar_corchetes(regex[:or_p])))
            self.Hijos.append(RegexNode(self.recortar_corchetes(regex[(or_p + 1) :])))
        elif concatenation != -1:
            # Encuentra una concatenacion
            self.item = "."
            self.Hijos.append(RegexNode(self.recortar_corchetes(regex[:concatenation])))
            self.Hijos.append(RegexNode(self.recortar_corchetes(regex[concatenation:])))
        elif kleene != -1:
            # encuentra un kleene
            self.item = "*"
            self.Hijos.append(RegexNode(self.recortar_corchetes(regex[:kleene])))

    def calc_functions(self, pos, followpos):
        # Es una hoja
        if self.es_letra(self.item):
            self.firstpos = [pos]
            self.lastpos = [pos]
            self.position = pos
            # Agrega la posición en la lista de followpos
            followpos.append([self.item, []])
            return pos + 1
        # Si es un nodo interno
        for Hijo in self.Hijos:
            pos = Hijo.calc_functions(pos, followpos)
        # Calcula la expresion actual

        if self.item == ".":
            # Si es concatenacion
            # Firstpos
            if self.Hijos[0].nullable:
                self.firstpos = sorted(
                    list(set(self.Hijos[0].firstpos + self.Hijos[1].firstpos))
                )
            else:
                self.firstpos = deepcopy(self.Hijos[0].firstpos)
            # Lastpos
            if self.Hijos[1].nullable:
                self.lastpos = sorted(
                    list(set(self.Hijos[0].lastpos + self.Hijos[1].lastpos))
                )
            else:
                self.lastpos = deepcopy(self.Hijos[1].lastpos)
            # Nullable
            self.nullable = self.Hijos[0].nullable and self.Hijos[1].nullable
            # Followpos
            for i in self.Hijos[0].lastpos:
                for j in self.Hijos[1].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        elif self.item == "|":
            # Si es un or
            # Firstpos
            self.firstpos = sorted(
                list(set(self.Hijos[0].firstpos + self.Hijos[1].firstpos))
            )
            # Lastpos
            self.lastpos = sorted(
                list(set(self.Hijos[0].lastpos + self.Hijos[1].lastpos))
            )
            # Nullable
            self.nullable = self.Hijos[0].nullable or self.Hijos[1].nullable

        elif self.item == "*":
            # Si es un kleene
            # Firstpos
            self.firstpos = deepcopy(self.Hijos[0].firstpos)
            # Lastpos
            self.lastpos = deepcopy(self.Hijos[0].lastpos)
            # Nullable
            self.nullable = True
            # Followpos
            for i in self.Hijos[0].lastpos:
                for j in self.Hijos[0].firstpos:
                    if j not in followpos[i][1]:
                        followpos[i][1] = sorted(followpos[i][1] + [j])

        # print('otro')
        # print(pos)
        return pos

    print(" ")
    print("nivel--item--firstpos--lastpos--nullable--posicion")

    def write_level(self, level):

        print(
            str(level) + " " + self.item,
            self.firstpos,
            self.lastpos,
            self.nullable,
            "" if self.position == None else self.position,
        )
        for Hijo in self.Hijos:
            Hijo.write_level(level + 1)


class RegexTree:
    def __init__(self, regex):
        self.root = RegexNode(regex)
        self.followpos = []
        self.functions()

    def write(self):
        self.root.write_level(0)

    def functions(self):
        positions = self.root.calc_functions(0, self.followpos)
        # print(self.followpos)

    def to_graphviz(self):
        # Create a new Digraph object
        dot = Digraph()

        # Add nodes to the graph
        for i, q in enumerate(self.Q):
            if i == self.q0:
                # Mark the initial state
                dot.node(str(i), label=str(i), shape="circle", style="bold")
            elif i in self.F:
                # Mark the accepting states
                dot.node(str(i), label=str(i), shape="doublecircle")
            else:
                dot.node(str(i), label=str(i))

        # Add edges to the graph
        for i, q in enumerate(self.Q):
            for a in self.V:
                if a in self.d[i]:
                    j = self.d[i][a]
                    dot.edge(str(i), str(j), label=a)

        return dot

    def toAFD(self):
        def contains_hashtag(q):
            for i in q:
                if self.followpos[i][0] == "#":
                    return True
            return False

        M = []  # Estados marcados
        Q = (
            []
        )  # Lista de estados en el formulario de seguimiento (matriz de posiciones)
        V = alfabeto - {"#", epsilon if usar_epsilon else ""}  # Alfabeto del automata
        d = []  # Array que contiene las transiciones de AFD resultante
        F = []  # Estado final
        q0 = self.root.firstpos

        Q.append(q0)
        if contains_hashtag(q0):
            F.append(Q.index(q0))

        while len(Q) - len(M) > 0:
            # Mientras existan estados sin marcar
            q = [i for i in Q if i not in M][0]
            # Se genera el array para el nuevo estado
            d.append({})
            # Se marca el estado
            M.append(q)
            # Para cada letra del alfabeto
            for a in V:
                # Se calcula el estado destino ( d(q,a) = U )
                U = []
                # Se calcula U para cada posicion de los estados
                for i in q:
                    # Si i tiene una etiqueta a
                    if self.followpos[i][0] == a:
                        # Añadimos la posición a la composición de U
                        U = U + self.followpos[i][1]
                U = sorted(list(set(U)))
                # Chequea si el estado es valido
                if len(U) == 0:
                    # Sin posiciones no se genera un estado nuevo
                    continue
                if U not in Q:
                    Q.append(U)
                    if contains_hashtag(U):
                        F.append(Q.index(U))
                d[Q.index(q)][a] = Q.index(U)
                g = Digraph("G", filename="regex_tree.gv")
            for q in Q:
                # Set final state attributes
                attrs = {}
                if q in F:
                    attrs["shape"] = "doublecircle"
                if q == Q.index(q0):
                    attrs["color"] = "blue"

            for i, row in enumerate(d):
                for a, j in row.items():
                    # Add transition to graph
                    g.edge(str(i), str(j), label=a)
            g.view()
        return AFD(Q, V, d, Q.index(q0), F)


class AFD:
    def __init__(self, Q, V, d, q0, F):
        self.Q = Q
        self.V = V
        self.d = d
        self.q0 = q0
        self.F = F

    def run(self, cadena):
        # Chequea si la entrada está en el alfabeto actual
        if len(set(cadena) - self.V) != 0:
            # No todos los caracteres están en el idioma.
            print(
                "caracteres erroneos",
                (set(cadena) - self.V),
                "caracteres no son parte del alfabeto",
            )
            exit(0)

        # Correr el Automata
        q = self.q0
        for i in cadena:
            # Chequea si existe la transicion
            if q >= len(self.d):
                print("No se acepta la cadena, No exsite la transicion")
                exit(0)
            if i not in self.d[q].keys():
                print(
                    "No se acepta la cadena, el estado no tiene transiciones con el carácter"
                )
                exit(0)
            # Se ejecuta la transicion
            q = self.d[q][i]

        if q in self.F:
            print("Cadena es parte del automata")
        else:
            print("No se acepta la cadena, termina en un estado no final")

    def write(self):
        for i in range(len(self.Q)):
            # imprime el index del Array que contiene las transiciones del AFD resultante
            print(i, self.d[i])


# Prepara la expresion para ser evaluada
def pre_proceso(regex):
    regex = regex.replace(" ", "")
    regex = "(" + regex + ")" + "#"
    return regex


# Funcion que regresa el alfabeto de la expresion
def gen_alfabeto(regex):
    return set(regex) - set("()|*")


def is_valid_regex(regex):
    stack = []
    regex_characters = set("()|*")
    regex_count = {char: 0 for char in regex_characters}

    for char in regex:
        if char in regex_characters:
            regex_count[char] += 1

        if char == "(":
            stack.append(char)
        elif char == ")":
            if not stack or stack[-1] != "(":
                return False
            stack.pop()

    if stack:
        return False

    if regex_count["*"] > (regex_count["("] + regex_count["|"]):
        return False

    return True


# Function to check if the regex is valid
def check_regex_validity(regex):
    valid_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789()|*"
    )
    invalid_chars = set(regex) - valid_chars
    if invalid_chars:
        raise ValueError(
            f"Invalid characters found in the regex: {', '.join(invalid_chars)}"
        )
    return True


# Valores iniciales
usar_epsilon = True
epsilon = "ϵ"
alfabeto = None

# Main
regex = "(a|b)*"
# regex = "(a*|b*)c"

# Validate the regex
check_regex_validity(regex)

if is_valid_regex(regex):
    # Procesa el Regex y genera el alfabeto del mismo
    t0 = time.perf_counter()
    p_regex = pre_proceso(regex)
    alfabeto = gen_alfabeto(p_regex)

    # Construccion de regex a afd
    tree = RegexTree(p_regex)
    tree.write()
    AFD = tree.toAFD()

    # Se simula la cadena predeterminada
    evaluar_cadena = "babbaaaaa"

    # prints finales para mostrar AFD resutante
    print("Regex: " + regex)
    print("Alfabeto : " + "".join(sorted(alfabeto)))
    print("Automata AFD resultante: \n")
    AFD.write()
    print('\nSimulacion en base a la cadena"' + evaluar_cadena + '" : \n')
    AFD.run(evaluar_cadena)
    print("")
else:
    print("Invalid regex")
