"""Fixture restaurants for filter unit tests."""

from __future__ import annotations

from domain.models import BudgetBucket, RestaurantRecord

FIXTURE_RESTAURANTS: list[RestaurantRecord] = [
    RestaurantRecord(
        id="r1",
        name="Italian Place",
        location="Bangalore",
        cuisines=["italian", "pizza"],
        rating=4.5,
        cost_for_two=450.0,
        cost_bucket=BudgetBucket.MEDIUM,
        attributes={"area": "Koramangala"},
    ),
    RestaurantRecord(
        id="r2",
        name="Budget Chinese",
        location="Bangalore",
        cuisines=["chinese"],
        rating=3.8,
        cost_for_two=300.0,
        cost_bucket=BudgetBucket.LOW,
        attributes={"area": "BTM"},
    ),
    RestaurantRecord(
        id="r3",
        name="Fine Italian",
        location="Bangalore",
        cuisines=["italian"],
        rating=4.9,
        cost_for_two=800.0,
        cost_bucket=BudgetBucket.HIGH,
        attributes={"area": "Indiranagar"},
    ),
    RestaurantRecord(
        id="r4",
        name="Delhi Diner",
        location="Delhi",
        cuisines=["italian"],
        rating=4.2,
        cost_for_two=500.0,
        cost_bucket=BudgetBucket.MEDIUM,
    ),
    RestaurantRecord(
        id="r5",
        name="No Cost Bucket",
        location="Bangalore",
        cuisines=["italian"],
        rating=4.0,
        cost_for_two=None,
        cost_bucket=None,
    ),
    RestaurantRecord(
        id="r6",
        name="Low Rated Italian",
        location="Bangalore",
        cuisines=["italian"],
        rating=3.0,
        cost_for_two=350.0,
        cost_bucket=BudgetBucket.LOW,
    ),
    RestaurantRecord(
        id="r7",
        name="North Indian Hub",
        location="Bangalore",
        cuisines=["north indian", "mughlai"],
        rating=4.1,
        cost_for_two=400.0,
        cost_bucket=BudgetBucket.LOW,
    ),
]
