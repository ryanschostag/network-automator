"""
Entry point for the Network Automator program
"""
import logging
import network_auditor


def main():
    try:
        auditor = network_auditor.NetworkAuditor()
        for device in auditor.inventory:
            config = auditor.fetch_config(device)
            if config:
                auditor.save_config(config, device)
                diff = auditor.compare_with_golden(config)
                auditor.generate_report(device['hostname'], diff)
    except network_auditor.NetworkAuditorError as nae:
        logging.error(f"Network Auditor Error: {nae}")


if __name__ == "__main__":
    main()
