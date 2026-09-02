# Olist Ecommerce Analytics

## Domain Context

### What is Olist?

Olist is a marketplace aggregator. Sellers list their products on the platform, and Olist distributes them across multiple online marketplaces under the unified "Olist Store" account. This saves sellers the headache of managing multi-channel inventory while instantly boosting their visibility; in return, Olist charges a subscription fee and takes a commission on sales.

## Building a dashboard
A dashboard must answers:
1. Are we winning or lossing (descriptive)
2. Why is it happening (causal)
3. what do we need to do (prescriptive)

Target audience: Chief Operating Officer
in charge of daily operation, making sure efficiency, speed, and reliability of these operation. 

The daily operation we are focussing is logistics (how item shipped from seller to buyer), as the olist dataset contains a lot of data about it. 

What winning and lossing looks like in logistics? 
1. Metric : Service Level Agreement (SLA) Rate
   Description: percentage of package that is delivered within the estimated delivery time
   Baseline : <90% (losing), 90-95% (okay), >95% (winning)
2. Metric : Delivery time
   Description : from payment approved to delivered
   Baseline : Based on review score, stratified by volume, surface area, (within state, outside state), distance.
3. Metric : Seller Dispatch Compliance 
   Description : duration from payment approved to hand over to postal carrier
   Baseline : Quantiles, stratified by volume and surface area, percentage within deadline <90% (losing), 90-95% (okay), >95% (winning)
4. Metric : Carrier Net Transit Time
   Description : duration between `order_delivered_carrier_date` and `order_delivered_customer_date`
   Baseline : Quantiles, stratified by (within state, outside state), distance, volume, surface area
5. Metric : Freight ratio
   Description : $$\text{Freight Ratio} = \frac{\text{Freight Value}}{\text{Product Value} + \text{Freight Value}}$$ 
   Baseline : <12% (Winning), 12-15% (okay), >15% (losing)
   [Source for baseline](https://magebit.com/blogs/shipping-pricing-strategy-for-ecommerce-balance-cost-conversion-and-margin)


TODO:
- try to handle the canceled and unavailable orders.