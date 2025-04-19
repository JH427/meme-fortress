# agent_logic.py

def interpret_task(command: str, trait: str) -> str:
    chaos_map = {
        "literal": f"Executing: {command}",
        "chaotic": f"Built a meme shrine instead of '{command}'",
        "doomer": f"'{command}' is pointless. Everything decays.",
        "clout chaser": f"Streaming '{command}' live for likes"
    }
    return chaos_map.get(trait, f"Misinterpreted '{command}' creatively")
