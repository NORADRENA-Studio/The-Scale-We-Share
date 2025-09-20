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

    # Verificare stricată PascalCase / camelCase fără underscore
    if is_member:
        # PascalCase: prima literă mare, fără underscore
        if not re.match(r'^[A-Z][A-Za-z0-9]*$', name):
            return f"❌ Member variable '{name}' should be PascalCase (no underscores)"
    else:
        # camelCase: prima literă mică, fără underscore
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

    # Prind toate .cpp și .h
    files = list(path.rglob("*.cpp")) + list(path.rglob("*.h"))

    for file in files:
        try:
            lines = file.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            print(f"⚠️ Cannot read file {file}: {e}")
            continue

        for i, line in enumerate(lines, start=1):
            line = line.strip()
            
            # Ignore comments
            if line.startswith("//") or line.startswith("/*") or line.startswith("*"):
                continue

            # 1️⃣ Clasă / Struct
            m_class = re.match(r'(?:class|struct)\s+(\w+)', line)
            if m_class:
                err = check_class(m_class.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")

            # 2️⃣ Funcție
            m_func = re.match(r'(?:virtual\s+)?(?:inline\s+)?(?:static\s+)?(?:const\s+)?[\w:<>&*]+\s+(\w+)\s*\([^)]*\)\s*(?:const)?', line)
            if m_func:
                err = check_function(m_func.group(1))
                if err:
                    errors.append(f"{file}:{i} {err}")

            # 3️⃣ Variabilă
            m_var = re.match(r'(?:const\s+)?([\w:<>&*]+)\s+(\w+)\s*;', line)
            if m_var:
                type_name = m_var.group(1)
                var_name = m_var.group(2)
                is_bool = type_name == "bool"
                # Membru: PascalCase sau prefix 'm'
                is_member = var_name[0].isupper() or var_name.startswith("m")
                err = check_variable(var_name, is_bool, is_member)
                if err:
                    errors.append(f"{file}:{i} {err}")

    # -----------------------------
    # Output și exit code
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
