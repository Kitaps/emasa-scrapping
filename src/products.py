class Product:

    def __init__(self, name, product_id, brand, description, sku, image_at, price, url, specifications, store) -> None:
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
        self.store = store

    def __repr__(self):
        return f"{self.name}: ${self.price}"

    

    def export_dict(self):
        atribute_json = {
            "NAME": self.name,
            "STORE_PRODUCT_ID": self.store_product_id,
            "BRAND": self.brand,
            "DESCRIPTION": self.description,
            "SKU": self.sku,
            "IMAGE_AT": self.image_at,
            "PRICE": self.price,
            "STORE": self.store,
        }
        # Update the atributes dict with the specs as attributes to be uploaded to DF
        # We want the keys to be in uppercase
        if self.specifications:
            specs = dict(zip(map(lambda key: key.upper(), self.specifications.keys()), self.specifications.values()))
            atribute_json.update(specs)
        return atribute_json


if __name__ == "__main__":
    import sodimac.product_getter as sodimac_getter
    import easy.product_getter as easy_getter

    product_data = sodimac_getter.parse_data(sodimac_getter.get_data_for(110316112))
    bateria = Product(**product_data)

    product_data = easy_getter.parse_data(easy_getter.get_data_for(672286), 672286)
    anti_pinchazo = Product(**product_data)

    print(bateria)
    print(anti_pinchazo)

