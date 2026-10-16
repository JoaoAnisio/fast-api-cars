# Fast API Cars

![Tests](https://github.com/JoaoAnisio/fast-api-cars/actions/workflows/tests.yml/badge.svg)

API REST para gestão de vendas de carros, construída com **FastAPI**, **SQLAlchemy** e **Alembic**. Vendedores autenticados cadastram clientes e registram pedidos de venda; administradores gerenciam o catálogo de carros e acompanham todas as vendas.

> Projeto de estudo. Usa SQLite e não foi preparado para produção sem ajustes (veja [Limitações](#limitações)).

## Funcionalidades

- Autenticação com **JWT** (access token + refresh token) e senhas armazenadas com **bcrypt**
- Dois perfis: **vendedor** e **administrador**
- Cadastro de carros (somente admin), clientes e pedidos
- Cálculo automático do preço final do pedido, com desconto
- **Teto de desconto** para vendedores comuns (configurável); acima dele, só admin
- Um carro só pode estar em um pedido ativo por vez
- Ciclo de vida do pedido: `PENDING` → `COMPLETED` ou `CANCELED`
- Migrations de banco com Alembic
- Suíte de testes automatizados com pytest

## Tecnologias

Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · python-jose (JWT) · passlib + bcrypt · SQLite · pytest

## Como rodar

**Pré-requisitos:** Python 3.12+ e Git.

```bash
# 1. clonar e entrar na pasta
git clone https://github.com/JoaoAnisio/fast-api-cars.git
cd fast-api-cars

# 2. criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate     # Linux / macOS

# 3. instalar as dependências
pip install -r requirements.txt

# 4. configurar as variáveis de ambiente
copy .env.example .env          # Linux / macOS: cp .env.example .env
# edite o .env e preencha a SECRET_KEY (instruções dentro do arquivo)

# 5. criar o banco de dados
alembic upgrade head

# 6. subir o servidor
uvicorn main:app --reload
```

A documentação interativa (Swagger) fica em **http://127.0.0.1:8000/docs**. O botão **Authorize** aceita e-mail e senha de um usuário cadastrado.

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | sim | Chave de assinatura dos tokens JWT. Gere com `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ALGORITHM` | sim | Algoritmo do JWT (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | sim | Validade do access token, em minutos |
| `MAX_DISCOUNT_SELLER` | não | Desconto máximo (%) para vendedores comuns. Padrão: `10` |

### Criando o primeiro administrador

O cadastro público (`POST /auth/create_user`) sempre cria um usuário comum. Para promover alguém a administrador, cadastre o usuário e rode:

```bash
python make_admin.py email@exemplo.com
```

## Endpoints

Todas as rotas, exceto `create_user` e as de login, exigem `Authorization: Bearer <access_token>`.

| Método | Rota | Descrição | Acesso |
|---|---|---|---|
| POST | `/auth/create_user` | Cadastra um usuário comum | público |
| POST | `/auth/login` | Retorna access e refresh token | público |
| POST | `/auth/login-form` | Login por formulário (usado pelo Swagger) | público |
| GET | `/auth/refresh_token` | Gera novo access token a partir do refresh token | refresh token |
| POST | `/cars/add_car` | Cadastra um carro | admin |
| GET | `/cars/list_cars` | Lista os carros | autenticado |
| GET | `/cars/get_car/{car_id}` | Busca um carro | autenticado |
| POST | `/clients/add_client` | Cadastra um cliente | autenticado |
| GET | `/clients/list_clients` | Lista os clientes | autenticado |
| GET | `/clients/get_client/{client_id}` | Busca um cliente | autenticado |
| POST | `/orders/create_order` | Registra um pedido de venda | autenticado |
| GET | `/orders/my_orders` | Lista os pedidos do próprio vendedor | autenticado |
| GET | `/orders/list_orders` | Lista todos os pedidos | admin |
| GET | `/orders/get_order/{order_id}` | Busca um pedido | dono ou admin |
| POST | `/orders/order/complete/{order_id}` | Conclui um pedido pendente | dono ou admin |
| POST | `/orders/order/cancel/{order_id}` | Cancela um pedido pendente | dono ou admin |
| DELETE | `/orders/delete_order/{order_id}` | Remove um pedido | dono ou admin |

### Exemplo de uso

```bash
# cadastrar e fazer login
curl -X POST http://127.0.0.1:8000/auth/create_user \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana", "email": "ana@exemplo.com", "password": "senha1234"}'

curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "ana@exemplo.com", "password": "senha1234"}'
# -> {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}

# registrar um pedido com 5% de desconto
curl -X POST http://127.0.0.1:8000/orders/create_order \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"car_id": 1, "client_id": 1, "discount": 5}'
```

## Regras de negócio

- O pedido pertence ao **vendedor autenticado**; o vendedor nunca é informado no corpo da requisição.
- `total_price = preço do carro × (1 − desconto / 100)`. O desconto vai de 0 a 100.
- Vendedores comuns podem dar até `MAX_DISCOUNT_SELLER`% de desconto (padrão 10%). Acima disso a API responde `403`.
- Um carro não pode estar em dois pedidos ativos. Cancelar o pedido libera o carro.
- Só pedidos `PENDING` podem ser concluídos ou cancelados.
- Um vendedor só vê e altera os próprios pedidos. Administradores veem todos.

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

Os testes usam um banco SQLite em memória e não precisam do arquivo `.env`.

## Estrutura do projeto

```
├── main.py              # cria o app e registra as rotas
├── config.py            # variáveis de ambiente, bcrypt e esquema OAuth2
├── dependencies.py      # sessão do banco e verificação de token
├── models.py            # modelos SQLAlchemy (User, Car, Client, Order)
├── schemas.py           # schemas Pydantic de entrada e saída
├── auth_routes.py       # cadastro, login e refresh
├── car_routes.py        # carros
├── client_routes.py     # clientes
├── order_routes.py      # pedidos
├── make_admin.py        # promove um usuário a admin
├── alembic/             # migrations do banco
└── tests/               # testes automatizados
```

## Limitações

- Banco SQLite local; para produção, troque por PostgreSQL ou similar.
- Não há revogação de tokens nem limite de tentativas de login.
- Os dados de clientes (como o documento) ficam visíveis a todos os usuários autenticados.

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
