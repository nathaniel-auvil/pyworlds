class Building:
    def __init__(self, name, level=1, base_production=None, base_capacity=None, cost=None, build_time=60):
        self.name = name
        self.level = level
        self.base_production = base_production
        self.base_capacity = base_capacity
        self.production = base_production
        self.cost = cost or {'metal': 100, 'crystal': 50}
        self.build_time = build_time
        self.current_build = None

    def calculate_production(self, level=None):
        if self.base_production is None:
            return 0
        level = level or self.level
        return self.base_production * (1.25 ** (level - 1))

    def calculate_capacity(self, level=None):
        if self.base_capacity is None:
            return 0
        level = level or self.level
        return self.base_capacity * level

    def calculate_cost(self, level=None):
        level = level or self.level
        return {
            resource: int(amount * (1.5 ** (level - 1)))
            for resource, amount in self.cost.items()
        }

    def calculate_build_time(self, level=None):
        level = level or self.level
        return self.build_time * (1.2 ** level)

class BuildingFactory:
    @staticmethod
    def create_metal_mine():
        return Building(
            name='metal_mine',
            base_production=10,
            cost={'metal': 60, 'crystal': 15},
            build_time=60
        )

    @staticmethod
    def create_crystal_mine():
        return Building(
            name='crystal_mine',
            base_production=8,
            cost={'metal': 48, 'crystal': 24},
            build_time=80
        )

    @staticmethod
    def create_solar_plant():
        return Building(
            name='solar_plant',
            base_production=20,
            cost={'metal': 75, 'crystal': 30},
            build_time=100
        )

    @staticmethod
    def create_storage_facility():
        return Building(
            name='storage_facility',
            base_capacity=1000,
            cost={'metal': 100, 'crystal': 50},
            build_time=120
        )

    @staticmethod
    def create_shipyard():
        return Building(
            name='shipyard',
            level=0,
            cost={'metal': 400, 'crystal': 200},
            build_time=300
        )

    @staticmethod
    def create_research_lab():
        return Building(
            name='research_lab',
            level=0,
            cost={'metal': 200, 'crystal': 400},
            build_time=240
        ) 