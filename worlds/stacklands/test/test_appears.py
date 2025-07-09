from . import StacklandsTestBase

class TestThisAppears(StacklandsTestBase):

    def test_appears(self) -> None:
        """Testing that this test even appears"""
        
        self.assertIs(True, True, "Nice, good job")