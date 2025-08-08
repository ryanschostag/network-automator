
import os
import yaml
import logging
import logging.config
from datetime import datetime
from netmiko import ConnectHandler
from pathlib import Path
from difflib import unified_diff


class Config:
    """
    Configuration class to handle settings for the Network Auditor.
    """
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_file : str = os.path.join(
        current_directory,
        os.path.basename(__file__).replace('.py', '.yaml')
    )

    def __init__(self, config_file : str = ''):
        if os.path.isfile(config_file):
            self.config_file = config_file
        self.settings = self.load_config()
        self.templates_folder = self.get('auditor', {}).get('templates_folder', '')
        self.template_directory = os.path.join(
            self.current_directory, self.templates_folder
        )
        self.golden_file = self.get('auditor', {}).get('golden_file', '')
        self.golden_file = os.path.join(
            self.template_directory, self.golden_file
        )
        self.config_logging()

    def load_config(self) -> dict:
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Configuration file {self.config_file} does not exist.")

        with open(self.config_file, 'r') as config_io:
            config = yaml.safe_load(config_io)

        return config
    
    def get(self, key: str, default=None):
        return self.settings.get(key, default)

    def config_logging(self):
        """
        Configures logging based on the settings in the configuration file.
        """
        log_config = self.get('logging', {})
        log_directory = os.path.join(
            self.current_directory,
            log_config.get('log_folder', '')
        )
        Path(log_directory).mkdir(parents=True, exist_ok=True)
        log_filename = log_config.get('log_filename', '')
        log_filepath = os.path.join(
            log_directory, log_filename
        )
        log_config_filename = log_config.get('log_config_file', '')
        log_config_filepath = os.path.join(
            self.current_directory, log_config_filename
        )
    
        if not os.path.isfile(log_config_filepath):
            raise FileNotFoundError(
                f"Log configuration file {log_config_filepath} does not exist."
            )

        with open(log_config_filepath, 'r') as log_config_io:
            log_config_data = yaml.safe_load(log_config_io)

        log_config_data['handlers']['file']['filename'] = log_filepath
        logging.config.dictConfig(log_config_data)
        logging.info("Logging configured successfully.")


class NetworkAuditorError(Exception):
    """Custom exception for Network Auditor errors."""
    pass


class NetworkAuditor(Config):
    def __init__(self, inventory_file : str = '', config_file : str = ''):
        super().__init__(config_file)
        if os.path.isfile(inventory_file):
            self.inventory_file = inventory_file
        else:
            self.inventory_file = self.get('auditor', {}).get('inventory_file', '')
        self.inventory = self.load_inventory()
        logging.info("Network Auditor initialized with inventory: %s", self.inventory)

    def load_inventory(self) -> list[dict[str, str]]:
        if not os.path.exists(self.inventory_file):
            raise FileNotFoundError(f"Inventory file {self.inventory_file} does not exist.")

        with open(self.inventory_file, 'r') as inventory_io:
            return yaml.safe_load(inventory_io)

    def fetch_config(self, device):
        logging.info(f"[+] Connecting to {device['host']} ({device['ip']})")
        try:
            conn = ConnectHandler(**device)
            config = conn.send_command("show running-config")
            conn.disconnect()
            return config
        except Exception as e:
            logging.error(f"[-] Failed to connect to {device['host']}: {e}")
            return None

    def save_config(self, config, device):
        Path("configs").mkdir(exist_ok=True)
        filename = f"configs/{device['hostname']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cfg"
        with open(filename, 'w') as f:
            f.write(config)
        return filename

    def compare_with_golden(self, config):
        with open(self.golden_file, 'r') as f:
            golden = f.readlines()
        current = config.splitlines(keepends=True)
        diff = list(unified_diff(golden, current, fromfile=self.golden_file, tofile='device_config'))
        return diff

    def generate_report(self, device_name, diff):
        Path("reports").mkdir(exist_ok=True)
        report_path = os.path.join('reports', f"{device_name}_report.txt")
        with open(report_path, 'w') as f:
            if diff:
                f.writelines(diff)
            else:
                f.write("No differences found. Configuration is compliant.\n")
        logging.info(f"[*] Report saved to {report_path}")
        return report_path
