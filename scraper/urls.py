from __future__ import annotations
import random
from typing import List
from .config import REAL_ESTATE_BASE


def build_url_pool() -> List[str]:
    suburb_slug = "st-kilda-3182"
    variants = []

    # Locality landing pages (Kasada-heavy, good test)
    variants.append(f"{REAL_ESTATE_BASE}/vic/{suburb_slug}/")

    # Buy listing pagination
    for n in range(1, 21):
        variants.append(
            f"{REAL_ESTATE_BASE}/buy/in-st+kilda,+vic+3182/list-{n}?includeSurrounding=false"
        )

    # Rent listing pagination
    for n in range(1, 21):
        variants.append(
            f"{REAL_ESTATE_BASE}/rent/in-st+kilda,+vic+3182/list-{n}?includeSurrounding=false"
        )

    # Sold
    for n in range(1, 11):
        variants.append(
            f"{REAL_ESTATE_BASE}/sold/in-st+kilda,+vic+3182/list-{n}?includeSurrounding=false"
        )

    # Nearby filters and sorts
    variants.extend([
        f"{REAL_ESTATE_BASE}/buy/property-apartment-in-st+kilda,+vic+3182/list-1",
        f"{REAL_ESTATE_BASE}/buy/property-house-in-st+kilda,+vic+3182/list-1",
        f"{REAL_ESTATE_BASE}/buy/with-1-bedroom-in-st+kilda,+vic+3182/list-1",
        f"{REAL_ESTATE_BASE}/rent/property-apartment-in-st+kilda,+vic+3182/list-2",
        f"{REAL_ESTATE_BASE}/buy/?q=st%20kilda%203182",
    ])

    random.shuffle(variants)
    return variants


def choose_random_urls(n: int) -> List[str]:
    pool = build_url_pool()
    return random.sample(pool, k=min(n, len(pool)))
