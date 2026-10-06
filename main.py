from enum import Enum
from fastapi import FastAPI, status, HTTPException, Path, Depends
from pydantic import BaseModel, Field
import itertools
from typing import Annotated

app = FastAPI()


class Name(str, Enum):
    MARGHERITA = "Margherita"
    PARMA = "Parma"
    COTTO = "Cotto"


class Size(str, Enum):
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"


class Status(str, Enum):
    PENDING = "Pending"
    CANCELED = "Canceled"
    CONFIRMED = "Confirmed"
    READY = "Ready"


class OrderItem(BaseModel):
    name: Name
    size: Size
    count: int = Field(ge=1, le=50)


class Order(BaseModel):
    items: list[OrderItem] = Field(min_length=1, max_length=25)


class OrderInDB(Order):
    id: int | None = None
    total: float
    status: Status = Status.PENDING
    internal_note: str | None = None


class OrderOut(Order):

    id: int
    total: float
    status: Status


class InternalNoteUpdate(BaseModel):
    internal_note: str = Field(min_length=3, max_length=100)


class StatusUpdate(BaseModel):
    status: Status


counter = itertools.count(start=1, step=1)

sizes = {Size.SMALL: 1, Size.MEDIUM: 1.5, Size.LARGE: 2}

prices = {Name.MARGHERITA: 13, Name.PARMA: 16, Name.COTTO: 15}
orders_db: dict[int, OrderInDB] = {}


def get_order_or_404(order_id: Annotated[int, Path(ge=1)]):

    order = orders_db.get(order_id)
    if order is not None:
        return order
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")


OrderFromPath = Annotated[OrderInDB, Depends(get_order_or_404)]


@app.get("/orders/{order_id}", response_model=OrderOut)
def show_order(
    order_in_db: OrderFromPath,
):

    return order_in_db


def insert_order_into_db(order: Order, total: float):

    saved_order = OrderInDB(items=order.items, total=total)
    order_id = next(counter)
    saved_order.id = order_id
    orders_db[order_id] = saved_order

    return saved_order


def order_total(order: Order):
    total: float = 0
    for item in order.items:
        amount = item.count * prices[item.name] * sizes[item.size]
        total += amount
    return total


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


@app.put("/orders/{order_id}/status", status_code=status.HTTP_204_NO_CONTENT)
def update_status(
    order_in_db: OrderFromPath,
    data: StatusUpdate,
):

    order_in_db.status = data.status
