from ._anvil_designer import FiguresPanelTemplate
from anvil import *
import anvil.server
import plotly.graph_objects as go

from ... import Model


class FiguresPanel(FiguresPanelTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run when the form opens.
        self.build_tabs()

    def build_tabs(self):
        layout = Model.layout

        tabs = [self._add_button(self.tabs, tab) for tab in layout.keys()]
        sub_tab = self.build_sub_tabs(tabs[0])
        self.selected_tab = tabs[0], sub_tab

    def build_sub_tabs(self, tab):
        self.sub_tabs.clear()
        layout = Model.layout
        sub_tabs = [
            self._add_button(self.sub_tabs, sub_tab) for sub_tab in layout[tab.tag]
        ]
        return sub_tabs[0]

    def _add_button(self, element, name):
        button = Button(text=name)
        button.tag = name
        button.set_event_handler("click", self.tab_click)
        element.add_component(button)
        return button

    def calculate(self, inputs):
        self.model_solution = anvil.server.call("calculate", list(inputs.values()))
        self.build_graphs()
        self.update_warnings()

    def update_warnings(self):
        l4_status = self.model_solution["warning_l4chosen"][0][1]
        if l4_status == 0:
            self.l4_warning.icon = "fa:square-o"
        elif l4_status == 1:
            self.l4_warning.icon = "fa:check-square"
        else:
            self.l4_warning.icon = "fa:asterisk"

    def build_graphs(self):
        self.figure_container.clear()
        layout = Model.layout
        tab, sub_tab = self.selected_tab
        try:
            self._plot(layout[tab.tag][sub_tab.tag]["Top"])
            self._plot(layout[tab.tag][sub_tab.tag]["Bottom"])
        except IndexError:
            pass

    def _plot(self, graph_data):
        plot = Plot()
        self.figure_container.add_component(plot)
        title, output = graph_data
        plot.layout.title = f"{title} Graph"
        plot.layout.margin.t = 30
        plot.layout.margin.b = 20
        plot.layout.margin.l = 30
        plot.layout.margin.r = 10
        plot.layout.hovermode = "closest"
        x = self.model_solution["x"]
        plot.data = [
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                stackgroup="one",
                name=name,
                showlegend=True,
            )
            for name, y in _prepare_rows(self.model_solution[output], x)
        ]

    @property
    def selected_tab(self):
        return self._selected_tab

    @selected_tab.setter
    def selected_tab(self, tab):
        for t in self.tabs.get_components():
            t.role = "raised" if t is tab[0] else ""
        for t in self.sub_tabs.get_components():
            t.role = "raised" if t is tab[1] else ""
        self._selected_tab = tab

    def tab_click(self, **event_args):
        """This method is called when the button is clicked"""
        current_tab, current_sub_tab = self.selected_tab
        sender = event_args["sender"]
        if sender in self.tabs.get_components():
            current_tab = sender
            current_sub_tab = self.build_sub_tabs(current_tab)
        elif sender in self.sub_tabs.get_components():
            current_sub_tab = sender
        self.selected_tab = current_tab, current_sub_tab

        self.build_graphs()


def _prepare_rows(data, x):
    for row in data[::-1]:
        name = row[0]
        trace = row[1 : len(x) + 1]
        yield name, trace
