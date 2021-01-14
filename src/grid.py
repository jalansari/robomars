from src.location import (
    Pos,
    Label
)


class Grid(object):

    def __init__(self, grid_extents: Pos):
        self.grid_extents = grid_extents
        self.labels = {}

    def __make_label_key(pos: Pos):
        return f'{pos.coord_x},{pos.coord_y}'

    def add_scent(self, pos: Pos, label: Label):
        self.labels[Grid.__make_label_key(pos)] = label

    def get_scent(self, pos: Pos):
        return self.labels.get(Grid.__make_label_key(pos))

    def is_within_grid(self, pos: Pos):
        return (
            pos.coord_x >= 0 and pos.coord_x <= self.grid_extents.coord_x and
            pos.coord_y >= 0 and pos.coord_y <= self.grid_extents.coord_y
        )
