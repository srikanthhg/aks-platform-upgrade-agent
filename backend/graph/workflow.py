from langgraph.graph import END, START, StateGraph
from graph.checkpointer import checkpointer
from graph.state import AKSUpgradeState
from graph.nodes import discovery_node, validation_node, pre_report_node, validation_notification_node, approval_notification_node, approval_node, started_notification_node, upgrade_node, post_report_node, final_notification_node, stop_node, complete_node
from graph.routing import after_discovery, after_validation_notification, after_approval, after_upgrade, after_final

def build_workflow():
    graph = StateGraph(AKSUpgradeState)
    for name, node in {'discovery': discovery_node, 'validation': validation_node, 'pre_report': pre_report_node, 'validation_notice': validation_notification_node, 'approval_notice': approval_notification_node, 'approval': approval_node, 'started': started_notification_node, 'upgrade': upgrade_node, 'post_report': post_report_node, 'final_notice': final_notification_node, 'stop': stop_node, 'complete': complete_node}.items(): graph.add_node(name, node)
    graph.add_edge(START, 'discovery')
    graph.add_conditional_edges('discovery', after_discovery, {'validation':'validation','stop':'stop'})
    graph.add_edge('validation','pre_report'); graph.add_edge('pre_report','validation_notice')
    graph.add_conditional_edges('validation_notice', after_validation_notification, {'started':'started','approval_notice':'approval_notice','stop':'stop'})
    graph.add_edge('approval_notice','approval'); graph.add_conditional_edges('approval', after_approval, {'started':'started','stop':'stop'})
    graph.add_edge('started','upgrade'); graph.add_conditional_edges('upgrade', after_upgrade, {'post_report':'post_report'})
    graph.add_edge('post_report','final_notice'); graph.add_conditional_edges('final_notice', after_final, {'complete':'complete','stop':'stop'})
    graph.add_edge('complete',END); graph.add_edge('stop',END)
    return graph.compile(checkpointer=checkpointer)
aks_upgrade_graph=build_workflow()
