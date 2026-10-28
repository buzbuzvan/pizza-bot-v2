BEGIN;

INSERT INTO "customers"("id", "phone") 
OVERRIDING SYSTEM VALUE
VALUES
(1, '+48123456789'),
(2, '+48987654321'),
(3, '+48213465780')
ON CONFLICT (id) DO NOTHING;

INSERT INTO "orders"("id", "created_at", "ready_by", "customer_id", "status", "total", "internal_note") 
OVERRIDING SYSTEM VALUE
VALUES
(1, '2026-10-24 18:00:00+02', '2026-10-24 18:15:00+02', 1, 'Ready', 59, 'Add napkins'),
(2, '2026-10-24 18:10:00+02', '2026-10-24 18:25:00+02', 2, 'Confirmed', 25, NULL),
(3, DEFAULT, NULL, 3, 'Pending', 60, NULL),
(4, '2026-10-24 18:30:00+02', '2026-10-24 18:40:00+02', 1, 'Confirmed', 36.5, 'Cut')
ON CONFLICT (id) DO NOTHING;

INSERT INTO "order_items"("id", "order_id", "pizza_id", "size_id", "price", "comment") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 1, 2, 1, 20, 'No Basil, Extra Mozzarella Cheese'),
(2, 1, 1, 3, 24, NULL),
(3, 2, 6, 1, 18, 'No Parmesan Cheese'),
(4, 3, 4, 3, 36, 'Extra Spicy Salami'),
(5, 3, 3, 1, 17, 'No Tomato Sauce'),
(6, 4, 5, 2, 25.5, 'Extra Mushrooms')
ON CONFLICT (id) DO NOTHING;

INSERT INTO "order_toppings"("order_item_id", "topping_id", "price") VALUES
(1, 1, 5),
(4, 4, 7),
(6, 8, 5)
ON CONFLICT DO NOTHING;

INSERT INTO "order_soft_drinks"("order_id", "soft_drink_id", "quantity", "price") 
VALUES
(1, 1, 2, 10),
(2, 1, 1, 5),
(2, 3, 1, 2),
(4, 2, 1, 6)
ON CONFLICT DO NOTHING;

SELECT setval('customers_id_seq', (SELECT MAX(id) FROM "customers"));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM "orders"));
SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM "order_items"));

COMMIT;