from app.game.engine import next_event, play_turn, use_item

# api/game.py에서 사용하는 별칭
select_event = next_event
process_choice = play_turn

__all__ = ["next_event", "play_turn", "process_choice", "select_event", "use_item"]
