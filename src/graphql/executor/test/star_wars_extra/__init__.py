"""Provides additional GraphQL-enabled objects for Star Wars.

While graphql.executor.test.star_wars has objects based on official test
cases, graphql.executor.test.star_wars_extra has our own custom
additions.
"""

from faction import SwFaction
from introduce_ship_mutation import SwIntroduceShipMutation
from search import SwSearch
from ship import get_sw_ship
from ship import SwShip
from users import SwUsers
