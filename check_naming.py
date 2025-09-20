import re
import sys
from pathlib import Path

# Config convenții Unreal
CLASS_PREFIXES = ["A", "U", "F", "E", "I"]
BOOL_PREFIX = "b"

def check_class(name):
    if not any(name.startswith(p) for p in CLASS_PREFIXES):
        return f"❌ Class '{name}' should start with {CLASS_PREFIXES}"
    if not name[0].isupper():
        return f"❌ Class '{name}' should be PascalCase"
    return None

def check_function(name):
    if not name[0].isupper():
        return f"❌ Function '{name}' should be PascalCase"
    return None

def check_variable(name, is_bool=False, is_member=False):
    if is_bool and not name.startswith(BOOL_PREFIX):
        return f"❌ Boolean variable '{name}' should start with 'b'"
    if is_member:
        if not name[0].isupper():
            return f"❌ Member variable '{name}' should be PascalCase"
    else:
        if not name[0].islower():
            return f"❌ Local variable '{name}' should be camelCase"
    return None

def main():
    path = Path(sys.argv[1])
    errors = []

    for file in path.rglob("*.[ch]pp"):
        lines = file.read_text(encoding="utf-8").splitlines()
        for i, line in enumerate(lines, start=1):
            # Clasa
            m_class = re.match(r'\s*class\s+(\w+)', line)
            if m_class:
                err = check_class(m_class.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")

            # Funcții
            m_func = re.match(r'\s*(?:void|int|float|bool|[\w:<>]+)\s+(\w+)\s*\(', line)
            if m_func:
                err = check_function(m_func.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")

            # Variabile membre (simplu detect: ';' la final)
            m_var = re.match(r'\s*(bool|int|float|double|[\w:<>]+)\s+(\w+)\s*;', line)
            if m_var:
                type_name = m_var.group(1)
                var_name = m_var.group(2)
                is_bool = type_name == "bool"
                # presupunem că toate variabilele cu literă mare la început sunt membre
                is_member = var_name[0].isupper()
                err = check_variable(var_name, is_bool, is_member)
                if err:
                    errors.append(f"{file}:{i} {err}")

    if errors:
        print("\n".join(errors))
        sys.exit(1)

if __name__ == "__main__":
    main()
