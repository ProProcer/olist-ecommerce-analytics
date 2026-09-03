-- Build the gold layer consumed by the Streamlit dashboard (app.py).
-- Usage: psql -d olist_ecommerce -f sql/04_build_gold_layer.sql
CREATE SCHEMA IF NOT EXISTS gold;

SET search_path TO gold;

-- Monthly logistics KPI table for the dashboard's trend and metric widgets.
CREATE TABLE gold.monthly_logistics_metrics AS
WITH delivery_time_metrics AS (
	SELECT 
		DATE_TRUNC('month', order_purchase_timestamp) AS year_month,
		COUNT(*) AS total_orders,
		SUM(CASE 
			WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1
			ELSE 0
		END) AS on_time_orders,
		AVG(CASE 
			WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1
			ELSE 0
		END) AS on_time_delivery_rate,
		EXTRACT (EPOCH FROM AVG(order_delivered_carrier_date - order_approved_at)) / 86400 AS handling_days,
		EXTRACT (EPOCH FROM AVG(order_delivered_customer_date - order_delivered_carrier_date)) / 86400 AS transit_days,
		EXTRACT (EPOCH FROM AVG(order_delivered_customer_date - order_approved_at)) / 86400 AS total_delivery_days
	FROM silver.orders
	WHERE 
		order_status = 'delivered' AND
		order_delivered_customer_date IS NOT NULL AND
		order_estimated_delivery_date IS NOT NULL AND
		order_delivered_carrier_date IS NOT NULL AND 
		order_approved_at IS NOT NULL AND 
		order_purchase_timestamp >= '2017-01-01'
	GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
	ORDER BY year_month
),
freight_metrics AS (
	SELECT 
		DATE_TRUNC('month', o.order_purchase_timestamp) AS year_month,
		COUNT(*) AS total_items,
		SUM(oi.freight_value) AS total_freight_value,
		SUM(p.product_weight_g) / 1000.0 AS total_freight_weight_kg,
		SUM(p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000000.0 AS total_freight_volume_m3
	FROM silver.orders o
	JOIN silver.order_items oi ON 
		oi.order_id = o.order_id
	JOIN silver.products p ON
		p.product_id = oi.product_id
	WHERE 
		o.order_delivered_carrier_date IS NOT NULL AND
		o.order_status = 'delivered' AND 
		o.order_purchase_timestamp BETWEEN '2017-01-01' AND '2018-08-31' AND
		oi.freight_value >= 0 AND
		p.product_weight_g > 0 AND
		p.product_length_cm > 0 AND 
		p.product_height_cm > 0 AND 
		p.product_width_cm > 0 
	GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)
	ORDER BY year_month
),
order_counts AS (
	SELECT 
	    DATE_TRUNC('month', order_purchase_timestamp) AS year_month,
	    COUNT(CASE WHEN order_status = 'created' THEN 1 END) AS created_count,
	    COUNT(CASE WHEN order_status = 'approved' THEN 1 END) AS approved_count,
	    COUNT(CASE WHEN order_status = 'processing' THEN 1 END) AS processing_count,
	    COUNT(CASE WHEN order_status = 'invoiced' THEN 1 END) AS invoiced_count,
	    COUNT(CASE WHEN order_status = 'shipped' THEN 1 END) AS shipped_count,
	    COUNT(CASE WHEN order_status = 'delivered' THEN 1 END) AS delivered_count,
	    COUNT(CASE WHEN order_status = 'unavailable' THEN 1 END) AS unavailable_count,
	    COUNT(CASE WHEN order_status = 'canceled' THEN 1 END) AS canceled_count
	FROM silver.orders
	WHERE order_purchase_timestamp BETWEEN '2017-01-01' AND '2018-8-31'
	GROUP BY DATE_TRUNC('month', order_purchase_timestamp)
	ORDER BY DATE_TRUNC('month', order_purchase_timestamp)
)
SELECT 
    dt.year_month,
    dt.total_orders,
    dt.on_time_orders,
    dt.on_time_delivery_rate,
    dt.handling_days,
    dt.transit_days,
    dt.total_delivery_days,
    f.total_items,
    f.total_freight_value,
    f.total_freight_weight_kg,
    f.total_freight_volume_m3,
    oc.created_count,
	oc.approved_count,
	oc.processing_count,
	oc.invoiced_count,
	oc.shipped_count,
	oc.delivered_count,
	oc.unavailable_count,
	oc.canceled_count
FROM delivery_time_metrics dt
JOIN freight_metrics f ON 
	dt.year_month = f.year_month
JOIN order_counts oc ON 
	oc.year_month = dt.year_month
ORDER BY dt.year_month;

-- Order-level fact table joined with OOF anomaly scores in the dashboard.
-- order_id is required by app.py for the merge with data/processed OOF CSVs.
CREATE TABLE gold.fct_orders AS 
SELECT
	order_id,
	order_approved_at,
	EXTRACT (EPOCH FROM (order_delivered_carrier_date - order_approved_at)) / 86400 AS handling_days,
	EXTRACT (EPOCH FROM (order_delivered_customer_date - order_delivered_carrier_date)) / 86400 AS transit_days,
	EXTRACT (EPOCH FROM (order_delivered_customer_date - order_approved_at)) / 86400 AS total_delivery_days,
	CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END AS is_on_time
FROM silver.orders
WHERE 
	order_status = 'delivered' AND
	order_delivered_customer_date IS NOT NULL AND
	order_estimated_delivery_date IS NOT NULL AND
	order_delivered_carrier_date IS NOT NULL AND 
	order_approved_at IS NOT NULL;
