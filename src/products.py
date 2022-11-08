class Product:

    def __init__(self, name, product_id, brand, description, sku, image_at, price, url, specifications) -> None:
        self.name = name
        self.store_product_id = product_id
        self.brand = brand
        self.description = description
        self.sku = sku
        self.image_at = image_at
        self.price = price
        self.url = url
        # specifications = {item1_key: item1_value, ..., itemn_key: itemn_value}
        self.specifications = specifications

    def __str__(self):
        return f"{self.name}: ${self.price}"


if __name__ == "__main__":
    import sodimac.product_getter as sodimac_getter
    import easy.product_getter as easy_getter

    product_data = sodimac_getter.parse_data(sodimac_getter.get_data_for(110316112))
    bateria = Product(**product_data)

    product_data = easy_getter.parse_data(easy_getter.get_data_for(672286), 672286)
    anti_pinchazo = Product(**product_data)

    print(bateria)
    print(anti_pinchazo)

