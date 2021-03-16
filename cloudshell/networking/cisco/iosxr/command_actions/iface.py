from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.networking.cisco.command_actions.iface_actions import IFaceActions
from cloudshell.networking.cisco.command_templates import iface


class CiscoIOSXRIFaceActions(IFaceActions):
    def get_sub_interfaces_config(self, port_name, action_map=None, error_map=None):
        """Retrieve current interface configuration.

        :param port_name:
        :param action_map: actions will be taken during executing commands,
            i.e. handles yes/no prompts
        :param error_map: errors will be raised during executing commands,
            i.e. handles Invalid Commands errors
        :return: str
        """
        result = CommandTemplateExecutor(
            self._cli_service,
            iface.SHOW_RUNNING_SUB_INTERFACES,
            action_map=action_map,
            error_map=error_map,
            remove_prompt=True,
        ).execute_command(port_name=port_name)

        return [
            x.replace("interface ", "")
            for x in result.lower().split("\n")
            if x.strip(" ").startswith("interface")
        ]
