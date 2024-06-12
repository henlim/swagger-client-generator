#!/usr/bin/env python3

import os
from os import path
import subprocess
import urllib.request
import re
import shutil
from dotenv import load_dotenv
import getpass
import json

# Diretório base do script
BASE_DIR = os.path.realpath(os.path.dirname(__file__))

# Caminho para o arquivo .env.development
CREDENTIALS_PATH = path.join(BASE_DIR, ".env.development")

# Carrega variáveis de ambiente do arquivo .env.development
load_dotenv(dotenv_path=CREDENTIALS_PATH)

# Variáveis de ambiente
SWAGGER_CODEGEN_CLI_VERSION = os.getenv('CODEGEN_CLI_VERSION')
API_ENDPOINT = os.getenv('API_ENDPOINT')
API_TOKEN = os.getenv('API_TOKEN')
SWAGGER_SCHEMA_FORMAT = os.getenv('SWAGGER_SCHEMA_FORMAT')

# Caminhos temporários e de saída
TMP_PATH = path.join(BASE_DIR, ".tmp")
SWAGGER_CODEGEN_CLI_PATH = path.join(TMP_PATH, "swagger-codegen-cli.jar")
BACKEND_OPENAPI_SPECIFICATION_PATH = path.join(
    TMP_PATH, "swagger_backend_openapi.json")
FETCH_CLIENT_PATH = path.join(TMP_PATH, "swagger-client")
CLIENT_PATH_YAML = path.join(TMP_PATH, "swagger.yaml")
GENERATED_CODE_OUTPUT_PATH = path.join(
    BASE_DIR, "src", "lib", "fetch-client")

# Variáveis de ambiente padrão
os.environ.setdefault("REPLACE_SECURITY_DEFINITIONS", "false")
os.environ.setdefault("DOWNLOAD_CLIENT_CODE", "true")

REPLACE_SECURITY_DEFINITIONS = os.environ.get(
    "REPLACE_SECURITY_DEFINITIONS").lower() == "true"
DOWNLOAD_CLIENT_CODE = os.environ.get("DOWNLOAD_CLIENT_CODE").lower() == "true"


def check_java():
    if shutil.which("java") is None:
        print("❌ Java não está instalado")
        exit(1)
    print("✅ Java instalado")


def check_tmp_dir():
    if not path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)
    print(f"✅ Diretório {TMP_PATH} criado/existente")


def check_swagger_gen_cli():
    if SWAGGER_CODEGEN_CLI_VERSION is None:
        print("""❌ A variável CODEGEN_CLI_VERSION
              não está definida no arquivo .env""")
        exit(1)

    if not path.exists(SWAGGER_CODEGEN_CLI_PATH):
        swagger_codegen_cli_url = (
            f"https://repo1.maven.org/maven2/io/swagger/codegen/v3/"
            f"swagger-codegen-cli/{SWAGGER_CODEGEN_CLI_VERSION}/"
            f"swagger-codegen-cli-{SWAGGER_CODEGEN_CLI_VERSION}.jar"
        )
        print(
            f"""🔗 Tentando baixar o Swagger Codegen CLI
            de {swagger_codegen_cli_url}""")
        try:
            with urllib.request.urlopen(swagger_codegen_cli_url) as response:
                if response.status == 200:
                    with open(SWAGGER_CODEGEN_CLI_PATH, "wb") as file:
                        file.write(response.read())
                else:
                    print(
                        f"""❌ Erro ao baixar
                        o arquivo swagger-codegen-cli.jar:
                        HTTP Status {response.status}""")
                    exit(1)
        except urllib.error.HTTPError as e:
            print(
                f"""❌ HTTP Error ao baixar
                o arquivo swagger-codegen-cli.jar:
                {e.code} {e.reason}""")
            exit(1)
        except urllib.error.URLError as e:
            print(
                f"""❌ URL Error ao baixar o
                arquivo swagger-codegen-cli.jar: {e.reason}""")
            exit(1)
        except Exception as ex:
            print("""❌ Erro ao baixar o
                  arquivo swagger-codegen-cli.jar:""", ex)
            exit(1)
    print("✅ swagger-codegen-cli.jar disponível")


def authenticate(api_url):
    username = input("🔑 Digite seu usuário: ")
    password = getpass.getpass("🔑 Digite sua senha: ")

    # Ajuste conforme o endpoint de login da sua API
    login_url = f"{api_url}/login"
    login_data = json.dumps(
        {"username": username, "password": password}).encode('utf-8')
    request = urllib.request.Request(login_url, data=login_data, headers={
                                     "Content-Type": "application/json"})

    try:
        with urllib.request.urlopen(request) as response:
            if response.status == 200:
                response_data = json.loads(response.read().decode("utf-8"))
                # Ajuste conforme a estrutura de resposta da sua API
                return response_data["token"]
            else:
                print(f"❌ Erro ao autenticar: HTTP Status {response.status}")
                exit(1)
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error ao autenticar: {e.code} {e.reason}")
        exit(1)
    except urllib.error.URLError as e:
        print(f"❌ URL Error ao autenticar: {e.reason}")
        exit(1)
    except Exception as ex:
        print(f"❌ Erro ao autenticar: {ex}")
        exit(1)


def download_backend_openapi(api_url, api_key, schema_format):
    backend_openapi_url = f"{api_url}{schema_format}"
    request = urllib.request.Request(backend_openapi_url)
    request.add_header("Authorization", f"Token {api_key}")
    try:
        with urllib.request.urlopen(request) as response:
            data = response.read().decode("utf-8")
            if REPLACE_SECURITY_DEFINITIONS:
                data = replace_security_definitions(data)
        with open(BACKEND_OPENAPI_SPECIFICATION_PATH,
                  "w", encoding='utf8') as file:
            file.write(data)
        print("✅ Endpoints do Backend gerados pelo Swagger baixados")
    except Exception as ex:
        print("""❌ Erro ao baixar os endpoints
              do Backend gerados pelo Swagger:""", ex)
        exit(1)


def replace_security_definitions(data):
    return re.sub(
        r'"securityDefinitions": {"Basic": {"type": "basic"}},'
        r'"security": \[{"Basic": \[]}]',
        '''
        "securityDefinitions": { "Basic": { "type": "basic" },
        "TokenAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": "Token-based authentication
        with required prefix \\"Token\\"" } },
        "security": [{ "Basic": [] }, { "TokenAuth": [] }]
        ''',
        data
    )


def generate_client_code():
    print("📥 Gerando o código cliente ...")
    if path.exists(FETCH_CLIENT_PATH):
        shutil.rmtree(FETCH_CLIENT_PATH)
    cmd = (
        f"java -jar {SWAGGER_CODEGEN_CLI_PATH} "
        f"generate -i {BACKEND_OPENAPI_SPECIFICATION_PATH} "
        f"-l typescript-axios --additional-properties "
        f"modelPropertyNaming=original -o {FETCH_CLIENT_PATH}"
    )
    os.system(cmd)
    print("✅ Código cliente gerado")
    if path.exists(BACKEND_OPENAPI_SPECIFICATION_PATH):
        os.remove(BACKEND_OPENAPI_SPECIFICATION_PATH)
        print("✅ Removido arquivo de endpoints baixado")


def download_client_code(api_url, api_key, schema_format):
    print("📥 Baixando o código cliente ...")
    if path.exists(FETCH_CLIENT_PATH):
        shutil.rmtree(FETCH_CLIENT_PATH)
    cmd = (
        f'java -jar {SWAGGER_CODEGEN_CLI_PATH} generate '
        f'-i {api_url}{schema_format} '
        f'-a "Authorization: Token {api_key}" '
        f'-l typescript-axios '
        f'--additional-properties modelPropertyNaming=original '
        f'-o {FETCH_CLIENT_PATH}'
    )
    print(f"🔗 Executando comando: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Captura e exibe a saída do comando
    if result.returncode != 0:
        print(f"❌ Erro ao executar o comando: {result.stderr}")
        exit(1)
    else:
        print(f"✅ Comando executado com sucesso: {result.stdout}")

    # Verifica se o diretório FETCH_CLIENT_PATH contém arquivos
    if not path.exists(FETCH_CLIENT_PATH):
        print(f"❌ O diretório {FETCH_CLIENT_PATH} não foi criado")
        exit(1)
    if not os.listdir(FETCH_CLIENT_PATH):
        print(f"❌ O diretório {FETCH_CLIENT_PATH} está vazio")
        exit(1)

    print("✅ Código cliente baixado")


def remove_files():
    files = [
        ".gitignore", ".swagger-codegen-ignore",
        "api_test.spec.ts", "git_push.sh",
        ".npmignore", "README.md"
    ]
    for file_name in files:
        file_path = path.join(FETCH_CLIENT_PATH, file_name)
        if path.exists(file_path):
            os.remove(file_path)
    print("✅ Arquivos não utilizados do código cliente removidos")


def replaces_in_code():
    api_file_path = path.join(FETCH_CLIENT_PATH, "api.ts")
    if not path.exists(api_file_path):
        print(f"❌ O arquivo {api_file_path} não existe")
        exit(1)
    with open(api_file_path, "r", encoding='utf8') as file:
        data = file.read()
        data = re.sub(
            r"const BASE_PATH.+",
            r'''const BASE_PATH =
            `${process.env.NEXT_PUBLIC_API_URL}`.replace(/\/+$/, "");''',
            data
        )
        data = re.sub(
            r"protected configuration: Configuration;",
            r'protected configuration?: Configuration;', data)
        data = re.sub(
            r'''export class RequiredError extends Error\n.+name:
            "RequiredError"''',
            r'export class RequiredError extends Error {', data)
        data = re.sub(
            r'delete localVarUrlObj.search;',
            r'localVarUrlObj.search = null;', data)
    with open(api_file_path, "w", encoding='utf8') as file:
        file.write(data)
    print("✅ Realizado substituições no código")


def remove_old_code():
    if path.exists(GENERATED_CODE_OUTPUT_PATH):
        shutil.rmtree(GENERATED_CODE_OUTPUT_PATH)
        print(f"✅ Removido o diretório {GENERATED_CODE_OUTPUT_PATH}")


def copy_new_code():
    if not path.exists(GENERATED_CODE_OUTPUT_PATH):
        os.makedirs(GENERATED_CODE_OUTPUT_PATH)
        print(f"✅ Diretório {GENERATED_CODE_OUTPUT_PATH} criado")

    shutil.copytree(FETCH_CLIENT_PATH,
                    GENERATED_CODE_OUTPUT_PATH, dirs_exist_ok=True)
    print(
        f"✅ Copiado novo código para o diretório {GENERATED_CODE_OUTPUT_PATH}")
    shutil.rmtree(FETCH_CLIENT_PATH)
    print(f"✅ Removido código cliente do diretório {TMP_PATH}")


def main():
    global API_TOKEN
    check_java()
    check_tmp_dir()
    check_swagger_gen_cli()

    # Verifica se API_TOKEN foi fornecido, senão autentica com login e senha
    if not API_TOKEN:
        print("🔒 API_TOKEN não fornecido, autenticando com login e senha...")
        API_TOKEN = authenticate(API_ENDPOINT)

    if DOWNLOAD_CLIENT_CODE:
        download_client_code(API_ENDPOINT, API_TOKEN,
                             SWAGGER_SCHEMA_FORMAT)
    else:
        download_backend_openapi(API_ENDPOINT, API_TOKEN,
                                 SWAGGER_SCHEMA_FORMAT)
        generate_client_code()
    remove_files()
    replaces_in_code()
    remove_old_code()
    copy_new_code()


if __name__ == "__main__":
    main()
