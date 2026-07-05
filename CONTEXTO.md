# Contexto del Proyecto: Integración Etsy API v3

Este documento resume el desarrollo y la configuración actual de los scripts para automatizar la gestión de productos en Etsy mediante su API v3.

## Objetivo Alcanzado
Se ha logrado establecer una conexión exitosa y autenticada con la API v3 de Etsy para la tienda **TheMathRelaxing**. El sistema está diseñado para crear listings en estado de **Borrador (Draft)**, adjuntando automáticamente títulos, descripciones, categorías, precios, imágenes de portada y archivos digitales (PDF/ZIP). Esto permite automatizar el trabajo pesado de carga, dejando la publicación final al control manual del usuario desde el panel de Etsy.

## Archivos Creados

### 1. `auth.py`
Script de un solo uso (o uso esporádico) encargado de manejar el flujo de autorización OAuth 2.0 PKCE.
- **Funcionamiento:** Genera un desafío criptográfico, crea una URL de autorización para el usuario, y procesa la URL de redirección (callback) para obtener el `access_token` inicial.
- **Dependencias:** Utiliza exclusivamente librerías estándar de Python (`urllib`, `hashlib`, `secrets`) para evitar problemas de compatibilidad (como los experimentados con `pip` en MSYS64).
- **Salida:** Genera el archivo `etsy_token.json`.

### 2. `etsy_token.json`
Archivo local que almacena de forma segura las credenciales generadas por `auth.py`. Contiene el `access_token` temporal y el `refresh_token` de larga duración.

### 3. `etsy_manager.py`
El motor principal de la integración. Contiene la clase `EtsyManager`.
- **Autenticación Automática:** Lee el archivo `etsy_token.json`. Si el token ha expirado (error HTTP 401), utiliza automáticamente el `refresh_token` para obtener uno nuevo y actualiza el archivo JSON sin intervención humana.
- **Multipart Form-Data:** Implementa su propia función (`_encode_multipart_formdata`) para codificar y subir archivos binarios (imágenes y PDFs) de forma nativa.
- **Flujo de Creación de Borradores (`create_full_product`):**
  1. Crea el borrador en la tienda usando el endpoint `POST /shops/{shop_id}/listings` (Status: "draft").
  2. Sube y asocia las imágenes (rankeadas por orden) usando `POST /shops/{shop_id}/listings/{listing_id}/images`.
  3. Sube el archivo digital (si corresponde) usando `POST /shops/{shop_id}/listings/{listing_id}/files`.

### 4. `upload_test.py`
Script de prueba que demuestra cómo utilizar `EtsyManager.create_full_product(...)` cargando imágenes reales (`fractal_flora_cover.jpg`, etc.) y archivos (`fractal_flora_digital.pdf`) desde el disco duro local, especificando la taxonomía correcta (ID `1`).

## Detalles Técnicos Importantes
- **Keys:** Se utiliza el Client ID (Keystring) y el Shared Secret en el header `x-api-key`.
- **Redirect URI:** Autorizado como `https://mathrelaxing.store/callback`.
- **Taxonomy ID:** Para la creación del borrador de prueba se utilizó el ID `1` (que es una categoría genérica raíz y es ampliamente aceptada para sortear validaciones estrictas iniciales).

## Cómo Continuar
A partir de este contexto, cualquier IA o script futuro solo necesita instanciar `EtsyManager` desde `etsy_manager.py` e invocar `manager.create_full_product(...)` pasando las rutas absolutas o relativas a las carpetas locales de nuevos productos (título, descripción, precio, categoría, lista de imágenes, y lista de archivos digitales). No se necesita reconfigurar la autenticación a menos que el `refresh_token` sea revocado manualmente desde el panel de Etsy.
