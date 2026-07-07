CREATE SCHEMA IF NOT EXISTS bronze;

SET search_path TO bronze;

CREATE TABLE geolocation (
	geolocation_zip_code_prefix INT,
	geolocation_lat DOUBLE PRECISION,
	geolocation_lng DOUBLE PRECISION,
	geolocation_city VARCHAR(100),
	geolocation_state CHAR(2)
);

CREATE TABLE customers (
	customer_id VARCHAR(50),
	customer_unique_id VARCHAR(50),
	customer_zip_code_prefix INT,
	customer_city VARCHAR(100),
	customer_state CHAR(2)
);

CREATE TABLE sellers (
	seller_id VARCHAR(50),
	seller_zip_code_prefix INT,
	seller_city VARCHAR(100),
	seller_state CHAR(2)
);

CREATE TABLE products (
	product_id VARCHAR(50),
	product_category_name VARCHAR(100),
	product_name_lenght INT,
	product_description_lenght INT,
	product_photos_qty INT,
	product_weight_g INT,
	product_length_cm INT,
	product_height_cm INT,
	product_width_cm INT
);


CREATE TABLE orders (
	order_id VARCHAR(50),
	customer_id VARCHAR(50),
	order_status VARCHAR(20),
	order_purchase_timestamp TIMESTAMP,
	order_approved_at TIMESTAMP,
	order_delivered_carrier_date TIMESTAMP,
	order_delivered_customer_date TIMESTAMP,
	order_estimated_delivery_date TIMESTAMP
);


CREATE TABLE order_payments (
	order_id VARCHAR(50),
	payment_sequential INT,
	payment_type VARCHAR(100),
	payment_installments INT,
	payment_value REAL
);

CREATE TABLE order_reviews (
	review_id VARCHAR(50),
	order_id VARCHAR(50),
	review_score INT,
	review_comment_title VARCHAR(200),
	review_comment_message TEXT,
	review_creation_date DATE,
	review_answer_timestamp TIMESTAMP
);


CREATE TABLE order_items (
	order_id VARCHAR(50),
	order_item_id INT,
	product_id VARCHAR(50),
	seller_id VARCHAR(50),
	shipping_limit_date TIMESTAMP,
	price REAL,
	freight_value REAL
);

CREATE TABLE category_name_translation (
	product_category_name VARCHAR(100),
	product_category_name_english VARCHAR(100)
);