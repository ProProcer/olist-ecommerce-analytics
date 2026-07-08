-- diagnostics for 02_data_cleaning.sql

-- show that original geolocation_zip_code_prefix is not unique, 
-- justifying deduplication in step 1
SELECT geolocation_zip_code_prefix, COUNT(*)
FROM bronze.geolocation 
GROUP BY geolocation_zip_code_prefix;


-- confirming that review_id, order_id is the minimal set for primary key, 
-- justifying deduplication and primary key choice in step 7
SELECT 
	COUNT(r) AS total_count,
	COUNT(DISTINCT (r)) AS unique_count,
	COUNT(DISTINCT (review_id)) AS unique_review_id,
	COUNT(DISTINCT (review_id, order_id)) AS unique_review_order_id
FROM bronze.order_reviews r;

-- around 0.28% of the customer zip code has no corresponding geolocation record, so no fk constraint is made. 
SELECT 1.0 * SUM(CASE WHEN g.geolocation_zip_code_prefix IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_customer_zip_code_proportion
FROM silver.customers c
LEFT JOIN silver.geolocation g ON 
	c.customer_zip_code_prefix = g.geolocation_zip_code_prefix;

-- around 0.23% of the seller zip code has no corresponding geolocation record, so no fk constraint is made. 
SELECT 1.0 * SUM(CASE WHEN g.geolocation_zip_code_prefix IS NULL THEN 1 ELSE 0 END) / COUNT(*) AS missing_seller_zip_code_proportion
FROM silver.sellers s
LEFT JOIN silver.geolocation g ON 
	s.seller_zip_code_prefix = g.geolocation_zip_code_prefix;

