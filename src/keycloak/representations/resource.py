# -*- coding: utf-8 -*-
from dataclasses import dataclass
from typing import List


@dataclass
class Resource:
    resource_id: str
    resource_scopes: List
