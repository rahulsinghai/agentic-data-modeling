# E-Commerce Analytics Requirements

## Business Context
We operate an online retail store selling products across multiple categories. We need a dimensional model to support analytics on sales performance, customer behavior, and product trends.

## Key Business Questions
1. What are our total sales by product category, by month?
2. Who are our top customers by revenue and order frequency?
3. What is our average order value trend over time?
4. Which products have the highest return/cancellation rates?
5. What is the geographic distribution of our sales?
6. How does discount usage affect total revenue and margin?

## Source Data
- **customers**: Customer master data with demographics
- **products**: Product catalog with pricing
- **categories**: Product category hierarchy
- **orders**: Order headers with status and totals
- **order_items**: Line-item detail with quantities and pricing

## Requirements
- Track order-level and line-item-level metrics
- Support analysis by customer, product, category, date, and geography
- Calculate revenue, cost, margin, and discount metrics
- Handle order status (completed, pending, cancelled, returned) as a dimension
- Date dimension should support year/quarter/month/week/day analysis
