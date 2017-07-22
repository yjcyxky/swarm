import sys, os
# for import dracclinet
SSHOSTMGT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SSHOSTMGT_DIR)

# stores configuration and provides introspection
default_app_config = 'sshostmgt.apps.SshostmgtConfig'