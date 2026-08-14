-- python scripts/export_dataset.py -i sql/03_build_order_delivery_dataset.sql -o data/processed/order_delivery_dataset.csv
SELECT 
	o.order_id AS order_id,
	o.order_approved_at,
	o.order_delivered_carrier_date,
	ANY_VALUE(cg.geolocation_lat) AS customer_lat,
	ANY_VALUE(cg.geolocation_lng) AS customer_lng,
	ANY_VALUE(COALESCE(cg.geolocation_state, c.customer_state)) AS customer_state,
	ANY_VALUE(sg.geolocation_lat) AS seller_lat,
	ANY_VALUE(sg.geolocation_lng) AS seller_lng,
	ANY_VALUE(COALESCE(sg.geolocation_state, s.seller_state)) AS seller_state,
	ANY_VALUE(6371 * 2 * ASIN(SQRT(
        POWER(SIN(RADIANS(cg.geolocation_lat - sg.geolocation_lat) / 2), 2) +
        COS(RADIANS(sg.geolocation_lat)) * COS(RADIANS(cg.geolocation_lat)) *
        POWER(SIN(RADIANS(cg.geolocation_lng - sg.geolocation_lng) / 2), 2)
    ))) AS distance_km,
	COUNT(oi.order_item_id) item_count,
	SUM(p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000000.0 AS volume_m3,
	SUM(p.product_weight_g) / 1000.0 AS weight_kg,
	EXTRACT (EPOCH FROM AVG(order_delivered_carrier_date - order_approved_at)) / 86400 AS handling_days,
	EXTRACT (EPOCH FROM AVG(order_delivered_customer_date - order_delivered_carrier_date)) / 86400 AS transit_days,
	EXTRACT (EPOCH FROM ANY_VALUE(order_delivered_customer_date - order_approved_at)) / 86400 AS total_delivery_days
FROM silver.orders o
JOIN silver.customers c ON
	o.customer_id = c.customer_id
LEFT JOIN silver.geolocation cg ON 
	c.customer_zip_code_prefix  = cg.geolocation_zip_code_prefix
JOIN silver.order_items oi ON
	oi.order_id = o.order_id
JOIN silver.sellers s ON 
	oi.seller_id = s.seller_id
LEFT JOIN silver.geolocation sg ON 
	s.seller_zip_code_prefix = sg.geolocation_zip_code_prefix
JOIN silver.products p ON 
	oi.product_id = p.product_id
WHERE 
	order_status = 'delivered' AND
	order_delivered_customer_date IS NOT NULL AND
	order_estimated_delivery_date IS NOT NULL AND
	order_delivered_carrier_date IS NOT NULL AND 
	order_approved_at IS NOT NULL AND 
	order_purchase_timestamp >= '2017-01-01' AND
	order_delivered_customer_date >= order_approved_at AND 
	order_delivered_carrier_date >= order_approved_at
GROUP BY o.order_id
HAVING COUNT(DISTINCT s.seller_id) = 1;