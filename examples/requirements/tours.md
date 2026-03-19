# Tour Booking Analytics — Business Requirements

## Overview

A travel company offers guided tours worldwide. They want a dimensional model to
analyse booking trends, revenue, guide performance, and customer behaviour.

## Key Business Questions

1. **Revenue** — What is total booking revenue by tour, destination, category, and month?
2. **Bookings** — How many bookings are confirmed, completed, or cancelled each month?
3. **Guests** — What is the average party size per tour category?
4. **Customers** — Which countries generate the most bookings and revenue?
5. **Guides** — Which guides handle the most bookings and highest revenue tours?
6. **Tours** — Which tours and destinations are most popular?
7. **Cancellations** — What is the cancellation rate by tour category and month?

## Grain

- **Fact**: one row per booking (booking_id is the natural key)

## Expected Dimensions

- **Date** — booking date and travel date (year, quarter, month, day)
- **Tour** — tour name, destination, category, duration, price
- **Customer** — name, email, country
- **Guide** — name, languages, specialty, experience

## Key Metrics

- `total_amount` — booking revenue (SUM)
- `num_guests` — guests per booking (SUM, AVG)
- `booking_count` — number of bookings (COUNT)
- `cancellation_rate` — cancelled / total bookings (derived)
