from app.text_crafter.state import State


async def default_flow(state: State) -> State:
    print("default")
