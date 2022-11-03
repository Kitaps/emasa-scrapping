class Product:

    def __init__(self, name, product_id, brand, description, sku, image_at, price, url, specifications ) -> None:
        self.name = name
        self.product_id = product_id
        self.brand = brand
        self.description = description
        self.sku = sku
        self.image_at = image_at
        self.price = price
        self.url = url
        self.specifications = specifications

    def __str__(self):
        return f"{self.name}: ${self.price}"

if __name__ == "__main__":
    from sodimac.product_getter import get_data_for, parse_data

    product_data = parse_data(get_data_for(110316112))
    bateria = Product(**product_data)

