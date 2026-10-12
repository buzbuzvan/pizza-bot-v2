DROP TABLE IF EXISTS "order_toppings";

DROP TABLE IF EXISTS "toppings";

DROP TABLE IF EXISTS "pizza_ingredients";

DROP TABLE IF EXISTS "order_items";

DROP TABLE IF EXISTS "orders";

DROP TABLE IF EXISTS "sizes";

DROP TABLE IF EXISTS "customers";

DROP TABLE IF EXISTS "ingredients";

DROP TABLE IF EXISTS "pizzas";

DROP TYPE IF EXISTS "status_type";

CREATE TYPE "status_type" AS ENUM('Pending', 'Canceled', 'Confirmed', 'Ready');

CREATE TABLE "pizzas" (
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL UNIQUE,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "price" DECIMAL(7,2) NOT NULL CHECK("price" > 0)
);

CREATE TABLE "ingredients" (
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL UNIQUE
);

CREATE TABLE "customers"(
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "name" VARCHAR(32) NOT NULL
);

CREATE TABLE "sizes"(
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "size" VARCHAR(32) NOT NULL UNIQUE,
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    "multiplier" DECIMAL(7,2) NOT NULL CHECK("multiplier" > 0)
);

CREATE TABLE "orders" (
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "customer_id" BIGINT NOT NULL,
    "status" "status_type" NOT NULL DEFAULT ('Pending'),
    "total" DECIMAL(7,2) NOT NULL CHECK("total" > 0),
    "internal_note" VARCHAR(100),
    FOREIGN KEY("customer_id") REFERENCES "customers"("id")
);

CREATE TABLE "order_items"(
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "order_id" BIGINT NOT NULL,
    "pizza_id" BIGINT NOT NULL,
    "size_id" BIGINT NOT NULL,
    "price" DECIMAL(7,2) NOT NULL CHECK("price" > 0),
    "comment" VARCHAR(100),
    FOREIGN KEY("order_id") REFERENCES "orders"("id") ON DELETE CASCADE,
    FOREIGN KEY("size_id") REFERENCES "sizes"("id"),
    FOREIGN KEY("pizza_id") REFERENCES "pizzas"("id")
);

CREATE TABLE "pizza_ingredients"(
    "pizza_id" BIGINT NOT NULL,
    "ingredient_id" BIGINT NOT NULL,
    PRIMARY KEY("pizza_id", "ingredient_id"),
    FOREIGN KEY("pizza_id") REFERENCES "pizzas"("id"),
    FOREIGN KEY("ingredient_id") REFERENCES "ingredients"("id")
);

CREATE TABLE "toppings"(
    "id" BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "ingredient_id" BIGINT NOT NULL UNIQUE,
    "price" DECIMAL(7,2) NOT NULL CHECK("price" > 0),
    "is_active" BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY("ingredient_id") REFERENCES "ingredients"("id")
);

CREATE TABLE "order_toppings"(
    "order_item_id" BIGINT NOT NULL,
    "topping_id" BIGINT NOT NULL,
    "price" DECIMAL(7,2) NOT NULL CHECK("price" > 0),
    PRIMARY KEY("order_item_id", "topping_id"),
    FOREIGN KEY("order_item_id") REFERENCES "order_items"("id") ON DELETE CASCADE,
    FOREIGN KEY("topping_id") REFERENCES "toppings"("id")
);

CREATE INDEX "orders_customer_id_created_at_idx"
ON "orders" ("customer_id", "created_at" DESC);

CREATE INDEX "order_items_order_id_idx"
ON "order_items" ("order_id");

CREATE INDEX "order_items_pizza_id_size_id_idx"
ON "order_items" ("pizza_id", "size_id");