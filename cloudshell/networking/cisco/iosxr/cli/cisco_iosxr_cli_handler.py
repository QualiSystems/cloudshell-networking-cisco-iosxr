from cloudshell.cli.service.cli_service_impl import CliServiceImpl
from cloudshell.networking.cisco.cli.cisco_cli_handler import CiscoCli, CiscoCliHandler
from cloudshell.networking.cisco.iosxr.cli.cisco_iosxr_command_modes import CiscoIOSXRConfigCommandMode, \
    CiscoIOSXRAdminCommandMode
from cloudshell.networking.cisco.cli.cisco_command_modes import (
    ConfigCommandMode,
    EnableCommandMode,
)


class CiscoIOSXRCli(CiscoCli):
    def get_cli_handler(self, resource_config, logger):
        return CiscoIOSXRCliHandler(self.cli, resource_config, logger)


class CiscoIOSXRCliHandler(CiscoCliHandler):
    @property
    def config_mode(self):
        return self.modes[CiscoIOSXRConfigCommandMode]

    @property
    def admin_mode(self):
        return self.modes[CiscoIOSXRAdminCommandMode]

    def on_session_start(self, session, logger):
        """Send default commands to configure/clear session outputs."""
        cli_service = CliServiceImpl(session=session, command_mode=self.enable_mode, logger=logger)
        cli_service.send_command("terminal length 0", EnableCommandMode.PROMPT)
        cli_service.send_command("terminal width 300", EnableCommandMode.PROMPT)
        with cli_service.enter_mode(self.config_mode) as config_session:
            config_session.send_command("no logging console", ConfigCommandMode.PROMPT)
