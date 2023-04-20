from collections import OrderedDict

from cloudshell.cli.service.command_mode import CommandMode
from cloudshell.networking.cisco.cli.cisco_command_modes import (
    DefaultCommandMode,
    EnableCommandMode,
)


class CiscoIOSXRConfigCommandMode(CommandMode):
    PROMPT = r"\(config.*\)#\s*$"
    ENTER_COMMAND = "configure terminal"
    EXIT_COMMAND = "commit"

    def __init__(self, context):
        """Initialize Config command mode."""
        exit_action_map = {
            self.PROMPT: lambda session, logger: session.send_line("exit", logger)
        }
        super().__init__(
            CiscoIOSXRConfigCommandMode.PROMPT,
            CiscoIOSXRConfigCommandMode.ENTER_COMMAND,
            CiscoIOSXRConfigCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
            exit_action_map=exit_action_map,
            enter_error_map=self.enter_error_map(),
            exit_error_map=self.exit_error_map(),
        )

    def enter_action_map(self):
        return OrderedDict()

    def enter_error_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()


class CiscoIOSXRAdminCommandMode(CommandMode):
    PROMPT = r"(\(admin.*\)|sysadmin.*)#\s*$"
    ENTER_COMMAND = "admin"
    EXIT_COMMAND = "exit"

    def __init__(self, context):
        """Initialize Config command mode."""
        exit_action_map = {
            self.PROMPT: lambda session, logger: session.send_line("exit", logger)
        }
        super().__init__(
            CiscoIOSXRAdminCommandMode.PROMPT,
            CiscoIOSXRAdminCommandMode.ENTER_COMMAND,
            CiscoIOSXRAdminCommandMode.EXIT_COMMAND,
            exit_action_map=exit_action_map,
        )


CommandMode.RELATIONS_DICT = {
    DefaultCommandMode: {
        EnableCommandMode: {
            CiscoIOSXRConfigCommandMode: {},
            CiscoIOSXRAdminCommandMode: {},
        }
    }
}
