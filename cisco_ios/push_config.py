import logging
from os.path import isfile
import os

try:
    from cisco_ncclient import manager
    HAS_CISCO_CLIENT = True
except ImportError:
    HAS_CISCO_CLIENT = False


# Helper function to push configuration
def push(module):
    args = module.params

    try:
        dev = manager.Manager(args['host'], username=args['user'], password=args['password'])
        dev.connect()
    except Exception as err:
        msg = 'unable to connect to {0}: {1}'.format(args['host'], str(err))
        logging.error(msg)
        module.fail_json(msg=msg)
        return

    file_path = module.params['file']
    file_path = os.path.abspath(file_path)

    results = {}

    results['changed'] = False

    prev_config = dev.get_config()

    if isfile(file_path):
        logging.info("pushing file: {0}".format(file_path))
        results['file'] = file_path
        try:
            dev.edit_config(file_path)
            logging.info('Configuration pushed')
        except Exception as err:
            msg = "Unable to load config: {0}".format(err)
            module.fail_json(msg=msg)
    else:
        logging.error("Path to config file invalid")

    cur_config = dev.get_config()

    if cur_config != prev_config:
        results['changed'] = True

    logging.info("Completed")
    dev.close()
    module.exit_json(**results)


# ----------------------------------
# MAIN module
# ----------------------------------

def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True),
            user=dict(required=False, default=os.getenv('USER')),
            passw=dict(required=False, default=None),
            file=dict(required=True)
        )
    )

    if not HAS_CISCO_CLIENT:
        module.fail_json(msg='cisco_ncclient required, not provided')

    push(module)

    if not isfile(args['file']):
        module.fail_json(msg="file not found: {0}".format(args['file']))
        return

from ansible.module_utils.basic import *
main()
