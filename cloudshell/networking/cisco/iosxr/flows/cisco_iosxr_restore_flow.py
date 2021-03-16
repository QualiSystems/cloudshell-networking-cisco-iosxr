from collections import OrderedDict
from cloudshell.networking.cisco.flows.cisco_restore_flow import CiscoRestoreFlow
from cloudshell.networking.cisco.iosxr.command_actions.cisco_iosxr_system_actions import CiscoIOSXRSystemActions


class CiscoIOSXRRestoreFlow(CiscoRestoreFlow):
    def __init__(self, cli_handler, logger):
        super(CiscoIOSXRRestoreFlow, self).__init__(cli_handler, logger)

    def execute_flow(self, path, configuration_type, restore_method, vrf_management_name=None):
        """ Execute flow which save selected file to the provided destination

        :param path: the path to the configuration file, including the configuration file name
        :param restore_method: the restore method to use when restoring the configuration file.
                               Possible Values are append and override
        :param configuration_type: the configuration type to restore. Possible values are startup and running
        :param vrf_management_name: Virtual Routing and Forwarding Name
        """

        if "-config" not in configuration_type:
            configuration_type += "-config"

        with self._cli_handler.get_cli_service(self._cli_handler.enable_mode) as enable_session:
            restore_action = CiscoIOSXRSystemActions(enable_session, self._logger)
            if "startup" in configuration_type:
                raise Exception(self.__class__.__name__, "Startup configuration is not supported by IOS-XR")

            elif "running" in configuration_type:
                if restore_method == "override":
                    with enable_session.enter_mode(self._cli_handler.config_mode) as config_session:
                        restore_action = CiscoIOSXRSystemActions(config_session, self._logger)
                        restore_action.load(source_file=path, vrf=vrf_management_name)
                        restore_action.replace_config()
                else:
                    restore_action.copy(source=path, destination=configuration_type, vrf=vrf_management_name,
                                        action_map=restore_action.prepare_action_map(path, configuration_type))
