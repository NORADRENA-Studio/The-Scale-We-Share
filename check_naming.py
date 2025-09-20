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

    # PascalCase pentru membri, camelCase pentru locale
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

        in_class = False
        in_function = False
        pending_class = False
        pending_function = False
        class_brace_level = 0
        function_brace_level = 0

        for i, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Ignorăm comentarii
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            # Detectare class/struct
            m_class = re.match(r'(?:class|struct)\s+(\w+)', stripped)
            if m_class:
                err = check_class(m_class.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")
                pending_class = True
                continue

            # Detectare funcție (doar dacă suntem în clasă)
            m_func = re.match(r'(?:virtual\s+)?(?:inline\s+)?(?:static\s+)?(?:const\s+)?[\w:<>&*]+\s+(\w+)\s*\([^)]*\)\s*(?:const)?', stripped)
            if m_func and in_class:
                err = check_function(m_func.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")
                pending_function = True
                continue

            # Dacă apare { activăm pending_class sau pending_function
            if '{' in stripped:
                if pending_class:
                    in_class = True
                    class_brace_level = 1
                    pending_class = False
                elif pending_function:
                    in_function = True
                    function_brace_level = 1
                    pending_function = False
                else:
                    # alt block (if/for/while)
                    if in_function:
                        function_brace_level += 1
                    elif in_class:
                        class_brace_level += 1

            # Dacă apare } scădem nivelul corespunzător
            if '}' in stripped:
                count = stripped.count('}')
                if in_function:
                    function_brace_level -= count
                    if function_brace_level <= 0:
                        in_function = False
                        function_brace_level = 0
                elif in_class:
                    class_brace_level -= count
                    if class_brace_level <= 0:
                        in_class = False
                        class_brace_level = 0

            # Detectare variabilă
            m_var = re.match(r'(?:const\s+)?([\w:<>&*]+)\s+(\w+)\s*;', stripped)
            if m_var:
                type_name = m_var.group(1)
                var_name = m_var.group(2)
                is_bool = type_name == "bool"
                # Membri: in_class True și in_function False
                is_member = in_class and not in_function
                err = check_variable(var_name, is_bool, is_member)
                if err:
                    errors.append(f"{file}:{i} {err}")

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
