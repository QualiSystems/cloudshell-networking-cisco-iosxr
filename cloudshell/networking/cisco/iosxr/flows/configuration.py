from cloudshell.networking.cisco.flows.cisco_configuration_flow import (
    CiscoConfigurationFlow,
)

from cloudshell.networking.cisco.iosxr.command_actions.system import (
    CiscoIOSXRSystemActions,
)
from cloudshell.networking.cisco.iosxr.constants import IOSXR_FILE_SYSTEM


class CiscoIOSXRConfigurationFlow(CiscoConfigurationFlow):
    @property
    def _file_system(self):
        return IOSXR_FILE_SYSTEM

    def _get_system_actions(self, enable_session):
        return CiscoIOSXRSystemActions(enable_session, self._logger)

    def _restore_flow(
        self,
        path: str,
        configuration_type: str,
        restore_method: str,
        vrf_management_name: str,
    ):
        """Execute flow which save selected file to the provided destination.

        :param path: the path to the configuration file, including the
                     configuration file name
        :param restore_method: the restore method to use when restoring the
                               configuration file. Possible Values are append
                               and override
        :param configuration_type: the configuration type to restore. Possible
                                   values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """
        if "-config" not in configuration_type:
            configuration_type += "-config"

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as enable_session:
            system_actions = self._get_system_actions(enable_session)
            if "startup" in configuration_type:
                raise Exception("Startup configuration is not supported by IOS-XR")

            elif "running" in configuration_type:
                if restore_method == "override":
                    with enable_session.enter_mode(
                        self._cli_handler.config_mode
                    ) as config_session:
                        restore_action = CiscoIOSXRSystemActions(
                            config_session, self._logger
                        )
                        restore_action.load(source_file=path, vrf=vrf_management_name)
                        restore_action.replace_config()
                else:
                    system_actions.copy(
                        source=path,
                        destination=configuration_type,
                        vrf=vrf_management_name,
                        action_map=system_actions.prepare_action_map(
                            path, configuration_type
                        ),
                    )
