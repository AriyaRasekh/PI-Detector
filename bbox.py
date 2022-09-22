from random import randrange


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

        if len(Bbox.all) == 0:

            return False

        for box in Bbox.all:

            # If one rectangle is on left side of other
            if l[0] > box.r_x or box.l_x > r[0]:
                continue
            # If one rectangle is above other
            elif l[1] > box.r_y or box.l_y > r[1]:
                continue

            else:
                return True

        return False

    @staticmethod
    def random_bbox_location(image, text_box):
        """return bbox coordinate which text box fits in the image"""
        text_x = randrange(image.shape[1] - text_box.shape[1])
        text_y = randrange(image.shape[0] - text_box.shape[0])
        l = (text_x, text_y)
        r = (text_x + text_box.shape[1], text_y + text_box.shape[0])
        return l, r

    def __repr__(self):
        print(f"self.l_x: {self.l_x}, self.l_y: {self.l_y}, self.r_x: {self.r_x}, self.r_y: {self.r_y}")
