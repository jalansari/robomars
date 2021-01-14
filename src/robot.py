from src.location import (
    Pos,
    Orientation
)


class Robot(object):

    def __init__(self):
        self.__position: Pos = None
        self.__orientation: Orientation = None
        self.__is_lost = False

    def set_position(self, new_position: Pos):
        self.__position = new_position

    def set_orientation(self, new_orientation: Orientation):
        self.__orientation = new_orientation

    def set_state(self, new_position: Pos, new_orientation: Orientation):
        self.set_position(new_position)
        self.set_orientation(new_orientation)

    def is_now_lost(self):
        self.__is_lost = True

    @property
    def is_lost(self):
        return self.__is_lost

    @property
    def position(self):
        return self.__position

    @property
    def orientation(self):
        return self.__orientation

    def __str__(self):
        return (
            f'{self.position.coord_x} {self.position.coord_y} {self.orientation}' +
            f'{" LOST" if self.is_lost else ""}'
        )
