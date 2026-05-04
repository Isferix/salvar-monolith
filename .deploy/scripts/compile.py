import platform
import re
import socket
import subprocess
from configparser import ConfigParser

CONFIG_FILE = "config.ini"
ENV_FILE = "./.deploy/.env"
GLOBAL_ENVS_FILE = "./.env" # Para las variables default del .ini, para que puedan ser utilizadas por comandos superiores como Makefile o docker-compose


def get_localhost():
    system = platform.system().lower()

    if system == "windows":
        # Windows normal
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
            if ip.startswith("127."):
                # fallback si devuelve loopback
                ip = socket.gethostbyname(socket.getfqdn())
            return ip
        except Exception:
            return "127.0.0.1"
    elif system == "linux":
        # Detectar WSL2
        try:
            with open("/proc/version") as f:
                version_info = f.read().lower()
            if "microsoft" in version_info:
                # WSL2 -> usar ip addr de eth0
                result = subprocess.run(
                    ["ip", "addr", "show", "eth0"], capture_output=True, text=True
                )
                match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/", result.stdout)
                return match.group(1) if match else "127.0.0.1"
        except FileNotFoundError:
            pass

        # Linux normal
        hostname = socket.gethostname()
        try:
            ip = socket.gethostbyname(hostname)
            return ip
        except Exception:
            return "127.0.0.1"


def compile_env(injected_vars=None):
    """
    Compila el config.ini en un .env resolviendo variables recursivamente.
    """
    parser = ConfigParser(interpolation=None)
    parser.read(CONFIG_FILE)

    # Variables globales (default) + inyectadas
    # variables = dict({key.upper(), value} for key, value in parser["default"].items()) if parser.has_section("default") else {}
    variables = {key.upper(): value for key, value in parser["default"].items()}

    if injected_vars:
        variables.update(injected_vars)

    print("Las variables para reemplazar son: ", variables)
    resolved = {}
    defaults = {}
    # Resolver todas las secciones
    for section in parser.sections():
        if section.lower() == "default":
            defaults = {f"{section.upper()}_{key.upper()}": value for key, value in parser[section].items()}   
            print("Las variables default son: ", defaults)
        for key, value in parser[section].items():
            resolved_key = f"{section.upper()}_{key.upper()}"
            resolved_value = substitute_vars(value, {**variables, **resolved})
            resolved[resolved_key] = resolved_value

    # Agregar también las globales como claves directas
    # for key, value in variables.items():
    #     resolved[key.upper()] = substitute_vars(value, {**variables, **resolved})

    # Guardar en .env
    with open(ENV_FILE, "w") as f:
        for key, value in resolved.items():
            f.write(f"{key}={value}\n")

    print(f"✅ {ENV_FILE} generado correctamente.")

    with open(GLOBAL_ENVS_FILE, "w") as f:
        for key, value in defaults.items():
            f.write(f"{key.removeprefix('DEFAULT_').upper()}={value}\n")
    print(f"✅ {GLOBAL_ENVS_FILE} generado correctamente.")

def substitute_vars(value, variables):
    """
    Reemplaza recursivamente ${VAR} por su valor en el diccionario.
    """
    pattern = re.compile(r"\$\{([^}]+)\}")

    def _substitute(s):
        match = pattern.search(s)
        while match:
            var_name = match.group(1)
            replacement = variables.get(
                var_name, match.group(0)
            )  # deja ${VAR} si no existe
            s = s[: match.start()] + replacement + s[match.end() :]
            match = pattern.search(s)
        return s

    result = _substitute(value)

    # Si aún quedan placeholders, repetir recursión
    # if pattern.search(result):
    #     return substitute_vars(result, variables)

    return result


def main():
    # Ejemplo: inyectamos LOCALHOST en el proceso de compilación
    host = get_localhost() or "127.0.0.1"
    compile_env(injected_vars={"LOCALHOST": host})


if __name__ == "__main__":
    main()