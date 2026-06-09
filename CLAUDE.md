# CLAUDE.md — tesouropy

Port **Python** do pacote R `tesouror` (StrategicProjects/tesouror). Fornece
interface unificada às APIs de dados abertos do Tesouro Nacional. Versão **0.1.0**
(paridade com tesouror 0.2.3).

> Comunicar em **português**. Mantenedor: André Leite (cientista de dados).

## O que é

Cobre as **mesmas 6 APIs** do `tesouror`:

| Domínio | Arquivo | Estilo de API |
|---|---|---|
| SICONFI (RREO, RGF, DCA, MSC, entes) | `src/tesouropy/siconfi.py` | ORDS (`hasMore`/`offset`) |
| CUSTOS | `src/tesouropy/custos.py` | ORDS |
| SADIPEM | `src/tesouropy/sadipem.py` | ORDS |
| Transferências Constitucionais | `src/tesouropy/transferencias.py` | JSON simples |
| SIORG | `src/tesouropy/siorg.py` | JSON simples |
| SIOPE (FNDE/MEC) | `src/tesouropy/siope.py` | OData |

## Arquitetura

Toda a infraestrutura HTTP vive em **`src/tesouropy/_core.py`** (espelha
`R/utils.R`). Os módulos por API são finos: montam parâmetros e delegam.

- **`tnr_request`** — uma requisição via `requests`: cache, retry (5 tentativas,
  backoff 3/6/9/12s em 429/5xx e falhas de conexão), erros acionáveis.
- **`ords_fetch_all`** — pagina ORDS via `hasMore`. Tolerante a falhas: retorna
  DataFrame parcial com `result.partial` / `result.last_page_error`.
- **`tnr_loop`** — itera `.f` sobre vários conjuntos de params, continua em
  falhas; expõe `result.failed` / `result.no_data`.
- **`siope_fetch` / `siope_build_url`** — paginação OData.
- **Cache**: dict em memória (`_CACHE`); limpar com `tesouropy_clear_cache()`.

## Decisões de port

- **polars** (não pandas) como análogo do tibble. Atributos R (`attr(x,
  "partial")`) viram atributos de instância (`x.partial`, `x.failed`,
  `x.no_data`, `x.last_page_error`) — perdem-se após operações polars; consumir
  logo após a chamada.
- **Interface bilíngue PT/EN** preservada: cada função PT tem alias EN que
  remapeia os nomes dos argumentos. **Manter as duas em sincronia.**
- `janitor::clean_names` → `clean_names()` em `_core.py` (snake_case, sem
  acentos via `unicodedata`, dedupe). `str_squish` aplicado a colunas string.
- `cli_alert_*` → `logging.getLogger("tesouropy")` com `NullHandler` (silencioso
  por padrão). `verbose=True` loga a URL completa.
- `max_rows=Inf` → `max_rows=float("inf")` (ou `None`). `check_required` rejeita
  `None` em argumentos obrigatórios.
- Ordem de parâmetros: obrigatórios primeiro (Python não permite obrigatório
  após default). Ex.: em `get_rreo`, `id_ente` vem antes de `co_esfera=None`.

## Convenções

- `snake_case` em funções/parâmetros/colunas (igual ao R).
- Sem editar `dist/`. Build com `uv build`.
- Dados internos: `src/tesouropy/data/rreo_layout.csv` (mesmo arquivo do R
  `inst/extdata/`). Carregado via `importlib.resources`.

## Testes

`tests/` usa **pytest** + **responses** (mock HTTP). Cobre clean_names,
construção de URL, guarda de UF, paginação ORDS, retry, parcial, e rreo tidy.
Rodar: `uv run pytest -q` ou `.venv/bin/python -m pytest`.

## Comandos úteis

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv -e ".[test]"   # instalar em modo dev
.venv/bin/python -m pytest -q                 # rodar testes
uv build                                      # gerar sdist + wheel
```

## Publicação

- **PyPI**: via GitHub Actions Trusted Publishing (`.github/workflows/publish.yml`,
  OIDC, sem token). Disparado por release/tag `v*`. Registrar o publisher
  confiável em pypi.org uma vez (owner=StrategicProjects, repo=tesouropy,
  workflow=publish.yml, environment=pypi).
- **CI**: `.github/workflows/ci.yml` roda testes em Python 3.9–3.13.
- Repositório: `StrategicProjects/tesouropy` (público).

## Direção

Manter **paridade** com `tesouror`: ao alterar a API lá, refletir aqui
(nomes PT+EN, endpoints, paginação, tolerância a falhas). Preservar a API pública.
