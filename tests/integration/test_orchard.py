from datetime import datetime, timedelta, timezone

from models import (
    db,
    LandType,
    SeedType,
    FruitType,
    OrchardItem,
    UserLand,
    UserOrchardInventory,
    UserHarvestedFruit,
)
from tests.conftest import login
from blueprints.orchard import get_or_create_user_orchard


def setup_orchard_basics(app):
    with app.app_context():
        land_type = LandType(
            name="Basic",
            name_en="Basic",
            level=1,
            icon="*",
            growth_reduction=0.0,
        )
        db.session.add(land_type)
        db.session.commit()

        seed = SeedType(
            name="Apple Seed",
            name_en="Apple Seed",
            price=2,
            growth_hours=1,
            available=True,
        )
        db.session.add(seed)
        db.session.commit()

        fruit = FruitType(
            seed_type_id=seed.id,
            name="Apple",
            name_en="Apple",
            rarity="SR",
            points=5,
            drop_rate=1.0,
            is_showcase_worthy=True,
        )
        db.session.add(fruit)

        item = OrchardItem(
            name="Fertilizer",
            name_en="Fertilizer",
            item_type="fertilizer",
            price=1,
            effect_value=2.0,
            available=True,
        )
        db.session.add(item)
        db.session.commit()

        land_type_id = land_type.id
        seed_id = seed.id
        fruit_id = fruit.id
        item_id = item.id
        db.session.expunge(land_type)
        db.session.expunge(seed)
        db.session.expunge(fruit)
        db.session.expunge(item)
        return land_type_id, seed_id, fruit_id, item_id


def test_buy_seed_and_plant_harvest_flow(client, make_user, app):
    """Happy path for buying seed, planting, and harvesting fruit."""
    _, seed_id, _, _ = setup_orchard_basics(app)
    user = make_user("orcharduser", "orchard@example.com", coins=10)
    login(client, user.username, "password123")

    response = client.post("/orchard/api/buy-seed", json={"seed_id": seed_id, "quantity": 1})
    assert response.status_code == 200
    assert response.get_json()["inventory_count"] == 1

    with app.app_context():
        get_or_create_user_orchard(user.id)
        land = UserLand.query.first()
        assert land is not None
        land_id = land.id

    response = client.post("/orchard/api/plant", json={"land_id": land_id, "seed_id": seed_id})
    assert response.status_code == 200

    with app.app_context():
        land = db.session.get(UserLand, land_id)
        land.matures_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
        land.plant_status = "growing"
        db.session.commit()

    response = client.post("/orchard/api/harvest", json={"land_id": land_id})
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["fruit"]["auto_showcase"] is True

    with app.app_context():
        harvested = UserHarvestedFruit.query.filter_by(user_id=user.id).first()
        assert harvested is not None


def test_buy_seed_insufficient_coins(client, make_user, app):
    """Buying seeds without enough coins should fail."""
    _, seed_id, _, _ = setup_orchard_basics(app)
    user = make_user("poor", "poor@example.com", coins=0)
    login(client, user.username, "password123")

    response = client.post("/orchard/api/buy-seed", json={"seed_id": seed_id, "quantity": 1})
    assert response.status_code == 400


def test_use_item_updates_maturity(client, make_user, app):
    """Using an item should reduce maturity time."""
    _, seed_id, _, item_id = setup_orchard_basics(app)
    user = make_user("itemuser", "item@example.com", coins=10)
    login(client, user.username, "password123")

    client.post("/orchard/api/buy-seed", json={"seed_id": seed_id, "quantity": 1})

    with app.app_context():
        get_or_create_user_orchard(user.id)
        inv = UserOrchardInventory(
            user_id=user.id,
            item_type="item",
            item_id=item_id,
            quantity=1,
        )
        db.session.add(inv)
        land = UserLand.query.first()
        land.plant_status = "growing"
        land.current_seed_id = seed_id
        land.planted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        land.matures_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=5)
        db.session.commit()
        land_id = land.id
        before = land.matures_at

    response = client.post("/orchard/api/use-item", json={"land_id": land_id, "item_id": item_id})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["land"]["crop_fertilizer_quality"] == 2.0
    assert payload["land"]["crop_water_count"] == 0

    with app.app_context():
        land = db.session.get(UserLand, land_id)
        assert land.matures_at < before
        assert float(land.crop_fertilizer_quality or 0) == 2.0


def test_use_item_water_increments_water_count(client, make_user, app):
    """Water should increment crop_water_count (fertilizer quality unchanged)."""
    _, seed_id, _, _ = setup_orchard_basics(app)
    user = make_user("wateruser", "water@example.com", coins=10)
    login(client, user.username, "password123")

    client.post("/orchard/api/buy-seed", json={"seed_id": seed_id, "quantity": 1})

    with app.app_context():
        get_or_create_user_orchard(user.id)
        water = OrchardItem(
            name="Test Water",
            name_en="Test Water",
            item_type="water",
            effect_value=1.0,
            price=1,
            available=True,
        )
        db.session.add(water)
        db.session.commit()
        water_id = water.id
        inv = UserOrchardInventory(
            user_id=user.id,
            item_type="item",
            item_id=water_id,
            quantity=2,
        )
        db.session.add(inv)
        land = UserLand.query.first()
        land.plant_status = "growing"
        land.current_seed_id = seed_id
        land.planted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        land.matures_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=5)
        db.session.commit()
        land_id = land.id

    r1 = client.post("/orchard/api/use-item", json={"land_id": land_id, "item_id": water_id})
    assert r1.status_code == 200
    assert r1.get_json()["land"]["crop_water_count"] == 1
    r2 = client.post("/orchard/api/use-item", json={"land_id": land_id, "item_id": water_id})
    assert r2.get_json()["land"]["crop_water_count"] == 2


def test_plant_resets_crop_care_counters(client, make_user, app):
    """New plant should clear water / fertilizer care totals."""
    _, seed_id, _, _ = setup_orchard_basics(app)
    user = make_user("resetcare", "resetcare@example.com", coins=10)
    login(client, user.username, "password123")

    client.post("/orchard/api/buy-seed", json={"seed_id": seed_id, "quantity": 2})

    with app.app_context():
        get_or_create_user_orchard(user.id)
        land = UserLand.query.first()
        land_id = land.id
        land.crop_water_count = 3
        land.crop_fertilizer_quality = 5.0
        land.plant_status = "idle"
        land.current_seed_id = None
        db.session.commit()

    assert client.post(
        "/orchard/api/plant", json={"land_id": land_id, "seed_id": seed_id}
    ).status_code == 200

    with app.app_context():
        land = db.session.get(UserLand, land_id)
        assert land.crop_water_count == 0
        assert float(land.crop_fertilizer_quality or 0) == 0.0


def test_get_land_status(client, make_user, app):
    """Land status endpoint should return user lands."""
    setup_orchard_basics(app)
    user = make_user("landuser", "land@example.com", coins=0)
    login(client, user.username, "password123")

    response = client.get("/orchard/api/land-status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert len(data["lands"]) >= 1
