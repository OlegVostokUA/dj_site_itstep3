from decimal import Decimal
from django.conf import settings

# from myshop.shop.models import Product
from shop.models import Product

# i = Product


class Cart(object):

    def __init__(self, request):
        """
        Ініціалізуємо кошик
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        """
        Додати продукт у кошик або оновити його кількість.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        # Оновлення сесії cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Відмітити сеанс як "змінений", щоб переконатися, що його збережено
        self.session.modified = True

    def remove(self, product):
        """
        Видалення товару з кошику.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """
        Перебір елементів у кошику та отримання продуктів з базы даних.
        """
        product_ids = self.cart.keys()
        # отримання обєктів product та додавання їх у кошик
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Підрахунок всіх товарів у кошику.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Підрахунок вартості товарів у кошику.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in
                   self.cart.values())

    def clear(self):
        # видалення кошику з сесії
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True
