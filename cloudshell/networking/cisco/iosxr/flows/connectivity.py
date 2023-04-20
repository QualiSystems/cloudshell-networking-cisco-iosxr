from cloudshell.networking.cisco.flows.cisco_connectivity_flow import (
    CiscoConnectivityFlow,
)

from cloudshell.networking.cisco.iosxr.command_actions.add_remove_vlan import (
    CiscoIOSXRAddRemoveVlanActions,
)
from cloudshell.networking.cisco.iosxr.command_actions.iface import (
    CiscoIOSXRIFaceActions,
)
from cloudshell.networking.cisco.iosxr.command_actions.system import (
    CiscoIOSXRSystemActions,
)


class CiscoIOSXRConnectivityFlow(CiscoConnectivityFlow):
    def _get_iface_actions(self, config_session):
        return CiscoIOSXRIFaceActions(config_session, self._logger)

    def _add_vlan_flow(self, vlan_range, port_mode, full_name, qnq, c_tag):
        self._logger.info(f"Add VLAN(s) {vlan_range} configuration started")

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            iface_actions = CiscoIOSXRIFaceActions(config_session, self._logger)
            vlan_actions = CiscoIOSXRAddRemoveVlanActions(config_session, self._logger)
            system_actions = CiscoIOSXRSystemActions(config_session, self._logger)
            port_name = iface_actions.get_port_name(full_name)

            if port_name and "-" not in vlan_range:
                port_name += f".{vlan_range}"
            else:
                raise Exception("Vlan range is not supported for IOS XR devices")

            iface_actions.enter_iface_config_mode(port_name)
            vlan_actions.set_vlan_to_interface(
                vlan_range, port_mode, port_name, qnq, c_tag
            )
            system_actions.commit()
            current_config = iface_actions.get_current_interface_config(port_name)

            if port_name not in current_config:
                raise Exception(f"[FAIL] VLAN(s) {vlan_range} configuration failed")

        msg = f"VLAN(s) {vlan_range} configuration completed successfully"
        self._logger.info(msg)
        return f"[ OK ] {msg}"

    def _remove_vlan_flow(self, vlan_range, full_name):
        self._logger.info("Remove Vlan {vlan_range} configuration started")

        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as config_session:
            iface_action = CiscoIOSXRIFaceActions(config_session, self._logger)
            vlan_actions = CiscoIOSXRAddRemoveVlanActions(config_session, self._logger)
            system_actions = CiscoIOSXRSystemActions(config_session, self._logger)
            port_name = iface_action.get_port_name(full_name)

            if port_name and "-" not in vlan_range:
                port_name += f".{vlan_range}"
            else:
                raise Exception("Vlan range is not supported for IOS XR devices")

            vlan_actions.clean_vlan_sub_interface(port_name)
            system_actions.commit()
            current_config = iface_action.get_current_interface_config(port_name)

            if port_name in current_config:
                raise Exception(f"[FAIL] VLAN(s) {vlan_range} removing failed")

        msg = f"VLAN(s) {vlan_range} removing completed successfully"
        self._logger.info(msg)
        return f"[ OK ] {msg}"
