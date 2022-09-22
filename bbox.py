class Bbox:
    all = []

    #   l ----------------------
    #   |                      |
    #   |                      |
    #   |_____________________ r

    def __init__(self, l_x, l_y, r_x, r_y):

        self.l_x, self.l_y, self.r_x, self.r_y = l_x, l_y, r_x, r_y

        Bbox.all.append(self)

    @staticmethod
    def do_overlap(l, r):
        """
        :param l: x and y coordinates of l as (x, y)
        :param r: x and y coordinates of r as (x, y)
        :return: true if there is an overlap, false otherwise
        """

        for box in Bbox.all:

            # # if rectangle has area 0, no overlap
            # if l[0] == r[0] or l[1] == r[1] or box.r_x == box.l_x or box.l_y == box.r_y:
            #     return False

            # If one rectangle is on left side of other
            if l[0] > box.r_x or box.l_x > r[0]:
                return False

            # If one rectangle is above other
            if r[1] > box.l_y or box.r_y > l[1]:
                return False

        return True
