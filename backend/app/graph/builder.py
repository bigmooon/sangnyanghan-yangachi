"""
LangGraph StateGraph 빌더.

흐름:
  character_select → generate_event → process_choice (interrupt 발생)
  → check_state → [게임오버? run_report : generate_event (다음 턴)]
"""

from functools import lru_cache

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.graph.nodes import (
    await_next,
    character_select,
    check_state,
    generate_event,
    process_choice,
    run_report,
)
from app.graph.state import GameState


def _route_after_check(state: GameState) -> str:
    if state.get("is_game_over"):
        return "run_report"
    return "await_next"


@lru_cache
def get_game_graph():
    """컴파일된 LangGraph를 싱글턴으로 반환한다."""
    builder = StateGraph(GameState)

    builder.add_node("character_select", character_select)
    builder.add_node("generate_event", generate_event)
    builder.add_node("process_choice", process_choice)
    builder.add_node("check_state", check_state)
    builder.add_node("await_next", await_next)
    builder.add_node("run_report", run_report)

    builder.set_entry_point("character_select")
    builder.add_edge("character_select", "generate_event")
    builder.add_edge("generate_event", "process_choice")
    builder.add_edge("process_choice", "check_state")
    builder.add_conditional_edges(
        "check_state",
        _route_after_check,
        {"await_next": "await_next", "run_report": "run_report"},
    )
    builder.add_edge("await_next", "generate_event")
    builder.add_edge("run_report", END)

    return builder.compile(checkpointer=MemorySaver())
