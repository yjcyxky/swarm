import logging
from sshostmgt.dracclient.client import DRACClient

logger = logging.getLogger(__name__)

def get_ipmi_client(ipmi_addr, ipmi_username, ipmi_passwd, **kwargs):
    """Get a client instance
    """
    logger.info("IPMI Information: %s-%s-%s" % (ipmi_addr, ipmi_username, ipmi_passwd))
    try:
        client = DRACClient(ipmi_addr, ipmi_username, ipmi_passwd, **kwargs)
        return client
    except:
        return None

def ping(ip_addr):
    import subprocess
    import shlex

    cmd = "ping -c 1 %s" % ipaddress
    args = shlex.split(cmd)

    try:
        subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Ping IPMI NIC: %s" % ipaddress)
        return True
    except subprocess.CalledProcessError as e:
        logger.warning("Ping IPMI NIC %s: %s" % (ipaddress, str(e)))
        return False
