Advanced OOP Challenge: Inventory Management System

Objective:
Design a robust Inventory Management System in Python that can manage different types of products, handle stock operations, sales, and persist data. This challenge is meant to polish your OOP concepts and make you confident in applying them in real-world use cases.

---

*1. Abstract Base Class: Product*

Use the abc module to make Product an abstract base class.

Attributes (with encapsulation):

* _product_id
* _name
* _price
* _quantity_in_stock

Methods (abstract & concrete):

* restock(amount)
* sell(quantity)
* get_total_value() --> price \ stock
* __str__() --> formatted product info

---

*2. Subclasses of Product:*

Create at least 3 different product types, each with extra attributes and overridden behavior where needed:

* *Electronics* --> warranty_years, brand

* *Grocery* --> expiry_date, is_expired()

* *Clothing*  --> size, material

Each subclass must override __str__() to include their specific info.

---

*3. Class: Inventory*

This class will manage a collection of products.

Attributes:

* _products --> a dict or list of products

Methods:

* add_product(product: Product)
* remove_product(product_id)
* search_by_name(name)
* search_by_type(product_type)
* list_all_products()
* sell_product(product_id, quantity)
* restock_product(product_id, quantity)
* total_inventory_value()
* remove_expired_products() (for groceries only)

---

4. Bonus / Extra Features (Optional but encouraged):

Add the ability to save and *load inventory data* in JSON format:

* save_to_file(filename)
* load_from_file(filename)

Ensure you store all relevant attributes and reconstruct subclasses properly when loading.

* Implement custom exceptions for cases like:

  * Selling more than available stock
  * Adding products with duplicate IDs
  * Loading invalid product data from file.

* Add CLI Menu using a while loop for interaction:

  * Add product
  * Sell product
  * Search/view product
  * Save/Load inventory
  * Exit

---

 Evaluation Criteria:

* Clean, well-structured code
* Proper use of OOP concepts
* Realistic and reusable class design
* Error and edge-case handling
* Code readability and documententation