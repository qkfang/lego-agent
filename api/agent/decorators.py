from model import Agent, Function, FunctionParameter
from functools import partial
from prompty.utils import get_json_type
from typing import Any, Callable, Union, get_type_hints


function_agents: dict[str, Agent] = {}
function_calls: dict[str, Function] = {}


def agent(func: Union[Callable, None] = None, **kwargs: Any) -> Callable:
    global function_agents

    if func is None:
        return partial(agent, **kwargs)

    if "description" not in kwargs:
        raise ValueError("description is required for agent decorator")

    if "name" not in kwargs:
        raise ValueError("name is required for agent decorator")

    name = kwargs.pop("name")
    description = kwargs.pop("description")
    args = get_type_hints(func, include_extras=True)

    # remove the return and notify arguments from the args dictionary
    args.pop("return", None)
    args.pop("notify", None)
    if "kind" in args:
        # remove kind from args if it exists
        args.pop("image", None)

    if func.__name__ not in function_agents:
        function_agents[func.__name__] = Agent(
            id=func.__name__,
            name=func.__name__,
            type="function_agent",
            description=" ".join(description.split()),
            parameters=[
                {
                    "name": k,
                    "type": get_json_type(v.__args__[0]),
                    "description": (
                        v.__metadata__[0]
                        if hasattr(v, "__metadata__")
                        else "No Description"
                    ),
                    "required": True,
                }
                for k, v in args.items()
            ],
        )

    return func


def function(func: Union[Callable, None] = None, **kwargs: Any) -> Callable:
    global function_calls

    if func is None:
        return partial(function, **kwargs)

    args = get_type_hints(func, include_extras=True)

    # remove the return and notify arguments from the args dictionary
    args.pop("return", None)
    args.pop("notify", None)

    if func.__name__ not in function_calls:
        function_calls[func.__name__] = Function(
            name=func.__name__,
            parameters=[
                FunctionParameter(
                    name=k,
                    type=get_json_type(v),
                )
                for k, v in args.items()
            ],
            func=func,
        )

    return func
