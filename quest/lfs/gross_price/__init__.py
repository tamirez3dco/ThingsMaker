# lfs imports
from lfs.plugins import PriceCalculator


class GrossPriceCalculator(PriceCalculator):
    """
    The value of product.price stored in the database includes tax, in other
    words, the stored price is the gross price of the product.

    See lfs.plugins.PriceCalculator for more information.
    """
    def get_price_net(self, with_properties=True):
        return self.get_price(with_properties) / self._calc_product_tax_rate()

    def get_price_gross(self, with_properties=True):
        return self.get_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_standard_price_net(self, with_properties=True):
        return self.get_standard_price(with_properties) / self._calc_product_tax_rate()

    def get_standard_price_gross(self, with_properties=True):
        return self.get_standard_price_net(with_properties) * self._calc_customer_tax_rate()

    def get_for_sale_price_net(self, with_properties=True):
        return self.get_for_sale_price(with_properties) / self._calc_product_tax_rate()

    def get_for_sale_price_gross(self, with_properties=True):
        return self.get_for_sale_price_net(with_properties) * self._calc_customer_tax_rate()

    def price_includes_tax(self):
        return True
