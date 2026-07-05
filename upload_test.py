import etsy_manager
import time

def main():
    manager = etsy_manager.EtsyManager()
    
    title = "TEST DRAFT - Fractal Flora Digital Book"
    description = "This is a test draft listing created via API. Please ignore or delete."
    price = 5.99
    taxonomy_id = 1  # Category
    
    images = ["fractal_flora_cover.jpg", "fractal_flora_sample_detail.jpg"]
    files = ["fractal_flora_digital.pdf"]
    
    print("Iniciando subida de borrador de prueba...")
    manager.create_full_product(title, description, price, taxonomy_id, images, files)

if __name__ == "__main__":
    main()
