import numpy as np

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

from dash import Dash, html
import dash_cytoscape as cyto

# list of objects
fund_names = [('1', 'Fund A'), ('2', 'Fund B'), ('3', 'Fund C'),
              ('4', 'Fund D'), ('5', 'Fund E')]

# annual returns
r = np.array([0.01, .0005, -.0003, .005, 0.022])

# correlation matrix
rho = np.array([[1., -0.9, .2, -.1, .4],
                [-.9, 1., .3, -.9, .3],
                [.2, .3, 1., .6, .34],
                [-.1, -.9, .6, 1., .05],
                [.4, .3, .34, .05, 1.]])

# distance derived from correlation
d = np.sqrt(1. - rho)
# d = np.sqrt(1. - np.abs(rho))


X = csr_matrix(d)
Tcsr = minimum_spanning_tree(X)

nodes = list()
for i in range(len(fund_names)):
    if r[i] < 0.:
        classes = 'red'
    else:
        classes = 'green'

    if np.abs(r[i]) < 0.001:
        classes += ' snode'
    elif np.abs(r[i]) < 0.005:
        classes += ' mnode'
    else:
        classes += ' lnode'

    nodes.append({'data': {'id': fund_names[i][0],
                           'label': fund_names[i][1] + ':{:.2f}%'.format(100. * r[i])},
                  'classes': classes})

edges = list()
for i in range(len(fund_names)):
    for j in range(Tcsr.indptr[i], Tcsr.indptr[i + 1]):
        from_idx = i
        to_idx = Tcsr.indices[j]
        val = np.abs(rho[from_idx, to_idx])
        if val > 0.5:
            classes = 'strong'
        else:
            classes = 'weak'
        edges.append({'data': {'source': fund_names[from_idx][0],
                               'target': fund_names[to_idx][0]},
                      'classes': classes})

my_stylesheet = [
    # Group selectors
    {
        'selector': 'node',
        'style': {
            'content': 'data(label)'
        }
    },

    # Class selectors
    {
        'selector': '.red',
        'style': {
            'background-color': 'red',
            'line-color': 'red'
        }
    },
    {
        'selector': '.green',
        'style': {
            'background-color': 'green',
            'line-color': 'green',
        }
    },
    {
        'selector': '.snode',
        'style': {
            'width': 10,
            'height': 10,
        }
    },
    {
        'selector': '.mnode',
        'style': {
            'width': 20,
            'height': 20,
        }
    },
    {
        'selector': '.lnode',
        'style': {
            'width': 30,
            'height': 30,
        }
    },
    {
        'selector': '.strong',
        'style': {
            'width': 5,
        }
    },
    {
        'selector': '.weak',
        'style': {
            'line-style': 'dashed',
        }
    },
]

if __name__ == "__main__":
    app = Dash()

    app.layout = html.Div([
        cyto.Cytoscape(
            id='cytoscape-graph-1',
            style={'width': '100%', 'height': '500px'},
            stylesheet=my_stylesheet,
            layout={'name': 'cose'},
            elements=nodes + edges
        )
    ])

    app.run(debug=True)
