"""
Esse script em Python serve como gerador automático de cliente HTTP baseado em uma especificação OpenAPI. Ele é especialmente útil para quem quer consumir APIs rapidamente sem escrever manualmente todos os métodos de acesso. A seguir, faço uma análise e explicação detalhada, incluindo melhorias e alertas.

✅ O que esse script faz?
Dado um arquivo ou URL com especificação OpenAPI em JSON, ele:

Extrai todos os schemas da seção components e gera modelos Pydantic correspondentes.

Para cada path, method, requestBody, response, gera um método assíncrono para a classe APIClient.

Salva tudo no arquivo client.py.

🧱 Estrutura do Cliente Gerado
1. BaseModel do Pydantic
Cada schema vira algo como:

python
Copy
Edit
class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
2. Classe APIClient
Contém um httpx.AsyncClient, com métodos como:

python
Copy
Edit
async def users_get(self, params: Optional[Dict[str, Any]] = None) -> List[User]:
    '''
    Gets a list of users
    '''
    url = "/users"
    response = await self.client.request("GET", url, params=params)
    response.raise_for_status()
    return [User(**item) for item in response.json()]
🔍 Pontos Fortes
✅ Geração automática de clientes compatíveis com async/await.

✅ Suporte a path parameters (como /user/{id}).

✅ Criação de modelos Pydantic.

✅ Boa cobertura de OpenAPI 3.0 (básica).

✅ Docstring descritiva do endpoint.

⚠️ Pontos de Atenção / Melhorias sugeridas
1. Verificação de HTTPS
python
Copy
Edit
response = httpx.get(openapi_json, timeout=10000, verify=False)
Sugestão: Evite verify=False por padrão. É inseguro.

2. method_name frágil
python
Copy
Edit
method_name = re.sub(r"\{.*?\}", "specific", method_name)
Isso pode gerar métodos genéricos e colidirem. Melhor usar path.replace("/", "__") + method.

3. Ignora headers globais ou security schemes
Se a API exige Authorization, isso não está automatizado.

4. Falta suporte a query parameters documentados
Só adiciona params, mas não gera com base na OpenAPI (parameters → in: query).

5. Dict[str, Any] como fallback
Modelos que não têm $ref são ignorados, o que pode gerar códigos muito genéricos.

💡 Sugestões de Extensões Futuras
 Gerar documentação local ou README com exemplo de uso.

 Suporte a autenticação (securitySchemes).

 Geração opcional de clientes síncronos (httpx.Client).

 Adicionar suporte a parâmetros de cabeçalho e cookie (in: header, in: cookie).

 Adicionar anotação dos status HTTP esperados.

 Testar APIs com base no schema: gerar pytest de contrato.

🧪 Como usar
bash
Copy
Edit
python generate_client.py https://minhaapi.com/openapi.json
Ele salva um client.py que pode ser usado assim:

python
Copy
Edit
from client import APIClient

async def main():
    async with APIClient(base_url="https://api.exemplo.com") as client:
        user = await client.users__get()

import asyncio
asyncio.run(main())
Se quiser, posso te ajudar a:

Refatorar esse script para torná-lo mais robusto.

Gerar também testes automaticamente.

Transformá-lo em um CLI de uso geral.

Quer seguir por algum desses caminhos?
"""

import json
import re
import sys
import textwrap
from contextlib import suppress
from os import path
from typing import Optional

import httpx

TEMPLATE = """import httpx
from urllib.parse import urljoin
from typing import Optional, Dict, List, Any
from pydantic import BaseModel


{models}


def normalize_payload(payload: Any) -> Optional[dict]:
    if payload is None:
        return None

    if isinstance(payload, BaseModel):
        payload_request = payload.model_dump()
    else:
        payload_request = payload

    return payload_request


class APIClient:
    def __init__(self, base_url: str, headers: Optional[dict] = None):
        self.client = httpx.AsyncClient(
            headers=headers,
            base_url=base_url.rstrip("/")
        )

{methods}

    async def close(self):
        await self.client.aclose()


    async def __aenter__(self):
        return self


    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
"""

def extract_path_params(method_name):
    path_params = []
    matches = path.replace("/", "__") + method_name  # Captura todas as ocorrências

    for match in matches:
        path_params.append(match)

    return path_params



def wrap_text(text: str, width: int = 70) -> str:
    result = '\n        '.join(textwrap.wrap(text, width))
    if not result:
        return "\"\"\" \"\"\""

    result = f"\"\"\"\n        {result}\n        \"\"\""
    return result



def generate_pydantic_model(name: str, schema: dict) -> Optional[str]:
    """Gera uma classe Pydantic baseada na especificação OpenAPI."""

    if name.endswith("Error"):
        return None

    properties = schema.get("properties", {})
    required = set(schema.get("required", []))

    fields = []
    for prop, details in properties.items():
        field_type = map_openapi_type_to_python(
            details, required = (prop in required)
        )
        default = "" if prop in required else " = None"
        fields.append(f"    {prop}: {field_type}{default}")

    return f"class {name}(BaseModel):\n" + ("\n".join(fields) if fields else "    pass")


def map_openapi_type_to_python(details: dict, required: bool) -> str:
    """Mapeia tipos OpenAPI para tipos Python/Pydantic."""
    type_mapping = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "array": "List",
        "object": "Dict[str, Any]",
        "null": "None"
    }

    openapi_type = details.get("type", "object")
    if required is True:
        if openapi_type == "array":
            items = details.get("items", {}).get("type", "Any")
            return f"List[{type_mapping.get(items, 'Any')}]"

        return type_mapping.get(openapi_type, "Any")

    else:
        if openapi_type == "array":
            items = details.get("items", {}).get("type", "Any")
            return f"Optional[List[{type_mapping.get(items, 'Any')}]]"

        return "Optional[" + type_mapping.get(openapi_type, "Any") + "]"


def generate_method(
    name: str,
    method: str,
    path: str,
    description: str,
    request_body: Optional[str],
    response_body: Optional[str],
    schema_class: Optional[str],
    path_params: list[str],
) -> str:
    """Gera um método para a API client."""

    request_type = request_body or "Dict[str, Any]"
    response_type = schema_class or "Dict[str, Any]"

    # Construção da URL
    formatted_path = path
    if path_params:
        specific_param = ", " + ", ".join(f"{param}: str" for param in path_params)
        formatted_path = path
        for param in path_params:
            formatted_path = formatted_path.replace(f"{{{param}}}", f"{{{param}}}")
        url = f'url = f"{formatted_path}"'
    else:
        specific_param = ","
        url = f'url = "{path}"'

    if not specific_param.endswith(","):
        specific_param += ","

    # Definição do retorno
    response_return = "return response.json()"
    if schema_class:
        response_return = f"return {schema_class}(**response.json())"

    # Tratamento do corpo da requisição
    if method in {"GET", "DELETE"}:
        body_section1 = ","
        body_section2 = ","
    else:
        body_section1 = f"\n        json_data: Optional[{request_type}] = None,"
        body_section2 = "\n            json=json_data,"

    return f"""    async def {name}(
        self{specific_param}
        params: Optional[Dict[str, Any]] = None,{body_section1}
        headers: Optional[Dict[str, str]] = None
    ) -> {response_type}:

        {wrap_text(description)}

        {url}

        response = await self.client.request(
            "{method}",
            url,
            params=params,{body_section2}
            headers=headers
        )

        response.raise_for_status()
        {response_return}
""".replace(",,", ",")


def generate_client(openapi_json: str):

    response = httpx.get(openapi_json, timeout=10000, verify=False)
    spec = response.json()

    models = []
    components = spec.get("components", {})
    schemas = components.get("schemas", {})

    for name, schema in schemas.items():
        if (model := generate_pydantic_model(name, schema)) is not None:
            models.append(model)

    methods = []
    for path, methods_dict in spec.get("paths", {}).items():
        for method, details in methods_dict.items():

            path_params = []
            method_name = f"{path.strip('/').replace('/', '__')}_{method}"
            # method_name = f"{path.strip('/').replace('/', '__')}"

            for path_param in extract_path_params(method_name):
                path_param = path_param.replace("{", "").replace("}", "")
                path_params.append(path_param)

            method_name = re.sub(r"\{.*?\}", "specific", method_name)

            description = details.get("description", "")
            request_body = None
            response_body = None

            if "requestBody" in details:
                content = details["requestBody"].get("content", {})
                for content_type, content_details in content.items():
                    if "application/json" in content_type:
                        schema_ref = content_details.get("schema", {}).get("$ref", "")
                        request_body = (
                            schema_ref.split("/")[-1]
                            if schema_ref else "Dict[str, Any]"
                        )
                        break

            if "responses" in details:
                for status, response in details["responses"].items():
                    content = response.get("content", {})
                    for content_type, content_details in content.items():
                        if "application/json" in content_type:
                            schema_ref = content_details.get("schema", {}).get("$ref", "")
                            response_body = (
                                schema_ref.split("/")[-1]
                                if schema_ref else "Dict[str, Any]"
                            )
                            break

            method_dict = methods_dict[method]

            schema_class = None
            for code, body_schema in method_dict['responses'].items():

                with suppress(Exception):
                    if 299 > int(code) > 199:

                        schema_class = (
                            body_schema
                                ['content']
                                ['application/json']
                                ['schema']
                                ['$ref']
                                .split("/")
                                [-1]
                        )

            methods.append(
                generate_method(
                    method_name.replace("__vspecific", "").replace('api__', ''),
                    method.upper(),
                    path,
                    description,
                    request_body,
                    response_body,
                    schema_class,
                    path_params
                )
            )

    client_code = TEMPLATE.format(models="\n\n\n".join(models), methods="\n".join(methods))
    with open("client.py", "w") as f:
        while client_code.find('""""') != -1:
            client_code = client_code.replace('""""', '"""')
        while client_code.find('\*') != -1:
            client_code = client_code.replace('\*', " *")

        f.write(client_code)

    print("Client generated: client.py")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python generate_client.py openapi.json")
        sys.exit(1)
    generate_client(sys.argv[1])
