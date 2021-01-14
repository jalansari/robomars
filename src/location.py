class Pos(object):

    def __init__(self, coord_x, coord_y):
        self.coord_x = coord_x
        self.coord_y = coord_y


class Orientation(object):
    FACING_NORTH = ('N', 0)
    FACING_EAST = ('E', 1)
    FACING_SOUTH = ('S', 2)
    FACING_WEST = ('W', 3)

    FacingMap_CharKeys = {
        FACING_NORTH[0]: FACING_NORTH[1],
        FACING_EAST[0]: FACING_EAST[1],
        FACING_SOUTH[0]: FACING_SOUTH[1],
        FACING_WEST[0]: FACING_WEST[1]
    }
    FacingMap_NumKeys = {
        FACING_NORTH[1]: FACING_NORTH[0],
        FACING_EAST[1]: FACING_EAST[0],
        FACING_SOUTH[1]: FACING_SOUTH[0],
        FACING_WEST[1]: FACING_WEST[0]
    }

    def __init__(self, facing_char):
        self.facing = Orientation.FacingMap_CharKeys.get(facing_char)

    def get_orientation(self):
        return Orientation.FacingMap_NumKeys.get(self.facing)

    def get_orientation_int(self):
        return self.facing

    def new_orientation_90_clockwise(self):
        return Orientation(Orientation.FacingMap_NumKeys.get((self.facing+1) % 4))

    def new_orientation_90_anticlockwise(self):
        return Orientation(Orientation.FacingMap_NumKeys.get((self.facing-1) % 4))

    def next_forward_position(self, current_pos: Pos):
        next_pos_x = current_pos.coord_x
        next_pos_y = current_pos.coord_y
        if self.facing == Orientation.FACING_NORTH[1]:
            next_pos_y = current_pos.coord_y + 1
        elif self.facing == Orientation.FACING_SOUTH[1]:
            next_pos_y = current_pos.coord_y - 1
        elif self.facing == Orientation.FACING_EAST[1]:
            next_pos_x = current_pos.coord_x + 1
        elif self.facing == Orientation.FACING_WEST[1]:
            next_pos_x = current_pos.coord_x - 1
        return Pos(next_pos_x, next_pos_y)

    def __str__(self):
        return Orientation.FacingMap_NumKeys.get(self.facing)


class Label(object):

    def __init__(self, orientation: Orientation, is_scent_at_edge=True):
        self.is_scent_at_edge = is_scent_at_edge
        self.orientation = orientation

    def is_next_drop(self, orientation: Orientation):
        return (
            self.orientation.get_orientation_int() == orientation.get_orientation_int() and
            self.is_scent_at_edge
        )
