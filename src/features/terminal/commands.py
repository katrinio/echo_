from dataclasses import dataclass


@dataclass(frozen=True)
class CommandHelp:
    name: str
    description: str
    example: str | None = None


COMMANDS = [
    CommandHelp(
        name="help",
        description="Show available commands",
        example="help",
    ),
    CommandHelp(
        name="new",
        description="Create a new milestone",
        example="new",
    ),
    CommandHelp(
        name="tags",
        description="List tags",
        example="tags",
    ),
    CommandHelp(
        name="tag {TAG_NAME}",
        description="Milestones by Tag",
        example="tag TRAVEL",
    ),
    CommandHelp(
        name="random",
        description="Random milestone",
        example="random",
    ),
]