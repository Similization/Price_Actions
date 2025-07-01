def change_data(data):
    return data.strftime('%d.%m.%Y (%H:%M:%S)')

def calculate_product_count(orders):
    result = dict()
    for order in orders:
        products = order['order_products']
        for product in products:
            key = product["product_name"]
            value = product["quantity"]
            result[key] = result.get(key, 0) + value
    return result