"""
Script para testar a geração de cards localmente
Execute: python test_local.py
"""

import requests
import json

# URL do serviço (local)
BASE_URL = "http://localhost:5000"

# Dados de teste (usando uma notícia real)
dados_teste = {
    "imagem_url": "https://s2-valor.glbimg.com/N/w/tzvzzPT7mbRCMCJEFkwA/ana-castela-iuri-maia-e-lauana-prado.jpg.jpeg",
    "categoria": "MARKETING",
    "titulo": "Mercado Livre triplica investimento em música e terá nova edição de festival"
}

def test_health():
    """Testa se o serviço está online"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_gerar_card_png():
    """Testa geração de card (retorna PNG)"""
    print("\n🎨 Testando geração de card (PNG)...")
    try:
        response = requests.post(
            f"{BASE_URL}/gerar-card",
            json=dados_teste,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            # Salvar imagem
            with open("test_output.png", "wb") as f:
                f.write(response.content)
            print("   ✅ Card salvo em: test_output.png")
            return True
        else:
            print(f"   ❌ Erro: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_gerar_card_base64():
    """Testa geração de card (retorna base64)"""
    print("\n🎨 Testando geração de card (Base64)...")
    try:
        response = requests.post(
            f"{BASE_URL}/gerar-card-base64",
            json=dados_teste,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Base64 length: {len(data.get('image_base64', ''))} chars")
            print("   ✅ Base64 gerado com sucesso!")
            return True
        else:
            print(f"   ❌ Erro: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 Arven Card Generator - Testes")
    print("=" * 50)
    
    # Verificar se serviço está rodando
    if not test_health():
        print("\n⚠️  Serviço não está rodando!")
        print("    Execute: python app.py")
        exit(1)
    
    # Testar geração
    test_gerar_card_png()
    test_gerar_card_base64()
    
    print("\n" + "=" * 50)
    print("✅ Testes concluídos!")
    print("=" * 50)
