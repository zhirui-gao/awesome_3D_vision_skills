
import random

import numpy as np
from scipy.special import binom
import matplotlib.pyplot as plt
import cv2

bernstein = lambda n, k, t: binom(n, k) * t ** k * (1. - t) ** (n - k)


def bezier(points, num=200):
    N = len(points)
    t = np.linspace(0, 1, num=num)
    curve = np.zeros((num, 2))
    for i in range(N):
        curve += np.outer(bernstein(N - 1, i, t), points[i])
    return curve

class Segment():
    def __init__(self, p1, p2, angle1, angle2, **kw):
        self.p1 = p1
        self.p2 = p2
        self.angle1 = angle1
        self.angle2 = angle2
        self.numpoints = kw.get("numpoints", 200)
        r = kw.get("r", 0.3)
        d = np.sqrt(np.sum((self.p2 - self.p1) ** 2))
        self.r = r * d
        self.p = np.zeros((4, 2))
        self.p[0, :] = self.p1[:]
        self.p[3, :] = self.p2[:]
        self.calc_intermediate_points(self.r)

    def calc_intermediate_points(self, r):
        self.p[1, :] = self.p1 + np.array([self.r * np.cos(self.angle1),
                                           self.r * np.sin(self.angle1)])
        self.p[2, :] = self.p2 + np.array([self.r * np.cos(self.angle2 + np.pi),
                                           self.r * np.sin(self.angle2 + np.pi)])
        self.curve = bezier(self.p, self.numpoints)

class Curves():
    def __init__(self, n):
        np.random.seed(10)
        self.rad = 0.2
        self.edgy = np.random.rand()
        self.n = n

    def get_point(self,min_x, max_x, min_y, max_y):
        a = self.get_random_points(n=self.n, scale=1)
        x, y, _ = self.get_bezier_curve(a, rad=self.rad, edgy=self.edgy)
        x = x * (max_x-min_x) + min_x
        y = y * (max_y-min_y) + min_y
        points = np.array(np.concatenate((x.reshape(-1,1), y.reshape(-1,1)), axis=1)) # N,2
        return points


    def get_curve(self, points, **kw):
        segments = []
        for i in range(len(points) - 1):
            seg = Segment(points[i, :2], points[i + 1, :2], points[i, 2], points[i + 1, 2], **kw)
            segments.append(seg)
        curve = np.concatenate([s.curve for s in segments])
        return segments, curve

    def ccw_sort(self, p):
        d = p - np.mean(p, axis=0)
        s = np.arctan2(d[:, 0], d[:, 1])
        return p[np.argsort(s), :]

    def get_bezier_curve(self,a, rad=0.2, edgy=0):
        """ given an array of points *a*, create a curve through
        those points.
        *rad* is a number between 0 and 1 to steer the distance of
              control points.
        *edgy* is a parameter which controls how "edgy" the curve is,
               edgy=0 is smoothest."""
        p = np.arctan(edgy) / np.pi + .5
        a = self.ccw_sort(a)
        a = np.append(a, np.atleast_2d(a[0, :]), axis=0)
        d = np.diff(a, axis=0)
        ang = np.arctan2(d[:, 1], d[:, 0])
        f = lambda ang: (ang >= 0) * ang + (ang < 0) * (ang + 2 * np.pi)
        ang = f(ang)
        ang1 = ang
        ang2 = np.roll(ang, 1)
        ang = p * ang1 + (1 - p) * ang2 + (np.abs(ang2 - ang1) > np.pi) * np.pi
        ang = np.append(ang, [ang[0]])
        a = np.append(a, np.atleast_2d(ang).T, axis=1)
        s, c = self.get_curve(a, r=rad, method="var")
        x, y = c.T
        return x, y, a

    def get_random_points(self, n=5, scale=0.8, mindst=None, rec=0):
        """ create n random points in the unit square, which are *mindst*
        apart, then scale them."""
        mindst = mindst or .7 / n
        a = np.random.rand(n, 2)
        d = np.sqrt(np.sum(np.diff(self.ccw_sort(a), axis=0), axis=1) ** 2)
        if np.all(d >= mindst) or rec >= 200:
            return a * scale
        else:
            return self.get_random_points(n=n, scale=scale, mindst=mindst, rec=rec + 1)

    def draw_plot(self,x, y):
        img = np.zeros((480, 640), np.uint8)
        for i in range(len(x) - 1):
            cv2.line(img, (int(x[i]), int(y[i])), (int(x[i + 1]), int(y[i + 1])), 255, 1, 8)
        cv2.imwrite('1.png', img)


""" Module used to generate geometrical synthetic shapes """
import os.path
import random

import cv2
import cv2 as cv
import numpy as np
import math

random_state = np.random.RandomState(None)


def set_random_state(state):
    global random_state
    random_state = state


def get_random_color(background_color):
    """ Output a random scalar in grayscale with a least a small
        contrast with the background color """
    color = random_state.randint(256)
    if abs(color - background_color) < 40:  # not enough contrast
        color = (color + 128) % 256
    return color


def get_different_color(previous_colors, min_dist=50, max_count=20):
    """ Output a color that contrasts with the previous colors
    Parameters:
      previous_colors: np.array of the previous colors
      min_dist: the difference between the new color and
                the previous colors must be at least min_dist
      max_count: maximal number of iterations
    """
    color = random_state.randint(256)
    count = 0
    while np.any(np.abs(previous_colors - color) < min_dist) and count < max_count:
        count += 1
        color = random_state.randint(256)
    return color


def add_salt_and_pepper(img):
    """ Add salt and pepper noise to an image """
    noise = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
    cv.randu(noise, 0, 255)
    black = noise < 30
    white = noise > 225
    img[white > 0] = 255
    img[black > 0] = 0
    cv.blur(img, (5, 5), img)
    return np.empty((0, 2), dtype=np.int)


def generate_background_steel(background_path='/home/gzr/Data/generative_steel/train', size=(960, 1280), max_id=10000):
    img_id = random.randint(0, max_id - 1)
    img_path = os.path.join(background_path, '%05d' % img_id + '.jpg')
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, dsize=(2400, 640))
    crop_rand_0 = random.randint(0, img.shape[0] - size[0])
    crop_rand_1 = random.randint(0, img.shape[1] - size[1])
    return img[crop_rand_0:crop_rand_0 + size[0], crop_rand_1:crop_rand_1 + size[1]]


def generate_background(size=(960, 1280), nb_blobs=100, min_rad_ratio=0.01,
                        max_rad_ratio=0.05, min_kernel_size=50, max_kernel_size=300):
    """ Generate a customized background image
    Parameters:
      size: size of the image
      nb_blobs: number of circles to draw
      min_rad_ratio: the radius of blobs is at least min_rad_size * max(size)
      max_rad_ratio: the radius of blobs is at most max_rad_size * max(size)
      min_kernel_size: minimal size of the kernel
      max_kernel_size: maximal size of the kernel
    """
    img = np.zeros(size, dtype=np.uint8)
    dim = max(size)
    cv.randu(img, 0, 255)
    cv.threshold(img, random_state.randint(256), 255, cv.THRESH_BINARY, img)
    background_color = int(np.mean(img))
    blobs = np.concatenate([random_state.randint(0, size[1], size=(nb_blobs, 1)),
                            random_state.randint(0, size[0], size=(nb_blobs, 1))],
                           axis=1)
    for i in range(nb_blobs):
        col = get_random_color(background_color)
        cv.circle(img, (blobs[i][0], blobs[i][1]),
                  np.random.randint(int(dim * min_rad_ratio),
                                    int(dim * max_rad_ratio)),
                  col, -1)
    kernel_size = random_state.randint(min_kernel_size, max_kernel_size)
    cv.blur(img, (kernel_size, kernel_size), img)
    return img


def generate_custom_background(size, background_color, nb_blobs=3000,
                               kernel_boundaries=(50, 100)):
    """ Generate a customized background to fill the shapes
    Parameters:
      background_color: average color of the background image
      nb_blobs: number of circles to draw
      kernel_boundaries: interval of the possible sizes of the kernel
    """
    img = np.zeros(size, dtype=np.uint8)
    img = img + get_random_color(background_color)
    blobs = np.concatenate([np.random.randint(0, size[1], size=(nb_blobs, 1)),
                            np.random.randint(0, size[0], size=(nb_blobs, 1))],
                           axis=1)
    for i in range(nb_blobs):
        col = get_random_color(background_color)
        cv.circle(img, (blobs[i][0], blobs[i][1]),
                  np.random.randint(20), col, -1)
    kernel_size = np.random.randint(kernel_boundaries[0], kernel_boundaries[1])
    cv.blur(img, (kernel_size, kernel_size), img)
    return img


def final_blur(img, kernel_size=(5, 5)):
    """ Apply a final Gaussian blur to the image
    Parameters:
      kernel_size: size of the kernel
    """
    cv.GaussianBlur(img, kernel_size, 0, img)


def ccw(A, B, C, dim):
    """ Check if the points are listed in counter-clockwise order """
    if dim == 2:  # only 2 dimensions
        return ((C[:, 1] - A[:, 1]) * (B[:, 0] - A[:, 0])
                > (B[:, 1] - A[:, 1]) * (C[:, 0] - A[:, 0]))
    else:  # dim should be equal to 3
        return ((C[:, 1, :] - A[:, 1, :])
                * (B[:, 0, :] - A[:, 0, :])
                > (B[:, 1, :] - A[:, 1, :])
                * (C[:, 0, :] - A[:, 0, :]))


def intersect(A, B, C, D, dim):
    """ Return true if line segments AB and CD intersect """
    return np.any((ccw(A, C, D, dim) != ccw(B, C, D, dim)) &
                  (ccw(A, B, C, dim) != ccw(A, B, D, dim)))


def keep_points_inside(points, size):
    """ Keep only the points whose coordinates are inside the dimensions of
    the image of size 'size' """
    mask = (points[:, 0] >= 0) & (points[:, 0] < size[1]) & \
           (points[:, 1] >= 0) & (points[:, 1] < size[0])
    return points[mask, :]


def cal_trans_point(M, point):
    x = round(M[0][0] * point[0][0] + M[0, 1] * point[0][1] + M[0, 2])
    y = round(M[1][0] * point[0][0] + M[1, 1] * point[0][1] + M[1, 2])
    return np.array([[x, y]])


def check_both_out_of_image(p1, p2, h, w):
    flag1, flag2 = True, True
    if p1[0][0] >= 0 and p1[0][0] < w and p1[0][1] >= 0 and p1[0][1] < h:
        flag1 = False
    if p2[0][0] >= 0 and p2[0][0] < w and p2[0][1] >= 0 and p2[0][1] < h:
        flag2 = False
    return flag1 * flag2


def check_out_image(p1, h, w):
    flag1 = True
    if p1[0][0] >= 0 and p1[0][0] < w and p1[0][1] >= 0 and p1[0][1] < h:
        flag1 = False
    return flag1


def draw_lines(img, nb_lines=10):
    """ Draw random lines and output the positions of the endpoints
    Parameters:
      nb_lines: maximal number of lines
    """
    num_lines = random_state.randint(1, nb_lines)
    segments = np.empty((0, 4), dtype=np.int)
    points = np.empty((0, 2), dtype=np.int)
    template_points = np.empty((0, 2), dtype=np.int)
    background_color = int(np.mean(img))
    min_dim = min(img.shape)
    ## template
    template_img = np.zeros_like(img)
    # generate a random transfmation matrix
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    angle = random_state.randint(-45, 45)
    scale = 1
    translate = [random_state.randint(img.shape[1]) / 4, random_state.randint(img.shape[0]) / 4]  # x,y
    M = cv2.getRotationMatrix2D(center, angle, scale)
    row_add = np.array([0, 0, 1])
    M = np.r_[M, [row_add]]
    M[0, 2] += translate[0]
    M[1, 2] += translate[1]

    for i in range(num_lines):
        x1 = random_state.randint(img.shape[1])
        y1 = random_state.randint(img.shape[0])
        p1 = np.array([[x1, y1]])
        x2 = random_state.randint(img.shape[1])
        y2 = random_state.randint(img.shape[0])
        p2 = np.array([[x2, y2]])
        # Check that there is no overlap
        if intersect(segments[:, 0:2], segments[:, 2:4], p1, p2, 2):
            continue
        p1_new = cal_trans_point(M, p1)
        p2_new = cal_trans_point(M, p2)

        if check_both_out_of_image(p1_new, p2_new, h, w):
            return None, None, None, None

        segments = np.concatenate([segments, np.array([[x1, y1, x2, y2]])], axis=0)
        col = get_random_color(background_color)
        thickness = random_state.randint(1, 2)
        cv.line(img, (x1, y1), (x2, y2), col, thickness)
        cv.line(template_img, (p1_new[0][0], p1_new[0][1]), (p2_new[0][0], p2_new[0][1]), 255, 1)
        points = np.concatenate([points, np.array([[x1, y1], [x2, y2]])], axis=0)
        template_points = np.concatenate(
            [template_points, np.array([[p1_new[0][0], p1_new[0][1]], [p2_new[0][0], p2_new[0][1]]])], axis=0)
    return points, template_points, template_img, np.linalg.inv(M)


def draw_polygon(img, max_sides=15):
    """ Draw a polygon with a random number of corners
    and return the corner points
    Parameters:
      max_sides: maximal number of sides + 1
    """
    # num_corners = random_state.randint(3, max_sides)
    num_corners = max_sides
    min_dim = min(img.shape[0], img.shape[1])
    rad = max(random_state.rand() * min_dim / 2, min_dim / 3)
    x = random_state.randint(rad, img.shape[1] - rad)  # Center of a circle
    y = random_state.randint(rad, img.shape[0] - rad)

    # Sample num_corners points inside the circle
    slices = np.linspace(0, 2 * math.pi, num_corners + 1)
    angles = [slices[i] + random_state.rand() * (slices[i + 1] - slices[i])
              for i in range(num_corners)]
    points = np.array([[int(x + (random_state.rand() * 0.5 + 0.5) * rad * math.cos(a)),
                        int(y + (random_state.rand() * 0.5 + 0.5) * rad * math.sin(a))]
                       for a in angles])

    # Filter the points that are too close or that have an angle too flat
    norms = [np.linalg.norm(points[(i - 1) % num_corners, :]
                            - points[i, :]) for i in range(num_corners)]
    mask = np.array(norms) > 0.01
    points = points[mask, :]
    num_corners = points.shape[0]
    corner_angles = [angle_between_vectors(points[(i - 1) % num_corners, :] -
                                           points[i, :],
                                           points[(i + 1) % num_corners, :] -
                                           points[i, :])
                     for i in range(num_corners)]
    mask = np.array(corner_angles) < (2 * math.pi / 3)
    points = points[mask, :]
    num_corners = points.shape[0]

    ## template
    template_img = np.zeros_like(img, np.uint8)
    # generate a random transfmation matrix
    h, w = img.shape[:2]
    center = (x, y)
    angle = random_state.randint(-45, 45)
    scale = 1
    translate = [w / 2 - x, h / 2 - y]  # x,y
    M = cv2.getRotationMatrix2D(center, angle, scale)
    row_add = np.array([0, 0, 1])
    M = np.r_[M, [row_add]]
    M[0, 2] += translate[0]
    M[1, 2] += translate[1]
    ## template

    if num_corners < 3:  # not enough corners
        return draw_polygon(img, max_sides)

    corners = points.reshape((-1, 1, 2))
    col = get_random_color(int(np.mean(img)))
    cv.fillPoly(img, [corners], col)

    ## template
    corners_templete = []
    for point in corners:
        point_new = cal_trans_point(M, point)
        if check_out_image(point_new, h, w):
            return None, None, None, None
        corners_templete.append(point_new)

    cv.fillPoly(template_img, [np.array(corners_templete)], 255)

    return template_img


def draw_contours(img, max_n=20):
    """ Draw a polygon with a random number of corners
    and return the corner points
    Parameters:
      max_sides: maximal number of sides + 1
    """
    num_corners = max_n
    # big

    curves = Curves(n=num_corners)
    boundary = 50
    points = curves.get_point(min_x=boundary, max_x=img.shape[1] - boundary, min_y=boundary,
                              max_y=img.shape[0] - boundary)

    x, y = np.mean(points, axis=0)  # # Center of a conture
    corners = points.reshape(-1, 1, 2).astype(int)
    cv.fillPoly(img, [corners], 255)

    ## template
    template_img = np.zeros_like(img,np.uint8)
    # generate a random transfmation matrix
    h, w = img.shape[:2]
    center = (x, y)
    angle = random_state.randint(-45, 45)
    scale = 1
    translate = [w / 2 - x, h / 2 - y]  # x,y
    M = cv2.getRotationMatrix2D(center, angle, scale)
    row_add = np.array([0, 0, 1])
    M = np.r_[M, [row_add]]
    M[0, 2] += translate[0]
    M[1, 2] += translate[1]
    ## template

    corners_templete = []

    for point in corners:
        point_new = cal_trans_point(M, point)
        if check_out_image(point_new, h, w):
            return None, None, None, None
        corners_templete.append(point_new)

    cv.fillPoly(template_img, [np.array(corners_templete)], 255)
    return template_img


def overlap(center, rad, centers, rads):
    """ Check that the circle with (center, rad)
    doesn't overlap with the other circles """
    flag = False
    for i in range(len(rads)):
        if np.linalg.norm(center - centers[i]) + min(rad, rads[i]) < max(rad, rads[i]):
            flag = True
            break
    return flag


def angle_between_vectors(v1, v2):
    """ Compute the angle (in rad) between the two vectors v1 and v2. """
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def draw_multiple_polygons(img, max_sides=8, nb_polygons=30, **extra):
    """ Draw multiple polygons with a random number of corners
    and return the corner points
    Parameters:
      max_sides: maximal number of sides + 1
      nb_polygons: maximal number of polygons
    """
    segments = np.empty((0, 4), dtype=np.uint8)
    centers = []
    rads = []
    points = np.empty((0, 2), dtype=np.uint8)
    background_color = int(np.mean(img))
    for i in range(nb_polygons):
        num_corners = random_state.randint(3, max_sides)
        min_dim = min(img.shape[0], img.shape[1])
        rad = max(random_state.rand() * min_dim / 2, min_dim / 10)
        x = random_state.randint(rad, img.shape[1] - rad)  # Center of a circle
        y = random_state.randint(rad, img.shape[0] - rad)

        # Sample num_corners points inside the circle
        slices = np.linspace(0, 2 * math.pi, num_corners + 1)
        angles = [slices[i] + random_state.rand() * (slices[i + 1] - slices[i])
                  for i in range(num_corners)]
        new_points = [[int(x + max(random_state.rand(), 0.4) * rad * math.cos(a)),
                       int(y + max(random_state.rand(), 0.4) * rad * math.sin(a))]
                      for a in angles]
        new_points = np.array(new_points)

        # Filter the points that are too close or that have an angle too flat
        norms = [np.linalg.norm(new_points[(i - 1) % num_corners, :]
                                - new_points[i, :]) for i in range(num_corners)]
        mask = np.array(norms) > 0.01
        new_points = new_points[mask, :]
        num_corners = new_points.shape[0]
        corner_angles = [angle_between_vectors(new_points[(i - 1) % num_corners, :] -
                                               new_points[i, :],
                                               new_points[(i + 1) % num_corners, :] -
                                               new_points[i, :])
                         for i in range(num_corners)]
        mask = np.array(corner_angles) < (2 * math.pi / 3)
        new_points = new_points[mask, :]
        num_corners = new_points.shape[0]
        if num_corners < 3:  # not enough corners
            continue

        new_segments = np.zeros((1, 4, num_corners))
        new_segments[:, 0, :] = [new_points[i][0] for i in range(num_corners)]
        new_segments[:, 1, :] = [new_points[i][1] for i in range(num_corners)]
        new_segments[:, 2, :] = [new_points[(i + 1) % num_corners][0]
                                 for i in range(num_corners)]
        new_segments[:, 3, :] = [new_points[(i + 1) % num_corners][1]
                                 for i in range(num_corners)]

        # Check that the polygon will not overlap with pre-existing shapes
        if intersect(segments[:, 0:2, None],
                     segments[:, 2:4, None],
                     new_segments[:, 0:2, :],
                     new_segments[:, 2:4, :],
                     3) or overlap(np.array([x, y]), rad, centers, rads):
            continue
        centers.append(np.array([x, y]))
        rads.append(rad)
        new_segments = np.reshape(np.swapaxes(new_segments, 0, 2), (-1, 4))
        segments = np.concatenate([segments, new_segments], axis=0)

        # Color the polygon with a custom background
        corners = new_points.reshape((-1, 1, 2))
        mask = np.zeros(img.shape, np.uint8)
        custom_background = np.zeros(img.shape, np.uint8)+255
        cv.fillPoly(mask, [corners], 255)
        locs = np.where(mask != 0)
        img[locs[0], locs[1]] = custom_background[locs[0], locs[1]]
    return img


def draw_ellipses(img, nb_ellipses=40):
    """ Draw several ellipses
    Parameters:
      nb_ellipses: maximal number of ellipses
    """
    centers = np.empty((0, 2), dtype=np.uint8)
    rads = np.empty((0, 1), dtype=np.uint8)
    min_dim = min(img.shape[0], img.shape[1]) / 2
    background_color = int(np.mean(img))
    ax_0, ay_0 = -100, -100
    for i in range(nb_ellipses):
        ax = int(max(random_state.rand() * min_dim, min_dim / 4))
        ay = int(max(random_state.rand() * min_dim, min_dim / 4))
        if max(ax, ay) / min(ax, ay) < 0.2:
            continue

        # control similar ellipses
        if (abs(ax - ax_0) / ax < 0.1 and abs(ay - ay_0) / ax < 0.1) or (
                abs(ay - ax_0) / ax < 0.1 and abs(ax - ay_0) / ax < 0.1):
            continue
        if (abs(ax - ax_0) < 10 and abs(ay - ay_0) < 10) or (
                abs(ay - ax_0) < 10 and abs(ax - ay_0) < 10):
            continue

        max_rad = max(ax, ay)
        x = random_state.randint(max_rad, img.shape[1] - max_rad)  # center
        y = random_state.randint(max_rad, img.shape[0] - max_rad)
        new_center = np.array([[x, y]])

        # Check that the ellipsis will not overlap with pre-existing shapes
        diff = centers - new_center
        if np.any(max_rad > (np.sqrt(np.sum(diff * diff, axis=1)) - rads)):
            continue
        centers = np.concatenate([centers, new_center], axis=0)
        rads = np.concatenate([rads, np.array([[max_rad]])], axis=0)

        col = get_random_color(background_color)
        angle = random_state.rand() * 45
        cv.ellipse(img, (x, y), (ax, ay), angle, 0, 360, col, -1)
        if ax_0 == -100:
            ax_0 = ax
            ay_0 = ay
            ## template
            template_img = np.zeros_like(img,np.uint8)
            # generate a random transfmation matrix
            h, w = img.shape[:2]
            center = (x, y)
            angle_M = random_state.randint(-45, 45)
            scale = 1
            translate = [w / 2 - x, h / 2 - y]  # x,y
            M = cv2.getRotationMatrix2D(center, angle_M, scale)  # counter-clockwise
            row_add = np.array([0, 0, 1])
            M = np.r_[M, [row_add]]
            M[0, 2] += translate[0]
            M[1, 2] += translate[1]

            ## template
            template_center = cal_trans_point(M, new_center)
            cv.ellipse(template_img, (template_center[0][0], template_center[0][1]), (ax, ay), angle - angle_M, 0, 360,
                       255, -1)  # clock-wise

    return template_img






img = np.zeros((480, 640), np.uint8)


# contures
# img = draw_contours(img, 10)
# img = draw_multiple_polygons(img)
# img = draw_ellipses(img)
img = draw_polygon(img,10)
cv2.imshow('img', img)
cv2.waitKey(2000)

