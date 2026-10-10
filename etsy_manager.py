import json
import urllib.request
import urllib.parse
import os
import uuid
import mimetypes

CLIENT_ID = "1nkkipgbsfholyrhfkqqqkjj"
SHARED_SECRET = os.environ.get("ETSY_SHARED_SECRET", "")
TOKEN_FILE = "etsy_token.json"

class EtsyManager:
    def __init__(self):
        self.base_url = "https://openapi.etsy.com/v3/application"
        self.token_data = self.load_tokens()
        self.shop_id = None
        
    def load_tokens(self):
        if not os.path.exists(TOKEN_FILE):
            env_refresh = os.environ.get("ETSY_REFRESH_TOKEN")
            if env_refresh:
                # Sin etsy_token.json (p. ej. sesión cloud nueva): generarlo con el refresh token del entorno
                self.token_data = {'refresh_token': env_refresh}
                self.refresh_token()
                return self.token_data
            raise Exception("No se encontró etsy_token.json. ¡Por favor ejecuta auth.py primero!")
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
            
    def save_tokens(self, data):
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, f)
        self.token_data = data
        
    def refresh_token(self):
        print("El token ha expirado. Refrescando...")
        url = "https://api.etsy.com/v3/public/oauth/token"
        data = urllib.parse.urlencode({
            'grant_type': 'refresh_token',
            'client_id': CLIENT_ID,
            'refresh_token': self.token_data['refresh_token']
        }).encode('ascii')
        
        req = urllib.request.Request(url, data=data)
        try:
            with urllib.request.urlopen(req) as response:
                new_token_data = json.loads(response.read().decode('utf-8'))
                self.save_tokens(new_token_data)
                print("¡Token refrescado con éxito!")
        except Exception as e:
            print("Error al refrescar el token.")
            if hasattr(e, 'read'):
                print(e.read().decode('utf-8'))
            raise Exception("No se pudo refrescar el token. Tendrás que volver a autenticarte.")

    def _encode_multipart_formdata(self, fields, files):
        boundary = uuid.uuid4().hex
        body = bytearray()
        
        for key, value in fields.items():
            body.extend(f'--{boundary}\r\n'.encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode('utf-8'))
            body.extend(f'{value}\r\n'.encode('utf-8'))
            
        for key, file_info in files.items():
            filename, content, content_type = file_info
            body.extend(f'--{boundary}\r\n'.encode('utf-8'))
            body.extend(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode('utf-8'))
            body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
            body.extend(content)
            body.extend(b'\r\n')
            
        body.extend(f'--{boundary}--\r\n'.encode('utf-8'))
        content_type = f'multipart/form-data; boundary={boundary}'
        return content_type, body

    def make_request(self, method, endpoint, payload=None, is_multipart=False, multipart_data=None,
                     json_body=False, retry=True):
        url = f"{self.base_url}{endpoint}"

        headers = {
            'x-api-key': f"{CLIENT_ID}:{SHARED_SECRET}",
            'Authorization': f"Bearer {self.token_data['access_token']}"
        }

        data = None
        if is_multipart and multipart_data:
            fields, files = multipart_data
            content_type, data = self._encode_multipart_formdata(fields, files)
            headers['Content-Type'] = content_type
        elif json_body and payload is not None:
            # Algunos endpoints (ej. /inventory) exigen JSON real, no
            # application/x-www-form-urlencoded: rechazan listas/objetos
            # anidados con "Not a valid JSON string".
            data = json.dumps(payload).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif payload:
            data = urllib.parse.urlencode(payload).encode('utf-8')
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                raw = response.read().decode('utf-8')
                return json.loads(raw) if raw.strip() else {}  # DELETE devuelve 204 sin cuerpo
        except urllib.error.HTTPError as e:
            if e.code == 401 and retry:
                self.refresh_token()
                return self.make_request(method, endpoint, payload, is_multipart, multipart_data,
                                        json_body, retry=False)
            else:
                print(f"Error de API ({e.code}) en {endpoint}:")
                print(e.read().decode('utf-8'))
                raise

    def get_shop_id(self):
        if self.shop_id:
            return self.shop_id
            
        print("Obteniendo información de la tienda...")
        me = self.make_request('GET', '/users/me')
        user_id = me['user_id']
        
        shops = self.make_request('GET', f'/users/{user_id}/shops')
        self.shop_id = shops['shop_id']
        return self.shop_id
        
    def create_draft_listing(self, title, description, price, taxonomy_id, is_digital=True, quantity=999,
                             tags=None, shipping_profile_id=None, readiness_state_id=None,
                             return_policy_id=None):
        shop_id = self.get_shop_id()
        print(f"\nCreando borrador: {title[:30]}...")

        payload = {
            'quantity': quantity,
            'title': title,
            'description': description,
            'price': price,
            'who_made': 'i_did',
            'when_made': '2020_2026',
            'taxonomy_id': taxonomy_id,
            'is_supply': 'false',
            'state': 'draft',
            'type': 'download' if is_digital else 'physical'
        }
        if not is_digital:
            if not shipping_profile_id:
                raise ValueError("shipping_profile_id es obligatorio para listings fisicos")
            if not readiness_state_id:
                raise ValueError("readiness_state_id es obligatorio para listings fisicos")
            if not return_policy_id:
                raise ValueError("return_policy_id es obligatorio para listings fisicos")
            payload['shipping_profile_id'] = shipping_profile_id
            payload['readiness_state_id'] = readiness_state_id
        if tags:
            # Etsy: máx 13 tags, cada una ≤20 chars; se envían separadas por comas
            payload['tags'] = ','.join(t.strip() for t in tags[:13] if len(t.strip()) <= 20)

        result = self.make_request('POST', f'/shops/{shop_id}/listings', payload=payload)
        print(f"Borrador creado exitosamente con ID: {result['listing_id']}")
        if not is_digital:
            # return_policy_id no siempre se acepta en el POST de creacion (no
            # verificado); el PATCH posterior SI esta confirmado que funciona
            # (ver notas de products_catalog.py, 2026-07-07) asi que se aplica
            # siempre aca para no repetir el hueco de los primeros 4 listings.
            self.update_listing(result['listing_id'], return_policy_id=return_policy_id)
        return result['listing_id']

    def update_listing(self, listing_id, **fields):
        """PATCH a un listing existente. Para tags pasar tags=[...].
        Nota: el precio NO se actualiza aquí — usar update_listing_price()."""
        shop_id = self.get_shop_id()
        payload = {}
        for k, v in fields.items():
            if k == 'tags' and isinstance(v, (list, tuple)):
                payload['tags'] = ','.join(t.strip() for t in v[:13] if len(t.strip()) <= 20)
            elif k == 'price':
                # Etsy ignores price on PATCH for inventory listings — route correctly
                continue
            else:
                payload[k] = v
        if not payload:
            return {}
        print(f"Actualizando listing {listing_id}: {list(payload.keys())}")
        return self.make_request('PATCH', f'/shops/{shop_id}/listings/{listing_id}', payload=payload)

    def update_listing_price(self, listing_id, price, quantity=None):
        """Update listing price via inventory API (required for most listings).

        PUT /listings/{listing_id}/inventory with JSON body.
        Preserves existing products/offerings structure when possible.
        """
        inv = self.make_request('GET', f'/listings/{listing_id}/inventory')
        products_out = []
        for prod in inv.get('products') or []:
            offerings_out = []
            for off in prod.get('offerings') or []:
                if off.get('is_deleted'):
                    continue
                qty = quantity if quantity is not None else off.get('quantity', 999)
                offerings_out.append({
                    'price': float(price),
                    'quantity': int(qty),
                    'is_enabled': bool(off.get('is_enabled', True)),
                })
            if not offerings_out:
                offerings_out = [{
                    'price': float(price),
                    'quantity': int(quantity if quantity is not None else 999),
                    'is_enabled': True,
                }]
            # property_values: keep property_id + value_ids shape Etsy expects
            pvs = []
            for pv in prod.get('property_values') or []:
                pvs.append({
                    'property_id': pv.get('property_id'),
                    'value_ids': pv.get('value_ids') or [],
                    'values': pv.get('values') or [],
                    'property_name': pv.get('property_name') or '',
                    'scale_id': pv.get('scale_id'),
                })
            products_out.append({
                'sku': prod.get('sku') or '',
                'property_values': pvs,
                'offerings': offerings_out,
            })
        if not products_out:
            products_out = [{
                'sku': '',
                'property_values': [],
                'offerings': [{
                    'price': float(price),
                    'quantity': int(quantity if quantity is not None else 999),
                    'is_enabled': True,
                }],
            }]

        body = {'products': products_out}
        # Optional property arrays if present
        for key in ('price_on_property', 'quantity_on_property', 'sku_on_property'):
            if inv.get(key):
                body[key] = inv[key]

        url = f"{self.base_url}/listings/{listing_id}/inventory"
        data = json.dumps(body).encode('utf-8')
        headers = {
            'x-api-key': f"{CLIENT_ID}:{SHARED_SECRET}",
            'Authorization': f"Bearer {self.token_data['access_token']}",
            'Content-Type': 'application/json',
        }
        req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
        try:
            with urllib.request.urlopen(req) as response:
                raw = response.read().decode('utf-8')
                result = json.loads(raw) if raw.strip() else {}
                print(f"Precio listing {listing_id} → ${float(price):.2f}")
                return result
        except urllib.error.HTTPError as e:
            if e.code == 401:
                self.refresh_token()
                headers['Authorization'] = f"Bearer {self.token_data['access_token']}"
                req = urllib.request.Request(url, data=data, headers=headers, method='PUT')
                with urllib.request.urlopen(req) as response:
                    raw = response.read().decode('utf-8')
                    result = json.loads(raw) if raw.strip() else {}
                    print(f"Precio listing {listing_id} → ${float(price):.2f}")
                    return result
            print(f"Error de API ({e.code}) al actualizar precio de {listing_id}:")
            print(e.read().decode('utf-8'))
            raise

    def update_price(self, listing_id, price):
        """
        Cambia el precio de un listing. IMPORTANTE: el precio en Etsy API v3
        vive en el INVENTARIO (/listings/{id}/inventory), no en el listing
        mismo -- update_listing(price=...) hace un PATCH que Etsy acepta con
        200 OK pero IGNORA en silencio (el precio no cambia). Hay que leer el
        inventario, limpiar los campos de solo-lectura (product_id, is_deleted,
        offering_id, readiness_state_id -- Etsy rechaza el PUT si van incluidos)
        y reenviarlo como JSON real (no form-urlencoded: los arrays anidados
        fallan con "Not a valid JSON string" si van url-encodeados).
        """
        inv = self.make_request('GET', f'/listings/{listing_id}/inventory')
        clean_products = []
        for prod in inv['products']:
            offerings = [{
                'price': price,
                'quantity': off['quantity'],
                'is_enabled': off['is_enabled'],
            } for off in prod['offerings']]
            clean_products.append({
                'sku': prod.get('sku', ''),
                'property_values': prod.get('property_values', []),
                'offerings': offerings,
            })
        print(f"Actualizando precio de listing {listing_id} a {price}...")
        result = self.make_request('PUT', f'/listings/{listing_id}/inventory',
                                   payload={'products': clean_products}, json_body=True)
        print("Precio actualizado con éxito.")
        return result

    def upload_listing_image(self, listing_id, image_path, rank=1):
        shop_id = self.get_shop_id()
        print(f"Subiendo imagen {os.path.basename(image_path)} (rank {rank})...")
        
        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = 'image/jpeg'
            
        with open(image_path, 'rb') as f:
            content = f.read()
            
        fields = {'rank': str(rank)}
        files = {'image': (os.path.basename(image_path), content, mime_type)}
        
        result = self.make_request('POST', f'/shops/{shop_id}/listings/{listing_id}/images', 
                                 is_multipart=True, multipart_data=(fields, files))
        print("Imagen subida con éxito.")
        return result
        
    def upload_listing_file(self, listing_id, file_path):
        shop_id = self.get_shop_id()
        print(f"Subiendo archivo digital {os.path.basename(file_path)}...")
        
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        fields = {'name': os.path.basename(file_path)}
        files = {'file': (os.path.basename(file_path), content, mime_type)}
        
        result = self.make_request('POST', f'/shops/{shop_id}/listings/{listing_id}/files', 
                                 is_multipart=True, multipart_data=(fields, files))
        print("Archivo digital subido con éxito.")
        return result

    def upload_listing_video(self, listing_id, video_path):
        """Sube un video al endpoint /videos (NO al de imágenes).
        Etsy: 1 video por listing, mp4, 5-15s aprox, <100MB."""
        shop_id = self.get_shop_id()
        print(f"Subiendo video {os.path.basename(video_path)}...")

        with open(video_path, 'rb') as f:
            content = f.read()

        fields = {'name': os.path.basename(video_path)}
        files = {'video': (os.path.basename(video_path), content, 'video/mp4')}

        result = self.make_request('POST', f'/shops/{shop_id}/listings/{listing_id}/videos',
                                 is_multipart=True, multipart_data=(fields, files))
        print("Video subido con éxito.")
        return result

    def delete_listing_image(self, listing_id, listing_image_id):
        shop_id = self.get_shop_id()
        print(f"Eliminando imagen {listing_image_id} del listing {listing_id}...")
        return self.make_request('DELETE', f'/shops/{shop_id}/listings/{listing_id}/images/{listing_image_id}')

    def delete_listing_file(self, listing_id, listing_file_id):
        shop_id = self.get_shop_id()
        print(f"Eliminando archivo {listing_file_id} del listing {listing_id}...")
        return self.make_request('DELETE', f'/shops/{shop_id}/listings/{listing_id}/files/{listing_file_id}')

    def delete_listing(self, listing_id):
        """Elimina un listing (útil para limpiar borradores fallidos)."""
        print(f"Eliminando listing {listing_id}...")
        return self.make_request('DELETE', f'/listings/{listing_id}')

    def create_full_product(self, title, description, price, taxonomy_id, image_paths,
                            digital_file_paths=None, video_path=None, tags=None,
                            shipping_profile_id=None, readiness_state_id=None, return_policy_id=None):
        is_digital = bool(digital_file_paths)
        listing_id = self.create_draft_listing(title, description, price, taxonomy_id, is_digital, tags=tags,
                                               shipping_profile_id=shipping_profile_id,
                                               readiness_state_id=readiness_state_id,
                                               return_policy_id=return_policy_id)

        for idx, img_path in enumerate(image_paths, start=1):
            if os.path.exists(img_path):
                self.upload_listing_image(listing_id, img_path, rank=idx)
            else:
                print(f"Advertencia: No se encontró la imagen {img_path}")

        if video_path and os.path.exists(video_path):
            try:
                self.upload_listing_video(listing_id, video_path)
            except Exception as e:
                print(f"Advertencia: el video no se pudo subir ({e}). Continúo sin video.")

        if digital_file_paths:
            for file_path in digital_file_paths:
                if os.path.exists(file_path):
                    self.upload_listing_file(listing_id, file_path)
                else:
                    print(f"Advertencia: No se encontró el archivo digital {file_path}")

        print(f"\n¡Proceso completado! El producto '{title[:30]}...' está en tus borradores de Etsy.")
        return listing_id

if __name__ == "__main__":
    print("El módulo etsy_manager.py ha sido actualizado y está listo para usarse.")
