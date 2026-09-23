import unittest

from afmaths.computer_science import diagonal_pixel_length


class ComputerScienceTestMethods(unittest.TestCase):

    def test_diagonal_pixel_length(self):
        self.assertEqual(diagonal_pixel_length(1080)(1920), 2202)


if __name__ == "__main__":
    unittest.main()
