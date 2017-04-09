import itertools
from math import sin, cos, pi

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.utils import get_color_from_hex as rgb
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App

from stock.gui.graph import SmoothLinePlot, Graph

Builder.load_string('''
<StockSticker>:
    orientation:"vertical"
    size_hint:(None,None)
    size:(800,200)
    BoxLayout:
        orientation:"horizontal"
        size_hint:(1,.1)
        Label:
            id: Title
            text: 'Volume'
            size_hint:(.25,1)
        Label:
            id: Stock
            text: 'Stock'
            size_hint:(.25,1)
        Label:
            id: Volume
            text: 'Volume'
            size_hint:(.5,1)
    BoxLayout:
        orientation:"horizontal"
        Graph:
            size_hint:(.75,1)
            id: Left
            y_grid_label:True
            x_grid_label:True
            padding:5
            xlog:False
            ylog:False
            x_grid:True
            y_grid:True
            xmin:-50
            xmax:5000
            ymin:-1
            ymax:1
        Graph:
            size_hint:(.25,1)
            id: Right
            y_grid_label:True
            x_grid_label:True
            padding:5
            xlog:False
            ylog:False
            x_grid:True
            y_grid:True
            xmin:-50
            xmax:50
            ymin:-1
            ymax:1
''')


class StockSticker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        colors = itertools.cycle([
            rgb('7dac9f'), rgb('dc7062'), rgb('66a8d4'), rgb('e5b060')])
        graph_theme = {
            'label_options': {
                'color': rgb('444444'),  # color of tick labels and titles
                'bold': True},
            'background_color': rgb('f8f8f2'),  # back ground color of canvas
            'tick_color': rgb('808080'),  # ticks and grid
            'border_color': rgb('808080')}  # border drawn around each graph

        self.left_plot = SmoothLinePlot(color=next(colors))
        self.left_plot.points = [(x, sin(x / 5.)) for x in range(-50, 51)]
        # for efficiency, the x range matches xmin, xmax
        self.ids['Left'].add_plot(self.left_plot)

        self.left_graph = self.ids['Left']

        Clock.schedule_interval(self.update_points, 1 / 60.)

        self.right_plot = SmoothLinePlot(color=next(colors))
        self.right_plot.points = [(x, sin(x / 5.)) for x in range(-50, 51)]
        # for efficiency, the x range matches xmin, xmax
        self.ids['Right'].add_plot(self.right_plot)

        self.right_graph = self.ids['Right']

    def update_points(self, *args):
        self.left_plot.points = [(x, 3 * cos(Clock.get_time() + x / 5.)) for x in range(-50, 51)]
        self.left_graph.ymax = max(max(i[1] for i in self.left_plot.points), self.left_graph.ymax)
        self.left_graph.ymin = min(min(i[1] for i in self.left_plot.points), self.left_graph.ymin)

        self.right_plot.points = [(x, 3 * sin(Clock.get_time() + x / 5.)) for x in range(-50, 51)]
        self.right_graph.ymax = max(max(i[1] for i in self.right_plot.points), self.right_graph.ymax)
        self.right_graph.ymin = min(min(i[1] for i in self.right_plot.points), self.right_graph.ymin)


class TestApp(App):
    def build(self):
        b = StockSticker(spacing=10)
        return b


if __name__ == '__main__':
    TestApp().run()
