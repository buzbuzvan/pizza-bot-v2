BEGIN;

INSERT INTO "kitchen_wait"("id") VALUES
(1)
ON CONFLICT (id) DO NOTHING;

INSERT INTO "pizzas"("id", "name", "is_active", "price") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 'Margherita', DEFAULT, 12),
(2, 'Parma', DEFAULT, 20),
(3, 'Cotto', DEFAULT, 17),
(4, 'Diavola', DEFAULT, 18),
(5, 'Funghi', FALSE, 17),
(6, 'Quattro', DEFAULT, 18)
ON CONFLICT (id) DO NOTHING;

INSERT INTO "soft_drinks"("id", "name", "is_active", "price") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 'Cola', DEFAULT, 5),
(2, 'Orange Juice', FALSE, 6),
(3, 'Still Water', DEFAULT, 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO "ingredients"("id", "name") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 'Dough'),
(2, 'Tomato Sauce'),
(3, 'Mozzarella Cheese'),
(4, 'Ham Di Parma'),
(5, 'Ham Cotto'),
(6, 'Basil'),
(7, 'Parmesan Cheese'),
(8, 'Spicy Salami'),
(9, 'Mushrooms'),
(10, 'Gorgonzola Cheese'),
(11, 'Provola Cheese')
ON CONFLICT (id) DO NOTHING;

INSERT INTO "sizes"("id", "size", "is_active", "multiplier") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 'Small', DEFAULT, 1),
(2, 'Medium', FALSE, 1.5),
(3, 'Large', DEFAULT, 2)
ON CONFLICT (id) DO NOTHING;

INSERT INTO "pizza_ingredients" ("pizza_id", "ingredient_id") VALUES
  (1, 1),
  (1, 2),
  (1, 3),
  (1, 6),
  (1, 7),
  (2, 1),
  (2, 3),
  (2, 4),
  (2, 6),
  (2, 7),
  (3, 1),
  (3, 2),
  (3, 3),
  (3, 5),
  (3, 6),
  (3, 7),
  (4, 1),
  (4, 2),
  (4, 3),
  (4, 6),
  (4, 8),
  (4, 11),
  (5, 1),
  (5, 3),
  (5, 6),
  (5, 7),
  (5, 9),
  (6, 1),
  (6, 2),
  (6, 3),
  (6, 7),
  (6, 10),
  (6, 11)
ON CONFLICT DO NOTHING;

INSERT INTO "toppings"("id", "ingredient_id", "is_active", "price") 
OVERRIDING SYSTEM VALUE
VALUES
(1, 3, DEFAULT, 5),
(2, 4, DEFAULT, 8),
(3, 5, DEFAULT, 7),
(4, 8, DEFAULT, 7),
(5, 7, DEFAULT, 5),
(6, 10, DEFAULT, 5),
(7, 11, DEFAULT, 5),
(8, 9, FALSE, 5)
ON CONFLICT (id) DO NOTHING;

SELECT setval('pizzas_id_seq', (SELECT MAX(id) FROM "pizzas"));
SELECT setval('soft_drinks_id_seq', (SELECT MAX(id) FROM "soft_drinks"));
SELECT setval('ingredients_id_seq', (SELECT MAX(id) FROM "ingredients"));
SELECT setval('sizes_id_seq', (SELECT MAX(id) FROM "sizes"));
SELECT setval('toppings_id_seq', (SELECT MAX(id) FROM "toppings"));

COMMIT;