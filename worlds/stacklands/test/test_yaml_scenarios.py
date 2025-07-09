from .bases import StacklandsWorldTestBase

class TestDarkForestEnabled(StacklandsWorldTestBase):

    options = {
        "dark_forest": True,
    }

    def test_dark_forest_enabled(self) -> None:
        """Test that relevant locations and items exist in the pool when Dark Forest is enabled in the YAML"""

        for location in self.dark_forest_locations:
            try:
                self.assertIsNotNone(self.world.get_location(location))
            except Exception:
                self.fail(f"YAML set to {self.world.options.dark_forest} but '{location}' does not exist in the location pool.")

class TestDarkForestDisabled(StacklandsWorldTestBase):

    options = {
        "dark_forest": False,
    }

    def test_dark_forest_disabled(self) -> None:
        """Test that relevant locations and items do not exist in the pool when Dark Forest is disabled in the YAML"""
        
        # Cycle through dark forest locations
        for location in self.dark_forest_locations:
            with self.assertRaises(KeyError, msg=f"YAML option is {self.world.options.dark_forest} but '{location}' location check exists in the pool."):
                self.world.get_location(location)

        # Cycle through dark forest items
        for item in self.dark_forest_items:
            with self.assertRaises(ValueError, msg=f"YAML option is {self.world.options.dark_forest} but '{item}' item exists in the pool."):
                self.get_item_by_name(item)

class TestMobsanityEnabledWithDarkForest(StacklandsWorldTestBase):

    options = {
        "mobsanity": True,
        "dark_forest": True
    }

    def test_mobsanity_enabled_with_dark_forest(self) -> None:
        """Test that relevant locations exist in the pool when Mobsanity is enabled and Dark Forest is enabled in the YAML"""

        for location in self.mobsanity_locations + self.dark_forest_mobsanity_locations:
            try:
                self.assertIsNotNone(self.world.get_location(location))
            except Exception:
                self.fail(f"YAML set to {self.world.options.mobsanity} and {self.world.options.dark_forest} but '{location}' does not exist in the location pool.")

class TestMobsanityEnabledWithoutDarkForest(StacklandsWorldTestBase):

    options = {
        "mobsanity": True,
        "dark_forest": False
    }

    def test_mobsanity_enabled_without_dark_forest(self) -> None:
        """Test that relevant locations exist in the pool when Mobsanity is enabled and Dark Forest is disabled in the YAML"""

        # Assert that Mobsanity locations exist
        for location in self.mobsanity_locations:
            try:
                self.assertIsNotNone(self.world.get_location(location))
            except Exception:
                self.fail(f"YAML set to {self.world.options.mobsanity} but '{location}' does not exist in the location pool.")

        # Assert that Mobsanity locations for Dark Forest don't exist
        for location in self.dark_forest_mobsanity_locations:
            with self.assertRaises(KeyError, msg=f"YAML option is {self.world.options.mobsanity} but '{location}' location check exists in the pool."):
                self.world.get_location(location)

class TestMobsanityDisabled(StacklandsWorldTestBase):

    options = {
        "mobsanity": False
    }

    def test_mobsanity_disabled(self) -> None:
        """Test that relevant locations and items do not exist in the pool when Mobsanity is disabled in the YAML"""
        
        # Cycle through dark forest locations
        for location in self.mobsanity_locations + self.dark_forest_mobsanity_locations:
            with self.assertRaises(KeyError, msg=f"YAML option is {self.world.options.mobsanity} but '{location}' location check exists in the pool."):
                self.world.get_location(location)

class TestPausingEnabled(StacklandsWorldTestBase):

    options = {
        "pausing": True
    }

    def test_pausing_enabled(self) -> None:
        """Test that relevant locations exist in the pool when Pausing is enabled in the YAML"""

        for location in self.pausing_locations:
            try:
                self.assertIsNotNone(self.world.get_location(location))
            except Exception:
                self.fail(f"YAML set to {self.world.options.pausing} but '{location}' does not exist in the location pool.")

class TestPausingDisabled(StacklandsWorldTestBase):

    options = {
        "pausing": False
    }

    def test_pausing_disabled(self) -> None:
        """Test that relevant locations are removed from the pool when Pausing is disabled in the YAML"""

        for location in self.pausing_locations:
            with self.assertRaises(KeyError, msg=f"YAML set to {self.world.options.pausing} but '{location}' exists in the location pool."):
                self.world.get_location(location)

class TestTrapsEnabled(StacklandsWorldTestBase):

    options = {
        "traps": True
    }

    def test_traps_enabled(self) -> None:
        """Test that relevant items are included in the item pool when enabled in the YAML"""

        # Check that at least one trap is in the pool
        traps = self.get_items_by_name(self.trap_items)
        self.assertGreater(len(traps), 0, f"YAML set to {self.world.options.traps} but no trap items found in the item pool.")

class TestTrapsDisabled(StacklandsWorldTestBase):

    options = {
        "traps": False
    }

    def test_traps_disabled(self) -> None:
        """Test that relevant items are removed from the item pool when disabled in the YAML"""

        for item in self.trap_items:
            with self.assertRaises(ValueError, msg=f"YAML set to {self.world.options.traps} but '{item}' exists in the item pool."):
                self.get_item_by_name(item)


# class TestNoMobsanityNoDarkForest(StacklandsWorldTestBase):

#     options = {
#         "dark_forest": False,
#         "mobsanity": False
#     }

#     def test_mobsanity_no_dark_forest(self) -> None:
#         """"""

    # def test_dark_forest_disabled(self) -> None:
    #     """Test that locations and items for The Dark Forest are removed when disabled in YAML"""

    #     # Cycle through dark forest locations
    #     for location in self.dark_forest_locations:
    #         with self.assertRaises(KeyError, msg=f"YAML option is {self.world.options.dark_forest} but '{location}' location check exists in the pool."):
    #             self.world.get_location(location)

    #     # Cycle through dark forest items
    #     for item in self.dark_forest_items:
    #         with self.assertRaises(ValueError, msg=f"YAML option is {self.world.options.dark_forest} but '{item}' item exists in the pool."):
    #             self.get_item_by_name(item)

    # def test_mobsanity_disabled(self) -> None:
    #     """Test that locations and items for Mobsanity are removed when disabled in YAML"""

    #     # Cycle through mobsanity locations
    #     for location in self.mainland_mobsanity_locations:
    #         with self.assertRaises(KeyError, msg=f"YAML option is {self.world.options.mobsanity} but '{location}' location check exists in the pool."):
    #             self.world.get_location(location)