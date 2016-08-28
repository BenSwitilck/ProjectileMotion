import numpy as np
from bokeh.plotting import figure, output_file, show

G = 9.8

class Projectile:

    def __init__(self, v0, theta):

        self.v0 = v0
        theta = np.radians(theta)
        self.ct = np.cos(theta)
        self.st = np.sin(theta)
        self.tof = None
        self.h = None

    def pos(self, t):

        x = self.v0*t*self.ct
        y = self.v0*t*self.st - 0.5*G*t**2

        return (x, y)

    def vel(self, t):

        x = self.v0*t*self.ct
        y = self.v0*t*self.st - G*t

        return (x, y)

    def accel(self, t):

        return (0, -G)

    def timeOfFlight(self):

        if self.tof == None:
            self.tof = 2*self.v0*self.st/G

        return self.tof

    def height(self):

        if self.h == None:
            self.h = (self.v0**2*self.st**2)/(2*G)

        return self.h


def test():
    p = Projectile(3000, 65)
    tof = np.ceil(p.timeOfFlight())
    time = np.arange(0, tof, 0.1)
    x, y = p.pos(time)
    z = np.zeros(time.size)

    output_file('output.html')

    p = figure(title='plot', x_axis_label='time', y_axis_label='y')
    p.line(time, y)
    show(p)
