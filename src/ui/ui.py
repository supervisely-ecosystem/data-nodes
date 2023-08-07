import json
from supervisely.app.widgets import (
    Container,
    Select,
    Button,
    Flexbox,
    NodesFlow,
    Text,
)
from supervisely.app import show_dialog

from src.ui.dtl import actions_list, actions, Layer


layers_count = 0
layers = {}


select_action_name = Select(
    groups=[
        Select.Group(
            group_name,
            items=[
                Select.Item(action_name, actions[action_name].title)
                for action_name in group_actions
            ],
        )
        for group_name, group_actions in actions_list.items()
    ],
    filterable=True,
)

add_layer_btn = Button("Add Layer")

nodes_flow = NodesFlow()

get_dtl_json_btn = Button("Get DTL json")

layout = Container(
    widgets=[
        Flexbox(widgets=[select_action_name, add_layer_btn]),
        nodes_flow,
        get_dtl_json_btn,
    ]
)


def create_node(layer_id: str, layer: Layer):
    node = NodesFlow.Node(
        id=layer_id,
        name=layer.action.title,
        width=layer.action.width,
        options=layer.action.create_options(),
        inputs=layer.action.create_inputs(),
        outputs=layer.action.create_outputs(),
    )
    return node


def create_layer(action_name: str) -> Layer:
    action = actions[action_name]
    return Layer(action)


@add_layer_btn.click
def add_layer_btn_cb():
    global layers
    global layers_count
    layers_count += 1
    action_name = select_action_name.get_value()
    id = action_name + "_" + str(layers_count)
    layer = create_layer(action_name)
    layers[id] = layer
    node = create_node(id, layer)
    nodes_flow.add_node(node)


@get_dtl_json_btn.click
def get_dtl_json_btn_cb():
    nodes = nodes_flow.get_nodes_json()
    nodes_state = nodes_flow.get_nodes_state_json()
    nodes_state = json.loads(json.dumps(nodes_state, indent=4))
    for node_id, node_options in nodes_state.items():
        layer = layers[node_id]
        try:
            parsed_options = layer.action.parse_options(node_options)
            print(parsed_options)
            print(json.dumps(parsed_options, indent=4))
        except Exception as e:
            show_dialog(
                title="Error parsing settings",
                description=f"Layer: {layer.action.title}. Error: {type(e).__name__}: {str(e)}",
                status="error",
            )
            return
