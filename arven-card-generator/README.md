# Arven Card Generator 🎨

Microserviço para geração automática de cards de notícias no estilo NotJournal/Arven.

## 📸 O que ele faz

Recebe uma notícia (título, categoria, imagem) e gera um card profissional 1080x1080px pronto para Instagram.

```
┌─────────────────────────────────┐
│  [LOGO ARVEN]                   │
│                                 │
│                                 │
│     [IMAGEM DA NOTÍCIA]         │
│       (com gradiente)           │
│                                 │
├─────────────────────────────────┤
│  CATEGORIA                      │
│  ─────────                      │
│  TÍTULO DA MANCHETE             │
│  EM ATÉ 3 LINHAS                │
└─────────────────────────────────┘
```

---

## 🚀 Quick Start

### Opção 1: Docker (Recomendado)

```bash
# 1. Clone ou copie os arquivos
cd arven-card-generator

# 2. Adicione seus assets
#    - Coloque sua logo em: assets/logo.png
#    - Coloque a fonte em: fonts/Montserrat-Bold.ttf

# 3. Suba o container
docker-compose up -d

# 4. Teste
curl http://localhost:5000/
```

### Opção 2: Python Local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Adicionar assets (logo e fonte)
mkdir -p fonts assets
# Coloque: assets/logo.png e fonts/Montserrat-Bold.ttf

# 3. Rodar
python app.py
```

---

## 📁 Estrutura de Arquivos

```
arven-card-generator/
├── app.py              # Código principal da API
├── requirements.txt    # Dependências Python
├── Dockerfile          # Container config
├── docker-compose.yml  # Orquestração
├── fonts/
│   └── Montserrat-Bold.ttf   # ⚠️ VOCÊ DEVE ADICIONAR
└── assets/
    └── logo.png              # ⚠️ VOCÊ DEVE ADICIONAR
```

### ⚠️ Assets Obrigatórios

1. **Logo** (`assets/logo.png`)
   - Sua logo em PNG com fundo transparente
   - Recomendado: ~150px de largura

2. **Fonte** (`fonts/Montserrat-Bold.ttf`)
   - Baixe grátis em: https://fonts.google.com/specimen/Montserrat
   - Use a versão Bold

---

## 🔌 API Endpoints

### `GET /`
Health check

```bash
curl http://localhost:5000/
```

**Response:**
```json
{
  "status": "ok",
  "service": "Arven Card Generator",
  "version": "1.0.0"
}
```

---

### `POST /gerar-card`
Gera o card e retorna a imagem PNG diretamente.

```bash
curl -X POST http://localhost:5000/gerar-card \
  -H "Content-Type: application/json" \
  -d '{
    "imagem_url": "https://exemplo.com/imagem.jpg",
    "categoria": "MARKETING",
    "titulo": "Mercado Livre triplica investimento em música e terá nova edição de festival"
  }' \
  --output card.png
```

**Response:** `image/png`

---

### `POST /gerar-card-base64`
Gera o card e retorna em base64 (ideal para n8n).

```bash
curl -X POST http://localhost:5000/gerar-card-base64 \
  -H "Content-Type: application/json" \
  -d '{
    "imagem_url": "https://exemplo.com/imagem.jpg",
    "categoria": "MARKETING",
    "titulo": "Mercado Livre triplica investimento em música"
  }'
```

**Response:**
```json
{
  "success": true,
  "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
  "mime_type": "image/png"
}
```

---

## 🔧 Integração com n8n

### Nó HTTP Request

| Campo | Valor |
|-------|-------|
| Method | POST |
| URL | `http://seu-servidor:5000/gerar-card-base64` |
| Body Type | JSON |

**Body:**
```json
{
  "imagem_url": "{{ $json.urlToImage }}",
  "categoria": "MARKETING",
  "titulo": "{{ $json.titulo }}"
}
```

### Fluxo Completo

```
NewsAPI → OpenAI Curador → OpenAI Gerador → Code Parse → HTTP Request (Card) → Instagram API
```

---

## ☁️ Deploy em Produção

### DigitalOcean / AWS / Railway

```bash
# Build da imagem
docker build -t arven-card-generator .

# Push para registry (exemplo Docker Hub)
docker tag arven-card-generator seu-usuario/arven-card-generator
docker push seu-usuario/arven-card-generator

# No servidor
docker run -d -p 5000:5000 \
  -v /path/to/fonts:/app/fonts \
  -v /path/to/assets:/app/assets \
  seu-usuario/arven-card-generator
```

### Railway (mais fácil)

1. Conecte seu repo GitHub
2. Railway detecta o Dockerfile automaticamente
3. Adicione as variáveis de ambiente se necessário
4. Deploy! 🚀

---

## 🎨 Personalização

### Cores e Estilo

Edite as constantes no `app.py`:

```python
CARD_WIDTH = 1080      # Largura do card
CARD_HEIGHT = 1080     # Altura do card

# Na função criar_gradiente_overlay():
opacidade = int(220 * progresso)  # Intensidade do gradiente (0-255)

# Na função gerar_card():
fonte_categoria = ... size=28    # Tamanho da categoria
fonte_titulo = ... size=52       # Tamanho do título
```

### Posicionamento

```python
# Posição da logo
img_final.paste(logo, (40, 40), logo)  # (x, y)

# Posição da categoria
draw.text((margem, CARD_HEIGHT - 280), ...)

# Posição do título
y_titulo = CARD_HEIGHT - 220
espacamento_linha = 60
```

---

## 📝 Exemplo de Resultado

Input:
```json
{
  "imagem_url": "https://s2-valor.glbimg.com/.../mercado-livre.jpg",
  "categoria": "MARKETING",
  "titulo": "Mercado Livre triplica investimento em música e terá nova edição de festival"
}
```

Output: Card 1080x1080px com:
- ✅ Imagem de fundo com gradiente escuro
- ✅ Logo no canto superior esquerdo
- ✅ Categoria em destaque
- ✅ Título em até 3 linhas

---

## 🐛 Troubleshooting

**Erro: Fonte não encontrada**
```
Coloque o arquivo Montserrat-Bold.ttf em fonts/
```

**Erro: Logo não aparece**
```
Coloque o arquivo logo.png em assets/
```

**Imagem fica distorcida**
```
O sistema já faz crop inteligente. Se ainda assim ficar ruim,
a imagem original pode estar com proporção muito diferente.
```

---

## 📄 Licença

Uso interno Arven. Não distribuir.
