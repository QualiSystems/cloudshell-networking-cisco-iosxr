from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.networking.cisco.command_actions.add_remove_vlan_actions import (
    AddRemoveVlanActions,
)
from cloudshell.networking.cisco.command_templates import (
    add_remove_vlan as vlan_command_template,
)
from cloudshell.networking.cisco.command_templates import (
    iface as iface_command_template,
)


class CiscoIOSXRAddRemoveVlanActions(AddRemoveVlanActions):
    def set_vlan_to_interface(
        self,
        vlan_range,
        port_mode,
        port_name,
        qnq,
        c_tag,
        action_map=None,
        error_map=None,
    ):
        """Assign VLAM to a certain interface.

        :param vlan_range: range of vlans to be assigned
        :param port_mode: switchport mode
        :param port_name: interface name
        :param qnq: qinq settings (dot1q tunnel)
        :param c_tag: selective qnq
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        CommandTemplateExecutor(
            self._cli_service, iface_command_template.CONFIGURE_INTERFACE
        ).execute_command(port_name=port_name, l2transport="")

        CommandTemplateExecutor(
            self._cli_service,
            iface_command_template.NO_SHUTDOWN,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        if qnq:
            CommandTemplateExecutor(
                self._cli_service,
                vlan_command_template.VLAN_SUB_IFACE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(vlan_id=vlan_range, qnq="")
        else:
            CommandTemplateExecutor(
                self._cli_service,
                vlan_command_template.VLAN_SUB_IFACE,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(vlan_id=vlan_range, untagged="")
