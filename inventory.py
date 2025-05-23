import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Type
import sys


# --- Custom Exceptions ---
class InventoryError(Exception): pass

class DuplicateProductIDError(InventoryError): pass
class ProductNotFoundError(InventoryError): pass
class InsufficientStockError(InventoryError): pass
class InvalidProductDataError(InventoryError): pass


# --- Abstract Base Product ---
class Product(ABC):
    def __init__(self, product_id: str, name: str, price: float, quantity_in_stock: int):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    def restock(self, amount: int):
        self._quantity_in_stock += amount

    def sell(self, quantity: int):
        if quantity > self._quantity_in_stock:
            raise InsufficientStockError(f"Not enough stock for {self._name}. Available: {self._quantity_in_stock}")
        self._quantity_in_stock -= quantity

    def get_total_value(self):
        return self._price * self._quantity_in_stock

    @abstractmethod
    def to_dict(self): pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data): pass

    def __str__(self):
        return f"{self._name} (ID: {self._product_id}) - ${self._price:.2f}, Stock: {self._quantity_in_stock}"


# --- Subclasses of Product ---
class Electronics(Product):
    def __init__(self, product_id, name, price, quantity, brand, warranty_years):
        super().__init__(product_id, name, price, quantity)
        self.brand = brand
        self.warranty_years = warranty_years

    def __str__(self):
        return super().__str__() + f", Brand: {self.brand}, Warranty: {self.warranty_years} yrs"

    def to_dict(self):
        return {
            "type": "Electronics",
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity": self._quantity_in_stock,
            "brand": self.brand,
            "warranty_years": self.warranty_years
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["product_id"], data["name"], data["price"], data["quantity"], data["brand"], data["warranty_years"])


class Grocery(Product):
    def __init__(self, product_id, name, price, quantity, expiry_date):
        super().__init__(product_id, name, price, quantity)
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    def is_expired(self):
        return datetime.now().date() > self.expiry_date

    def __str__(self):
        status = "EXPIRED" if self.is_expired() else "Valid"
        return super().__str__() + f", Expires: {self.expiry_date} ({status})"

    def to_dict(self):
        return {
            "type": "Grocery",
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity": self._quantity_in_stock,
            "expiry_date": self.expiry_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["product_id"], data["name"], data["price"], data["quantity"], data["expiry_date"])


class Clothing(Product):
    def __init__(self, product_id, name, price, quantity, size, material):
        super().__init__(product_id, name, price, quantity)
        self.size = size
        self.material = material

    def __str__(self):
        return super().__str__() + f", Size: {self.size}, Material: {self.material}"

    def to_dict(self):
        return {
            "type": "Clothing",
            "product_id": self._product_id,
            "name": self._name,
            "price": self._price,
            "quantity": self._quantity_in_stock,
            "size": self.size,
            "material": self.material
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["product_id"], data["name"], data["price"], data["quantity"], data["size"], data["material"])


# --- Inventory Manager ---
class Inventory:
    def __init__(self):
        self._products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        if product._product_id in self._products:
            raise DuplicateProductIDError(f"Product ID {product._product_id} already exists.")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product ID {product_id} not found.")
        del self._products[product_id]

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if p.__class__.__name__.lower() == product_type.lower()]

    def list_all_products(self):
        return list(self._products.values())

    def sell_product(self, product_id, quantity):
        product = self._products.get(product_id)
        if not product:
            raise ProductNotFoundError()
        product.sell(quantity)

    def restock_product(self, product_id, quantity):
        product = self._products.get(product_id)
        if not product:
            raise ProductNotFoundError()
        product.restock(quantity)

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired_ids = [pid for pid, p in self._products.items() if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired_ids:
            del self._products[pid]

    def save_to_file(self, filename):
        data = [p.to_dict() for p in self._products.values()]
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        product_map = {
            "Electronics": Electronics,
            "Grocery": Grocery,
            "Clothing": Clothing
        }

        self._products.clear()
        for item in data:
            ptype = item.get("type")
            cls = product_map.get(ptype)
            if not cls:
                raise InvalidProductDataError(f"Unknown product type: {ptype}")
            product = cls.from_dict(item)
            self._products[product._product_id] = product


# --- CLI Menu ---
def cli():
    inventory = Inventory()

    menu = """
[1] Add Product
[2] Sell Product
[3] Restock Product
[4] Search Product
[5] List All Products
[6] Remove Expired Groceries
[7] Total Inventory Value
[8] Save Inventory to File
[9] Load Inventory from File
[0] Exit
"""

    while True:
        print(menu)
        choice = input("Select an option: ").strip()

        try:
            if choice == "1":
                ptype = input("Type (Electronics/Grocery/Clothing): ").strip().lower()
                pid = input("ID: ")
                name = input("Name: ")
                price = float(input("Price: "))
                qty = int(input("Quantity: "))

                if ptype == "electronics":
                    brand = input("Brand: ")
                    warranty = int(input("Warranty (years): "))
                    product = Electronics(pid, name, price, qty, brand, warranty)

                elif ptype == "grocery":
                    exp = input("Expiry Date (YYYY-MM-DD): ")
                    product = Grocery(pid, name, price, qty, exp)

                elif ptype == "clothing":
                    size = input("Size: ")
                    material = input("Material: ")
                    product = Clothing(pid, name, price, qty, size, material)

                else:
                    print("Invalid type.")
                    continue

                inventory.add_product(product)
                print("Product added.")

            elif choice == "2":
                pid = input("Product ID to sell: ")
                qty = int(input("Quantity: "))
                inventory.sell_product(pid, qty)
                print("Product sold.")

            elif choice == "3":
                pid = input("Product ID to restock: ")
                qty = int(input("Quantity: "))
                inventory.restock_product(pid, qty)
                print("Product restocked.")

            elif choice == "4":
                name = input("Search by name: ")
                results = inventory.search_by_name(name)
                for p in results:
                    print(p)

            elif choice == "5":
                for p in inventory.list_all_products():
                    print(p)

            elif choice == "6":
                inventory.remove_expired_products()
                print("Expired groceries removed.")

            elif choice == "7":
                print("Total Inventory Value: $%.2f" % inventory.total_inventory_value())

            elif choice == "8":
                filename = input("Filename to save: ")
                inventory.save_to_file(filename)
                print("Saved.")

            elif choice == "9":
                filename = input("Filename to load: ")
                inventory.load_from_file(filename)
                print("Loaded.")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Invalid option.")

        except InventoryError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    cli()
