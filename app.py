"""
Arven News Card Generator - Microserviço para geração de cards de notícias
"""

from flask import Flask, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import os
import textwrap

app = Flask(__name__)

# Configurações
CARD_WIDTH = 1080
CARD_HEIGHT = 1080
FONTS_DIR = "fonts"
ASSETS_DIR = "assets"


def download_image(url: str) -> Image.Image:
    """Baixa uma imagem da URL e retorna como objeto PIL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Erro ao baixar imagem: {e}")
        # Retorna uma imagem placeholder cinza
        return Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (30, 30, 30))


def criar_gradiente_overlay(largura: int, altura: int) -> Image.Image:
    """Cria um overlay com gradiente escuro na parte inferior"""
    overlay = Image.new("RGBA", (largura, altura), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Gradiente começa em 40% da altura
    inicio_gradiente = int(altura * 0.4)
    
    for y in range(inicio_gradiente, altura):
        # Calcula opacidade progressiva (0 a 220)
        progresso = (y - inicio_gradiente) / (altura - inicio_gradiente)
        opacidade = int(220 * progresso)
        draw.rectangle([(0, y), (largura, y + 1)], fill=(0, 0, 0, opacidade))
    
    return overlay


def quebrar_texto(texto: str, fonte: ImageFont.FreeTypeFont, max_largura: int, draw: ImageDraw.Draw) -> list:
    """Quebra o texto em múltiplas linhas que cabem na largura especificada"""
    palavras = texto.split()
    linhas = []
    linha_atual = ""
    
    for palavra in palavras:
        teste = f"{linha_atual} {palavra}".strip()
        bbox = draw.textbbox((0, 0), teste, font=fonte)
        largura_texto = bbox[2] - bbox[0]
        
        if largura_texto <= max_largura:
            linha_atual = teste
        else:
            if linha_atual:
                linhas.append(linha_atual)
            linha_atual = palavra
    
    if linha_atual:
        linhas.append(linha_atual)
    
    return linhas


def gerar_card(
    imagem_url: str,
    categoria: str,
    titulo: str,
    logo_path: str = None
) -> BytesIO:
    """
    Gera um card de notícia no estilo NotJournal/Arven
    
    Args:
        imagem_url: URL da imagem de fundo
        categoria: Categoria da notícia (ex: "MARKETING", "TECNOLOGIA")
        titulo: Título/manchete da notícia
        logo_path: Caminho para o arquivo da logo (opcional)
    
    Returns:
        BytesIO: Buffer com a imagem PNG gerada
    """
    
    # 1. Baixar e preparar imagem de fundo
    img_fundo = download_image(imagem_url)
    
    # Redimensionar mantendo aspect ratio e cortando para preencher
    img_ratio = img_fundo.width / img_fundo.height
    target_ratio = CARD_WIDTH / CARD_HEIGHT
    
    if img_ratio > target_ratio:
        # Imagem mais larga - ajusta pela altura
        new_height = CARD_HEIGHT
        new_width = int(new_height * img_ratio)
    else:
        # Imagem mais alta - ajusta pela largura
        new_width = CARD_WIDTH
        new_height = int(new_width / img_ratio)
    
    img_fundo = img_fundo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Cortar para o centro
    left = (new_width - CARD_WIDTH) // 2
    top = (new_height - CARD_HEIGHT) // 2
    img_fundo = img_fundo.crop((left, top, left + CARD_WIDTH, top + CARD_HEIGHT))
    img_fundo = img_fundo.convert("RGBA")
    
    # 2. Aplicar overlay com gradiente
    overlay = criar_gradiente_overlay(CARD_WIDTH, CARD_HEIGHT)
    img_final = Image.alpha_composite(img_fundo, overlay)
    
    # 3. Adicionar logo (se existir)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path).convert("RGBA")
            # Redimensionar logo mantendo proporção (max 150px de largura)
            logo_max_width = 150
            if logo.width > logo_max_width:
                ratio = logo_max_width / logo.width
                logo = logo.resize(
                    (logo_max_width, int(logo.height * ratio)),
                    Image.Resampling.LANCZOS
                )
            img_final.paste(logo, (40, 40), logo)
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
    
    # 4. Preparar para desenhar texto
    draw = ImageDraw.Draw(img_final)
    
    # Carregar fontes
    try:
        fonte_categoria = ImageFont.truetype(
            os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"), 28
        )
        fonte_titulo = ImageFont.truetype(
            os.path.join(FONTS_DIR, "Montserrat-Bold.ttf"), 52
        )
    except Exception as e:
        print(f"Erro ao carregar fontes, usando padrão: {e}")
        fonte_categoria = ImageFont.load_default()
        fonte_titulo = ImageFont.load_default()
    
    margem = 40
    max_largura_texto = CARD_WIDTH - (margem * 2)
    
    # 5. Desenhar categoria
    categoria_upper = categoria.upper()
    draw.text(
        (margem, CARD_HEIGHT - 280),
        categoria_upper,
        font=fonte_categoria,
        fill=(255, 255, 255, 200)
    )
    
    # Linha decorativa abaixo da categoria
    bbox_cat = draw.textbbox((margem, CARD_HEIGHT - 280), categoria_upper, font=fonte_categoria)
    largura_categoria = bbox_cat[2] - bbox_cat[0]
    draw.rectangle(
        [(margem, CARD_HEIGHT - 245), (margem + largura_categoria, CARD_HEIGHT - 242)],
        fill=(255, 255, 255, 180)
    )
    
    # 6. Desenhar título
    linhas_titulo = quebrar_texto(titulo, fonte_titulo, max_largura_texto, draw)
    
    # Máximo 3 linhas
    linhas_titulo = linhas_titulo[:3]
    if len(linhas_titulo) == 3 and len(quebrar_texto(titulo, fonte_titulo, max_largura_texto, draw)) > 3:
        # Adicionar "..." se truncou
        linhas_titulo[2] = linhas_titulo[2][:50] + "..."
    
    y_titulo = CARD_HEIGHT - 220
    espacamento_linha = 60
    
    for linha in linhas_titulo:
        draw.text(
            (margem, y_titulo),
            linha,
            font=fonte_titulo,
            fill=(255, 255, 255)
        )
        y_titulo += espacamento_linha
    
    # 7. Converter para RGB e salvar em buffer
    img_final = img_final.convert("RGB")
    
    buffer = BytesIO()
    img_final.save(buffer, format="PNG", quality=95)
    buffer.seek(0)
    
    return buffer


# ==================== ROTAS DA API ====================

@app.route("/", methods=["GET"])
def home():
    """Rota de health check"""
    return jsonify({
        "status": "ok",
        "service": "Arven Card Generator",
        "version": "1.0.0"
    })


@app.route("/gerar-card", methods=["POST"])
def api_gerar_card():
    """
    Gera um card de notícia
    
    Body JSON:
    {
        "imagem_url": "https://...",
        "categoria": "MARKETING",
        "titulo": "Título da notícia aqui"
    }
    
    Returns:
        image/png
    """
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({"error": "JSON body é obrigatório"}), 400
        
        imagem_url = dados.get("imagem_url")
        categoria = dados.get("categoria", "NOTÍCIA")
        titulo = dados.get("titulo")
        
        if not titulo:
            return jsonify({"error": "Campo 'titulo' é obrigatório"}), 400
        
        if not imagem_url:
            return jsonify({"error": "Campo 'imagem_url' é obrigatório"}), 400
        
        # Caminho da logo (opcional)
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if not os.path.exists(logo_path):
            logo_path = None
        
        # Gerar card
        buffer = gerar_card(
            imagem_url=imagem_url,
            categoria=categoria,
            titulo=titulo,
            logo_path=logo_path
        )
        
        return send_file(
            buffer,
            mimetype="image/png",
            as_attachment=False,
            download_name="card.png"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/gerar-card-base64", methods=["POST"])
def api_gerar_card_base64():
    """
    Gera um card e retorna em base64 (útil para n8n)
    
    Body JSON:
    {
        "imagem_url": "https://...",
        "categoria": "MARKETING",
        "titulo": "Título da notícia aqui"
    }
    
    Returns:
        JSON com campo "image_base64"
    """
    import base64
    
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({"error": "JSON body é obrigatório"}), 400
        
        imagem_url = dados.get("imagem_url")
        categoria = dados.get("categoria", "NOTÍCIA")
        titulo = dados.get("titulo")
        
        if not titulo:
            return jsonify({"error": "Campo 'titulo' é obrigatório"}), 400
        
        if not imagem_url:
            return jsonify({"error": "Campo 'imagem_url' é obrigatório"}), 400
        
        # Caminho da logo (opcional)
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if not os.path.exists(logo_path):
            logo_path = None
        
        # Gerar card
        buffer = gerar_card(
            imagem_url=imagem_url,
            categoria=categoria,
            titulo=titulo,
            logo_path=logo_path
        )
        
        # Converter para base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        return jsonify({
            "success": True,
            "image_base64": image_base64,
            "mime_type": "image/png"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Criar diretórios se não existirem
    os.makedirs(FONTS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    print("=" * 50)
    print("Arven Card Generator")
    print("=" * 50)
    print(f"Diretório de fontes: {FONTS_DIR}/")
    print(f"Diretório de assets: {ASSETS_DIR}/")
    print("")
    print("Coloque sua logo em: assets/logo.png")
    print("Coloque a fonte em: fonts/Montserrat-Bold.ttf")
    print("")
    print("Endpoints:")
    print("  POST /gerar-card        → Retorna imagem PNG")
    print("  POST /gerar-card-base64 → Retorna JSON com base64")
    print("=" * 50)
    
    app.run(host="0.0.0.0", port=5000, debug=True)