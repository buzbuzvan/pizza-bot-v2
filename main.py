from enum import Enum
from fastapi import FastAPI, status, HTTPException, Path, Depends
from pydantic import BaseModel, Field, field_validator, StringConstraints
import itertools
from typing import Annotated
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

app = FastAPI()


class PizzaName(str, Enum):
    MARGHERITA = "Margherita"
    PARMA = "Parma"
    COTTO = "Cotto"
    DIAVOLA = "Diavola"
    FUNGHI = "Funghi"
    QUATTRO = "Quattro"


class PizzaSize(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class Status(str, Enum):
    PENDING = "Pending"
    CANCELED = "Canceled"
    CONFIRMED = "Confirmed"
    READY = "Ready"


class Topping(str, Enum):
    MOZZARELLA_CHEESE = "Mozzarella Cheese"
    HAM_DI_PARMA = "Ham Di Parma"
    HAM_COTTO = "Ham Cotto"
    PARMESAN_CHEESE = "Parmesan Cheese"
    SPICY_SALAMI = "Spicy Salami"
    MUSHROOMS = "Mushrooms"
    GORGONZOLA_CHEESE = "Gorgonzola Cheese"
    PROVOLA_CHEESE = "Provola Cheese"


class SoftDrink(str, Enum):
    COLA = "Cola"
    ORANGE_JUICE = "Orange Juice"
    STILL_WATER = "Still Water"


class OrderSoftDrink(BaseModel):
    name: SoftDrink
    count: int = Field(ge=1, le=25)


class OrderTopping(BaseModel):
    name: Topping


def validate_unique(v: list | None):
    if v is None:
        return v

    seen = set()
    for item in v:
        if item.name in seen:
            raise ValueError(
                f'Item "{item.name.value}" cannot be added again. Each item must be unique.'
            )
        seen.add(item.name)

    return v


class OrderItem(BaseModel):
    name: PizzaName
    size: PizzaSize
    comment: OrderText | None = None

    toppings: list[OrderTopping] | None = Field(
        default=None, min_length=1, max_length=8
    )

    @field_validator("toppings")
    @classmethod
    def validate_unique_toppings(
        cls, v: list[OrderTopping] | None
    ) -> list[OrderTopping] | None:
        return validate_unique(v)


class Order(BaseModel):
    items: list[OrderItem] = Field(min_length=1, max_length=25)
    soft_drinks: list[OrderSoftDrink] | None = Field(
        default=None, min_length=1, max_length=25
    )

    @field_validator("soft_drinks")
    @classmethod
    def validate_unique_soft_drinks(
        cls, v: list[OrderSoftDrink] | None
    ) -> list[OrderSoftDrink] | None:
        return validate_unique(v)


class OrderInDB(Order):
    id: int | None = None
    phone: PhoneE164 | None = None
    created_at: datetime | None = None
    ready_by: datetime | None = None
    total: OrderTotal
    status: Status = Status.PENDING
    internal_note: OrderText | None = None


class OrderOut(Order):
    id: int
    phone: PhoneE164 | None = None
    total: OrderTotal
    status: Status
    ready_by: datetime | None = None


class InternalNoteUpdate(BaseModel):
    internal_note: OrderText


class ReadyByUpdate(BaseModel):
    prep_minutes: int = Field(ge=10, le=40)


business_tz = ZoneInfo("Europe/Warsaw")

counter = itertools.count(start=1, step=1)

sizes = {
    PizzaSize.SMALL: Decimal("1"),
    PizzaSize.MEDIUM: Decimal("1.5"),
    PizzaSize.LARGE: Decimal("2"),
}

prices = {
    PizzaName.MARGHERITA: Decimal("12"),
    PizzaName.PARMA: Decimal("20"),
    PizzaName.COTTO: Decimal("17"),
    PizzaName.DIAVOLA: Decimal("18"),
    PizzaName.FUNGHI: Decimal("17"),
    PizzaName.QUATTRO: Decimal("18"),
}

prices_toppings = {
    Topping.MOZZARELLA_CHEESE: Decimal("5"),
    Topping.GORGONZOLA_CHEESE: Decimal("5"),
    Topping.PARMESAN_CHEESE: Decimal("5"),
    Topping.PROVOLA_CHEESE: Decimal("5"),
    Topping.HAM_COTTO: Decimal("7"),
    Topping.HAM_DI_PARMA: Decimal("8"),
    Topping.SPICY_SALAMI: Decimal("7"),
    Topping.MUSHROOMS: Decimal("5"),
}

prices_soft_drinks = {
    SoftDrink.COLA: Decimal("5"),
    SoftDrink.ORANGE_JUICE: Decimal("6"),
    SoftDrink.STILL_WATER: Decimal("2"),
}

orders_db: dict[int, OrderInDB] = {}


def get_order_or_404(order_id: Annotated[int, Path(ge=1)]):

    order = orders_db.get(order_id)
    if order is not None:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


OrderFromPath = Annotated[OrderInDB, Depends(get_order_or_404)]

PhoneE164 = Annotated[str, StringConstraints(pattern=r"^\+[1-9]\d{6,14}$")]

OrderTotal = Annotated[
    Decimal, Field(max_digits=7, decimal_places=2, examples=[Decimal("100.00")])
]

OrderText = Annotated[
    str, StringConstraints(min_length=2, max_length=100, strip_whitespace=True)
]


@app.get("/orders/{order_id}", response_model=OrderOut)
def show_order(
    order_in_db: OrderFromPath,
):

    return order_in_db


def insert_order_into_db(order: Order, total: OrderTotal):

    saved_order = OrderInDB(
        items=order.items, total=total, soft_drinks=order.soft_drinks
    )
    saved_order.phone = saved_phone("+48123123123")
    created_at = datetime.now(business_tz)
    saved_order.created_at = created_at
    order_id = next(counter)
    saved_order.id = order_id
    orders_db[order_id] = saved_order

    return saved_order


def saved_phone(phone_number):
    return phone_number


def order_total(order: Order):
    total: OrderTotal = Decimal("0")
    for item in order.items:
        amount = prices[item.name] * sizes[item.size]
        result = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total += result
        if item.toppings is None:
            continue
        for topping in item.toppings:
            total += prices_toppings[topping.name]
    if order.soft_drinks is None:
        return total
    for product in order.soft_drinks:
        summation = product.count * prices_soft_drinks[product.name]
        total += summation
    return total


def calculate_ready_time(prep_minutes: int) -> datetime:
    confirmed_order_time = datetime.now(business_tz)
    ready_time = confirmed_order_time + timedelta(minutes=prep_minutes)
    return ready_time


@app.post(
    "/orders",
    response_model=OrderOut,
    status_code=status.HTTP_201_CREATED,
)
def create_order(order: Order):

    total = order_total(order)

    saved_order = insert_order_into_db(order, total)
    return saved_order


@app.put("/orders/{order_id}/internal_note", status_code=status.HTTP_204_NO_CONTENT)
def update_internal_note(
    order_in_db: OrderFromPath,
    data: InternalNoteUpdate,
):

    order_in_db.internal_note = data.internal_note


@app.put(
    "/orders/{order_id}/confirmed_and_ready_by",
    status_code=status.HTTP_204_NO_CONTENT,
)
def update_confirmed_and_ready_by(
    order_in_db: OrderFromPath,
    data: ReadyByUpdate,
):
    if order_in_db.status != Status.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot confirm an order that is already confirmed or ready or canceled",
        )
    prep_minutes = data.prep_minutes
    ready_time = calculate_ready_time(prep_minutes)
    order_in_db.ready_by = ready_time
    order_in_db.status = Status.CONFIRMED


@app.put("/orders/{order_id}/canceled", status_code=status.HTTP_204_NO_CONTENT)
def update_status_canceled(
    order_in_db: OrderFromPath,
):

    if order_in_db.status != Status.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot cancel an order that is already confirmed or ready or canceled",
        )

    order_in_db.status = Status.CANCELED


@app.put("/orders/{order_id}/ready", status_code=status.HTTP_204_NO_CONTENT)
def update_status_ready(
    order_in_db: OrderFromPath,
):

    if order_in_db.status != Status.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order must be confirmed before it can be marked as ready",
        )

    order_in_db.status = Status.READY
