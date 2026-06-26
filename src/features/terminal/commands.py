from dataclasses import dataclass


@dataclass(frozen=True)
class CommandHelp:
    name: str
    description: str
    example: str | None = None
    command: str | None = None

    @property
    def autocomplete_value(self) -> str:
        return self.command or self.name.split()[0]


COMMANDS = [
    CommandHelp(
        name="logout",
        description="Logging out",
        example="logout",
    ),
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
        name="tag {tag_name}",
        description="Milestones by tag",
        example="tag TRAVEL",
        command="tag",
    ),
    CommandHelp(
        name="random",
        description="Random milestone",
        example="random",
    ),
]