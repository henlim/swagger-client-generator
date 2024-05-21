#!/usr/bin/env python3
"""
    The Python script automates the process of downloading and generating client code from a Swagger API
    specification, with options to replace security definitions and customize the generated code.
"""
# The above Python code is importing the `shutil` module, which provides a higher-level interface for
# file operations. However, the code snippet provided does not include any specific operations or
# functions being called from the `shutil` module.
import shutil

# The above Python code is importing necessary modules such as `os`, `urllib.request`, `re`, and
# `load_dotenv`. It is also importing specific functions from the `os` module using `from os import
# path`. The code seems to be setting up the environment for working with files, making HTTP requests,
# handling regular expressions, and loading environment variables from a `.env` file.
import os
from os import path
import urllib.request
import re
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
# The above code is likely using the `load_dotenv()` function to load environment variables from a
# .env file into the current environment. This is a common practice in Python applications to keep
# sensitive information, such as API keys or database credentials, out of the codebase and stored
# securely in a separate file.
load_dotenv()

# The line `BASE_DIR = os.path.realpath(os.path.dirname(__file__))` in the Python script is used to
# get the absolute path of the directory where the current Python script is located. Here's a
# breakdown of what each part of the code does:
BASE_DIR = os.path.realpath(os.path.dirname(__file__))
# The line `CREDENTIALS_PATH = path.join(BASE_DIR, ".env")` is creating a variable `CREDENTIALS_PATH`
# that stores the absolute path to a file named `.env` within the directory specified by `BASE_DIR`.
# This file is typically used to store sensitive information such as API keys, tokens, or other
# credentials required for the script to interact with external services securely.
CREDENTIALS_PATH = path.join(BASE_DIR, ".env")

# The line `SWAGGER_CODEGEN_CLI_VERSION = os.getenv('CODEGEN_CLI_VERSION')` is retrieving the value of
# an environment variable named `CODEGEN_CLI_VERSION` using the `os.getenv()` function and assigning
# it to the variable `SWAGGER_CODEGEN_CLI_VERSION`. This environment variable likely stores the
# version number of the Swagger Codegen CLI that the script will use for generating client code from a
# Swagger API specification. This approach allows for flexibility in specifying the version of the
# Swagger Codegen CLI to be used without hardcoding it in the script, making it easier to manage and
# update the version as needed.
SWAGGER_CODEGEN_CLI_VERSION = os.getenv('CODEGEN_CLI_VERSION')
# The above code is attempting to retrieve the value of the environment variable 'API_ENDPOINT' using
# the `os.getenv()` function in Python. This value is then assigned to the variable `API_ENDPOINT`.
API_ENDPOINT = os.getenv('API_ENDPOINT')
# The above code is attempting to retrieve the value of the environment variable 'API_TOKEN' using the
# `os.getenv()` function in Python. This value is then assigned to the variable `API_TOKEN`.
API_TOKEN = os.getenv('API_TOKEN')

# The above code is defining a variable `TMP_PATH` and setting its value to the result of joining the
# `BASE_DIR` variable with the string `".swagger-assets"`. The `path.join()` function is typically
# used to concatenate parts of a file path in a platform-independent way.
TMP_PATH = path.join(BASE_DIR, ".swagger-assets")

# The above code is setting the `SWAGGER_CODEGEN_CLI_PATH` variable to the path of the
# `swagger-codegen-cli.jar` file located in the `TMP_PATH` directory.
SWAGGER_CODEGEN_CLI_PATH = path.join(TMP_PATH, "swagger-codegen-cli.jar")
# The code is defining a Python constant `BACKEND_OPENAPI_SPECIFICATION_PATH` with a value that is the
# result of joining the `TMP_PATH` variable with the string `"swagger_backend_openapi.json"` using the
# `path.join()` function. This code is likely used to create a file path for a Swagger/OpenAPI
# specification file in a backend application.
BACKEND_OPENAPI_SPECIFICATION_PATH = path.join(TMP_PATH, "swagger_backend_openapi.json")
# The above code is defining a variable `FETCH_CLIENT_PATH` and setting its value to be the result of
# joining the `TMP_PATH` and the string "swagger-client" using the `path.join()` function.
FETCH_CLIENT_PATH = path.join(TMP_PATH, "swagger-client")
# The code is defining a variable `CLIENT_PATH_YAML` that stores the path to a file named
# "swagger.yaml" located in the directory specified by the variable `TMP_PATH`. The `path.join()`
# function is used to concatenate the directory path specified by `TMP_PATH` with the file name
# "swagger.yaml" to create the complete file path.
CLIENT_PATH_YAML = path.join(TMP_PATH, "swagger.yaml")

# The above code is setting the `GENERATED_CODE_OUTPUT_PATH` variable to a specific path within the
# project directory. It is using the `path.join()` function to concatenate the `BASE_DIR` variable
# with the subdirectories "src", "lib", and "swagger-client" to create the final output path.
GENERATED_CODE_OUTPUT_PATH = path.join(BASE_DIR, "src", "lib", "swagger-client")

# The above code is setting the environment variable "REPLACE_SECURITY_DEFINITIONS" to the value
# "false" if it is not already set. This can be useful for configuring the behavior of the program
# based on the value of this environment variable.
os.environ.setdefault("REPLACE_SECURITY_DEFINITIONS", "false")
# The above code in Python is setting the environment variable "DOWNLOAD_CLIENT_CODE" to the value
# "true" if it is not already set. This can be useful for configuring the behavior of a program based
# on environment variables.
os.environ.setdefault("DOWNLOAD_CLIENT_CODE", "true")

# The above code is checking if the environment variable `REPLACE_SECURITY_DEFINITIONS` is set to the
# string "true" (case-insensitive comparison). If it is, then the variable
# `REPLACE_SECURITY_DEFINITIONS` will be set to `True`, otherwise it will be set to `False`.
REPLACE_SECURITY_DEFINITIONS = os.environ.get("REPLACE_SECURITY_DEFINITIONS").lower() == "true"
# The above code is checking if the environment variable `DOWNLOAD_CLIENT_CODE` is set to the string
# "true" (case-insensitive comparison). If it is, the variable `DOWNLOAD_CLIENT_CODE` will be set to
# `True`, otherwise it will be set to `False`.
DOWNLOAD_CLIENT_CODE = os.environ.get("DOWNLOAD_CLIENT_CODE").lower() == "true"

def check_java():
    """
    The function `check_java()` checks if Java is installed on the system and prints a message
    accordingly.
    """
    if shutil.which("java") is None:
        print("❌ Java não está instalado")
        exit(1)
    print("✅ Java instalado")

def check_tmp_dir():
    """
    This Python function checks if a temporary directory exists and creates it if it doesn't.
    """
    if not path.exists(TMP_PATH):
        print(f"❗ Criando diretório {TMP_PATH}")
        os.mkdir(TMP_PATH)
    print(f"✅ Diretório {TMP_PATH}")

def check_swagger_gen_cli():
    """
    This Python function checks if the Swagger Codegen CLI file exists, downloads it if not, and prints
    status messages accordingly.
    """
    if not path.exists(SWAGGER_CODEGEN_CLI_PATH):
        print(f"❗ Arquivo {SWAGGER_CODEGEN_CLI_PATH} não localizado")
        swagger_codegen_cli_url = (
            f"https://repo1.maven.org/maven2/io/swagger/codegen/v3/"
            f"swagger-codegen-cli/{SWAGGER_CODEGEN_CLI_VERSION}/"
            f"swagger-codegen-cli-{SWAGGER_CODEGEN_CLI_VERSION}.jar"
        )
        try:
            print(f"📥 Baixando o arquivo {swagger_codegen_cli_url} ...")
            with urllib.request.urlopen(swagger_codegen_cli_url) as response:
                with open(SWAGGER_CODEGEN_CLI_PATH, "wb") as file:
                    file.write(response.read())
        except Exception as ex:
            print("❌ Erro ao baixar o arquivo swagger-codegen-cli.jar:", ex)
            exit(1)
    print("✅ swagger-codegen-cli.jar baixado")

def download_backend_openapi(api_url, api_key):
    """
    The function `download_backend_openapi` downloads the OpenAPI specification from a given API URL
    using a provided API key and saves it to a specified file path.
    
    :param api_url: The `api_url` parameter is the URL of the backend API from which you want to
    download the OpenAPI specification. This URL should point to the root of the API and include the
    necessary path to access the OpenAPI documentation
    :param api_key: The `api_key` parameter is a security token or key that is used to authenticate and
    authorize access to the API. It is typically provided by the API provider to the API consumer for
    accessing protected resources
    """
    try:
        backend_openapi_url = f"{api_url}/?format=json"
        request = urllib.request.Request(backend_openapi_url)
        request.add_header("Authorization", f"Token {api_key}")
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            if REPLACE_SECURITY_DEFINITIONS:
                data = replace_security_definitions(data)
        with open(BACKEND_OPENAPI_SPECIFICATION_PATH, "w", encoding='utf8') as file:
            file.write(data)
        print("✅ Endpoints do Backend gerados pelo Swagger baixado")
    except Exception as ex:
        print("❌ Erro ao baixar os endpoints do Backend gerados pelo Swagger:", ex)
        exit(1)

def replace_security_definitions(data):
    """
    The function `replace_security_definitions` replaces a specific security definition in a JSON data
    string with a new security definition.
    
    :param data: The `replace_security_definitions` function takes a string `data` as input and uses
    regular expressions to replace a specific pattern related to security definitions in the input
    string. The pattern being replaced is related to security definitions for Basic authentication and
    an empty array for Basic security in the input JSON data
    :return: The `replace_security_definitions` function takes a string `data` as input and uses regular
    expressions to replace a specific pattern related to security definitions in the input string. The
    function replaces the existing security definitions with a new set of security definitions that
    include both "Basic" and "TokenAuth" types.
    """
    return re.sub(
        r'"securityDefinitions": {"Basic": {"type": "basic"}},'
        r'"security": \[{"Basic": \[]}]',
        '''
        "securityDefinitions": { "Basic": { "type": "basic" },
        "TokenAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Token-based authentication with required prefix \\"Token\\"" } },
        "security": [{ "Basic": [] }, { "TokenAuth": [] }]
        ''',
        data
    )

def generate_client_code():
    """
    This Python function generates a client code using a Swagger Codegen CLI command.
    """
    print("📥 Gerando o código cliente ...")
    if path.exists(FETCH_CLIENT_PATH):
        shutil.rmtree(FETCH_CLIENT_PATH)
    try:
        cmd = f"""java -jar {SWAGGER_CODEGEN_CLI_PATH}\n
        generate -i {BACKEND_OPENAPI_SPECIFICATION_PATH}\n
        -l typescript-axios\n
        --additional-properties\n
        modelPropertyNaming=original -o {FETCH_CLIENT_PATH}"""
        os.system(cmd)
        print("✅ Código cliente gerado")
        if path.exists(BACKEND_OPENAPI_SPECIFICATION_PATH):
            os.remove(BACKEND_OPENAPI_SPECIFICATION_PATH)
            print("✅ Removido arquivo de endpoints baixado")
    except Exception as ex:
        print("❌ Erro ao gerar o código cliente:", ex)
        exit(1)

def download_client_code(api_url, api_key):
    """
    This Python function downloads client code using a specified API URL and API key by executing a Java
    command with specific parameters.
    
    :param api_url: The `api_url` parameter is the URL of the API from which you want to download the
    client code. It is used to specify the location of the API's OpenAPI specification document
    :param api_key: The `api_key` parameter is typically an authentication token or key that is used to
    authenticate and authorize access to an API. In this specific code snippet, the `api_key` is being
    used to set the authorization header in the API request when downloading the client code. This helps
    ensure that only authorized
    """
    print("📥 Baixando o código cliente ...")
    if path.exists(FETCH_CLIENT_PATH):
        shutil.rmtree(FETCH_CLIENT_PATH)
    try:
        cmd = (
            f'java -jar {SWAGGER_CODEGEN_CLI_PATH} generate '
            f'-i {api_url}/?format=json '
            f'-a "Authorization: Token {api_key}" '
            f'-l typescript-axios '
            f'--additional-properties modelPropertyNaming=original '
            f'-o {FETCH_CLIENT_PATH}'
        )
        os.system(cmd)
        print("✅ Código cliente baixado")
    except Exception as ex:
        print("❌ Erro ao baixar o código cliente:", ex)
        exit(1)

def remove_files():
    """
    The function `remove_files` removes specific files from a directory if they exist.
    """
    files = [
        path.join(FETCH_CLIENT_PATH, ".gitignore"),
        path.join(FETCH_CLIENT_PATH, ".swagger-codegen-ignore"),
        path.join(FETCH_CLIENT_PATH, "api_test.spec.ts"),
        path.join(FETCH_CLIENT_PATH, "git_push.sh"),
        path.join(FETCH_CLIENT_PATH, ".npmignore"),
        path.join(FETCH_CLIENT_PATH, "package.json"),
        path.join(FETCH_CLIENT_PATH, "tsconfig.json"),
        path.join(FETCH_CLIENT_PATH, "README.md"),
    ]
    for file in files:
        if path.exists(file):
            os.remove(file)
    print("✅ Arquivos não utilizados do código cliente removidos")

def replaces_in_code():
    """
    The function `replaces_in_code` performs multiple string replacements in a specified file to update
    certain code patterns.
    """
    api_file_path = path.join(FETCH_CLIENT_PATH, "api.ts")
    if not path.exists(api_file_path):
        print(f"❌ O arquivo {api_file_path} não existe")
        exit(1)
    with open(api_file_path, "r", encoding='utf8') as filein:
        data = filein.read()
        data = re.sub(
            r"const BASE_PATH.+",
            r'''const BASE_PATH = `${process.env.NEXT_PUBLIC_API_URL}`
            .replace(/\/+$/, "");''',
            data
        )
        data = re.sub(
            r"protected configuration: Configuration;",
            r'protected configuration?: Configuration;', data)
        data = re.sub(
            r'''export class RequiredError extends Error\n.+name: "RequiredError"''',
            r'export class RequiredError extends Error {', data)
        data = re.sub(
            r'delete localVarUrlObj.search;',
            r'localVarUrlObj.search = null;', data)
    with open(api_file_path, "w", encoding='utf8') as fileout:
        fileout.write(data)
        print("✅ Realizado substituições no código")

def remove_old_code():
    """
    This Python function removes a directory if it exists.
    """
    if path.exists(GENERATED_CODE_OUTPUT_PATH):
        shutil.rmtree(GENERATED_CODE_OUTPUT_PATH)
        print(f"✅ Removido o diretório {GENERATED_CODE_OUTPUT_PATH}")

def copy_new_code():
    """
    The `copy_new_code` function copies new code from a specified path to another path and then removes
    the original code from a temporary directory.
    """
    shutil.copytree(FETCH_CLIENT_PATH, GENERATED_CODE_OUTPUT_PATH)
    print(f"✅ Copiado novo código para o diretório {GENERATED_CODE_OUTPUT_PATH}")
    shutil.rmtree(FETCH_CLIENT_PATH)
    print(f"✅ Removido código cliente do diretório {TMP_PATH}")

def main():
    """
    The main function performs a series of checks, downloads client code or backend OpenAPI based on a
    condition, generates client code, and performs file operations.
    """
    check_java()
    check_tmp_dir()
    check_swagger_gen_cli()
    if DOWNLOAD_CLIENT_CODE:
        download_client_code(API_ENDPOINT, API_TOKEN)
    else:
        download_backend_openapi(API_ENDPOINT, API_TOKEN)
        generate_client_code()
    remove_files()
    replaces_in_code()
    remove_old_code()
    copy_new_code()

if __name__ == "__main__":
    main()
