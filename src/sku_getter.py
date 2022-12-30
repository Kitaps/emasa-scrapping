import pandas

# Every file is diferent and has diferent needs, therefore we treat each file
sonax_df = pandas.read_excel("C:/Users/Liedt/Desktop/EMASA/emasa_scrapping/feeder_files/SKUsLegacy/sonax.xls")
sonax_skus = sonax_df[["sku", "store"]]



if __name__ == "__main__":
    # print(sonax_df.head())
    print(sonax_skus.head())