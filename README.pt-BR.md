# Julia-1 API

[English](README.md) | **Português (Brasil)**

Uma API REST leve e conteinerizada para o [SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1), construída com FastAPI e preparada para execução em CPU, Docker e Coolify.

Julia-1 é um modelo compacto de decisão voltado para classificação, roteamento, pontuação e decisões booleanas, em vez de geração de texto como um modelo de chat.

## Recursos

- Interface REST com FastAPI
- Execução otimizada para CPU
- Pronto para Docker e Coolify
- Mantém o Julia-1 carregado em memória entre requisições
- Endpoint de health check
- Documentação OpenAPI interativa em `/docs`
- Configuração através de variáveis de ambiente
- Endpoint simples `/v1/decide`

## Início Rápido com Docker

```bash
docker build -t julia-1-api .
docker run --rm -p 8000:8000 \
  -e JULIA_CPU_THREADS=4 \
  julia-1-api
```

A documentação interativa da API estará disponível em:

```text
http://localhost:8000/docs
```

## API

### Health Check

```bash
curl http://localhost:8000/health
```

### Decisão

```bash
curl -X POST http://localhost:8000/v1/decide \
  -H "Content-Type: application/json" \
  -d '{
    "state": "Um cliente informa que recebeu uma cobrança duplicada.",
    "questions": {
      "team": {
        "type": "choice",
        "instructions": "Qual equipe deve atender esta solicitação?",
        "criteria": {
          "billing": "Cobranças e disputas de pagamento",
          "shipping": "Envio e entrega",
          "access": "Acesso à conta"
        }
      }
    }
  }'
```

## Deploy no Coolify

Crie uma nova Application no Coolify utilizando este repositório do GitHub e selecione **Dockerfile** como build pack.

Configuração inicial recomendada:

- Porta interna: `8000`
- Health check: `/health`
- Limite de CPU: 2-4 CPUs
- Limite de memória: 2-4 GB
- Workers: 1
- `JULIA_CPU_THREADS=4`

Se o servidor também executar serviços sensíveis a latência, comece com poucos recursos e aumente a alocação de CPU somente quando os benchmarks justificarem.

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
| --- | --- | --- |
| `JULIA_CPU_THREADS` | `4` | Threads de CPU disponíveis para o Julia |
| `JULIA_MODEL_PATH` | `/models/Julia-1` | Localização do modelo dentro do container |
| `JULIA_DEVICE` | `cpu` | Dispositivo utilizado para inferência |

## Estrutura do Repositório

```text
.
├── app/
│   └── main.py
├── .github/
│   ├── workflows/
│   │   └── ci.yml
│   ├── CODEOWNERS
│   └── pull_request_template.md
├── Dockerfile
├── requirements.txt
├── .env.example
├── .dockerignore
├── .gitignore
├── CONTRIBUTING.md
└── LICENSE
```

## Contribuindo

Contribuições são bem-vindas. Leia o [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir um Pull Request.

A branch `main` foi pensada para receber alterações através de Pull Requests revisados.

## Projeto Original

Este repositório é um wrapper independente de API e não possui afiliação com a Supersonic Labs.

Os artefatos do modelo Julia-1 permanecem sujeitos à licença e aos termos do projeto original.

## Licença

O código deste wrapper está disponível sob a [Licença MIT](LICENSE).
