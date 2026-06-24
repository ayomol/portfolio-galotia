import requests
from bs4 import BeautifulSoup
import time

# Configuración inicial
base_url = "https://galotiabrewing.com/categoria-producto/cervezas/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

print("Iniciando el escaneo profundo de Galotia Brewing...")

# 1. Obtener la página principal de la tienda
response = requests.get(base_url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# 2. Encontrar todos los enlaces únicos a los productos individuales
product_links = []
for link in soup.select('ul.products li.product a.woocommerce-LoopProduct-link'):
    href = link.get('href')
    if href and href not in product_links:
        product_links.append(href)

print(f"Se han encontrado {len(product_links)} cervezas. Escaneando páginas individuales...")

html_cards = ""

# 3. Visitar cada página de producto uno por uno
for url in product_links:
    print(f"-> Extrayendo datos de: {url}")
    try:
        prod_response = requests.get(url, headers=headers)
        prod_soup = BeautifulSoup(prod_response.text, 'html.parser')
        
        # Extraer título
        title_tag = prod_soup.select_one('h1.product_title')
        title = title_tag.text.strip() if title_tag else "Cerveza Galotia"
        
        # Extraer imagen en alta calidad
        img_tag = prod_soup.select_one('meta[property="og:image"]')
        img_url = img_tag['content'] if img_tag and img_tag.has_attr('content') else "https://via.placeholder.com/200x300/252525/f39c12?text=Sin+Imagen"
        
        # Extraer categoría (Ej: Hazy IPA, Core Range...)
        cat_tags = prod_soup.select('.product_meta .posted_in a')
        categories = " / ".join([cat.text for cat in cat_tags]) if cat_tags else "Craft Beer"
        
        # ¡NUEVO! Extraer la descripción corta (Alcohol, lúpulos, etc.)
        desc_tag = prod_soup.select_one('div.woocommerce-product-details__short-description')
        # Usamos decode_contents() para mantener los saltos de línea y negritas originales de WooCommerce
        short_desc = desc_tag.decode_contents().strip() if desc_tag else "<p>Disfruta de nuestra cerveza artesanal.</p>"
        
        # Generar la tarjeta HTML
        html_cards += f"""
            <div class="product-card">
                <div class="product-image">
                    <img src="{img_url}" alt="{title}">
                </div>
                <div class="product-info">
                    <span class="product-tag">{categories}</span>
                    <h2 class="product-title">{title}</h2>
                    <div class="product-description">
                        {short_desc}
                    </div>
                </div>
            </div>
        """
    except Exception as e:
        print(f"Error escaneando {url}: {e}")
        
    # Pausa de 1 segundo para ser amigables con el servidor
    time.sleep(1)

# 4. Construir la Landing Page completa con el CSS actualizado
html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Portfolio de Cervezas - Galotia Brewing</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&family=Oswald:wght@500;700&display=swap');

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Montserrat', sans-serif; background-color: #121212; color: #ffffff; line-height: 1.6; }}
        
        header {{ background-color: #0a0a0a; padding: 20px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #f39c12; }}
        .logo {{ font-family: 'Oswald', sans-serif; font-size: 24px; font-weight: 700; color: #f39c12; text-transform: uppercase; letter-spacing: 2px; }}
        nav a {{ color: #ffffff; text-decoration: none; margin-left: 20px; text-transform: uppercase; font-size: 14px; font-weight: 700; transition: color 0.3s; }}
        nav a:hover {{ color: #f39c12; }}

        .hero {{ background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1566633806327-68e152aaf26d?auto=format&fit=cover&w=1200&q=80') no-repeat center center/cover; height: 300px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 20px; }}
        .hero h1 {{ font-family: 'Oswald', sans-serif; font-size: 48px; text-transform: uppercase; color: #ffffff; letter-spacing: 3px; margin-bottom: 10px; }}
        .hero p {{ font-size: 18px; color: #cccccc; max-width: 600px; }}

        .portfolio-container {{ max-width: 1200px; margin: 50px auto; padding: 0 20px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 30px; }}

        .product-card {{ background-color: #1a1a1a; border-radius: 8px; overflow: hidden; border: 1px solid #333333; transition: transform 0.3s, border-color 0.3s; display: flex; flex-direction: column; }}
        .product-card:hover {{ transform: translateY(-5px); border-color: #f39c12; }}
        .product-image {{ width: 100%; height: 320px; background-color: #252525; display: flex; justify-content: center; align-items: center; overflow: hidden; }}
        .product-image img {{ width: auto; height: 90%; object-fit: contain; transition: transform 0.3s; }}
        .product-card:hover .product-image img {{ transform: scale(1.05); }}
        
        .product-info {{ padding: 20px; text-align: center; flex-grow: 1; display: flex; flex-direction: column; justify-content: flex-start; }}
        .product-tag {{ font-size: 11px; text-transform: uppercase; background-color: #f39c12; color: #000000; padding: 3px 8px; font-weight: 700; border-radius: 4px; align-self: center; margin-bottom: 10px; }}
        .product-title {{ font-family: 'Oswald', sans-serif; font-size: 20px; text-transform: uppercase; margin-bottom: 8px; color: #ffffff; letter-spacing: 1px; }}
        
        /* ¡NUEVO! Estilos para la descripción corta de WooCommerce */
        .product-description {{ font-size: 13px; color: #bbbbbb; text-align: center; margin-top: 15px; padding-top: 15px; border-top: 1px solid #333333; line-height: 1.4; }}
        .product-description p {{ margin-bottom: 5px; }}

        footer {{ background-color: #0a0a0a; padding: 40px 20px; text-align: center; border-top: 1px solid #333333; margin-top: 50px; font-size: 14px; color: #666666; }}
        footer a {{ color: #f39c12; text-decoration: none; }}
        
        @media (max-width: 768px) {{ header {{ flex-direction: column; padding: 20px; }} nav {{ margin-top: 15px; }} .hero h1 {{ font-size: 36px; }} }}
    </style>
</head>
<body>

    <header>
        <div class="logo">Galotia Brewing</div>
        <nav>
            <a href="https://galotiabrewing.com/">Inicio</a>
            <a href="https://galotiabrewing.com/categoria-producto/cervezas/">Tienda</a>
            <a href="#portfolio">Nuestro Portfolio</a>
        </nav>
    </header>

    <div class="hero">
        <h1>Nuestras Creaciones</h1>
        <p>Una selección exclusiva de cervezas artesanales hechas con pasión, carácter y un cariño especial por las mejores recetas.</p>
    </div>

    <div class="portfolio-container" id="portfolio">
        <div class="grid">
            {html_cards}
        </div>
    </div>

    <footer>
        <p><strong>Galotia Brewing</strong> - Calle de Escorial, 17, 35110 Vecindario, Gran Canaria, Las Palmas</p>
        <p>Tel: +34 828 664 897 | Email: <a href="mailto:info@galotiabrewing.com">info@galotiabrewing.com</a></p>
        <p style="margin-top: 20px;">&copy; 2026 Galotia Brewing. Todos los derechos reservados.</p>
    </footer>

</body>
</html>
"""

# 5. Guardar el archivo definitivo
with open("portfolio.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("¡Portfolio actualizado con éxito! Se ha generado el archivo portfolio.html")
