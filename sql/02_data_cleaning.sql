CREATE SCHEMA IF NOT EXISTS silver;

SET search_path TO silver;

-- 1. geolocation

-- deduplicate zip code in geolocation table
CREATE TABLE geolocation AS 
SELECT 
	geolocation_zip_code_prefix,
	AVG(geolocation_lat) AS geolocation_lat,
	AVG(geolocation_lng) AS geolocation_lng,
	INITCAP(MAX(geolocation_city)) AS geolocation_city,
	MAX(geolocation_state) AS geolocation_state
FROM bronze.geolocation
GROUP BY geolocation_zip_code_prefix;

ALTER TABLE geolocation ADD PRIMARY KEY (geolocation_zip_code_prefix);

-- 2. customers
CREATE TABLE customers AS 
SELECT DISTINCT * FROM bronze.customers;

ALTER TABLE customers ADD PRIMARY KEY (customer_id);


-- 3. sellers
CREATE TABLE sellers AS 
SELECT DISTINCT * FROM bronze.sellers;

ALTER TABLE sellers ADD PRIMARY KEY (seller_id);

-- 4. products
CREATE TABLE products AS 
SELECT DISTINCT * FROM bronze.products;

ALTER TABLE products ADD PRIMARY KEY (product_id);

-- 5. category_name_translation
CREATE TABLE category_name_translation AS 
SELECT DISTINCT * FROM bronze.category_name_translation;

ALTER TABLE category_name_translation ADD PRIMARY KEY (product_category_name);

-- 6. orders
CREATE TABLE orders AS 
SELECT DISTINCT * FROM bronze.orders;

ALTER TABLE orders ADD PRIMARY KEY (order_id);

-- 7. order_reviews

CREATE TABLE order_reviews AS 
SELECT DISTINCT * 
FROM bronze.order_reviews;

ALTER TABLE order_reviews ADD PRIMARY KEY (review_id, order_id);


-- 8. order_payments
CREATE TABLE order_payments AS 
SELECT DISTINCT *
FROM bronze.order_payments;

ALTER TABLE order_payments ADD PRIMARY KEY (order_id, payment_sequential);


-- 9. order_items
CREATE TABLE order_items AS 
SELECT * FROM bronze.order_items;

ALTER TABLE order_items ADD PRIMARY KEY (order_id, order_item_id);


-- Foreign keys

ALTER TABLE orders 
	ADD CONSTRAINT fk_orders_customers
	FOREIGN KEY (customer_id)
	REFERENCES customers (customer_id);

ALTER TABLE order_reviews
	ADD CONSTRAINT fk_reviews_orders
	FOREIGN KEY (order_id)
	REFERENCES orders (order_id);

ALTER TABLE order_payments
	ADD CONSTRAINT fk_payments_orders
	FOREIGN KEY (order_id)
	REFERENCES orders (order_id);

ALTER TABLE order_items
	ADD CONSTRAINT fk_items_orders 
		FOREIGN KEY (order_id)
		REFERENCES orders (order_id),
	ADD CONSTRAINT fk_items_products 
		FOREIGN KEY (product_id)
		REFERENCES products (product_id),
	ADD CONSTRAINT fk_items_sellers
		FOREIGN KEY (seller_id)
		REFERENCES sellers (seller_id);