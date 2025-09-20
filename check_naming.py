import re
import sys
from pathlib import Path

# -----------------------------
# Config convenții Unreal
# -----------------------------
CLASS_PREFIXES = ["A", "U", "F", "E", "I"]
BOOL_PREFIX = "b"

# -----------------------------
# Funcții de verificare
# -----------------------------
def check_class(name):
    if not any(name.startswith(p) for p in CLASS_PREFIXES):
        return f"❌ Class/Struct '{name}' should start with {CLASS_PREFIXES}"
    if not name[0].isupper():
        return f"❌ Class/Struct '{name}' should be PascalCase"
    return None

def check_function(name):
    if not name[0].isupper():
        return f"❌ Function '{name}' should be PascalCase"
    return None

def check_variable(name, is_bool=False, is_member=False):
    if is_bool and not name.startswith(BOOL_PREFIX):
        return f"❌ Boolean variable '{name}' should start with 'b'"

    # PascalCase pentru membri, camelCase pentru variabile locale
    if is_member:
        if not re.match(r'^[A-Z][A-Za-z0-9]*$', name):
            return f"❌ Member variable '{name}' should be PascalCase (no underscores)"
    else:
        if not re.match(r'^[a-z][A-Za-z0-9]*$', name):
            return f"❌ Local variable '{name}' should be camelCase (no underscores)"
    return None

# -----------------------------
# Funcție principală
# -----------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 check_naming.py <folder>")
        sys.exit(1)

    path = Path(sys.argv[1])
    errors = []

    files = list(path.rglob("*.cpp")) + list(path.rglob("*.h"))

    for file in files:
        try:
            lines = file.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            print(f"⚠️ Cannot read file {file}: {e}")
            continue

        class_scope = False      # True dacă suntem în interiorul unei clase/struct
        function_scope = 0       # >0 dacă suntem în interiorul unei funcții
        brace_stack = []         # pentru a ține evidența blocurilor {}

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Ignorăm comentarii
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            # Detectare clase / struct
            m_class = re.match(r'(?:class|struct)\s+(\w+)', stripped)
            if m_class:
                err = check_class(m_class.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")
                class_scope = True

            # Detectare funcții (simplificat)
            m_func = re.match(r'(?:virtual\s+)?(?:inline\s+)?(?:static\s+)?(?:const\s+)?[\w:<>&*]+\s+(\w+)\s*\([^)]*\)\s*(?:const)?', stripped)
            if m_func and class_scope:
                err = check_function(m_func.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")
                function_scope += 1

            # Detectare variabile
            m_var = re.match(r'(?:const\s+)?([\w:<>&*]+)\s+(\w+)\s*;', stripped)
            if m_var:
                type_name = m_var.group(1)
                var_name = m_var.group(2)
                is_bool = type_name == "bool"
                # Membri: suntem în clasă și nu în funcție
                is_member = class_scope and function_scope == 0
                err = check_variable(var_name, is_bool, is_member)
                if err:
                    errors.append(f"{file}:{i} {err}")

            # Actualizare brace_stack pentru a ține evidența nesting-ului
            for char in stripped:
                if char == '{':
                    brace_stack.append('block')
                elif char == '}':
                    if brace_stack:
                        brace_stack.pop()
                        # Ieșim dintr-o funcție dacă function_scope > 0 și am închis blocul ei
                        if function_scope > 0 and len(brace_stack) < function_scope:
                            function_scope -= 1

            # Ieșim din clasă dacă stack-ul gol și nu mai suntem în funcție
            if class_scope and not brace_stack and function_scope == 0:
                class_scope = False

    # -----------------------------
    # Output
    # -----------------------------
    if errors:
        print("\n".join(errors))
        print(f"\n❌ Found {len(errors)} naming errors.")
        sys.exit(1)
    else:
        print("✅ All naming conventions passed!")
        sys.exit(0)

# -----------------------------
# Entry point
# -----------------------------
if __name__ == "__main__":
    main()
