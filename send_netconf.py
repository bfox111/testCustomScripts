#!/usr/bin/env python


"""

Author: Barbara A. Fox <bfox@ciena.com>

Read in output from the "log view netconf-rpc edit" command.  Reverse the order and print out 
Netconf commands that can be lifted and dropped into a device

Strings are immutable - hence all the crazy variables.

Usage:  convert_log_to_netconf.py <log-output> <netconf-cmds>


"""

import sys
import logging
from ncclient import manager
# from ncclient.devices.ciena import *

logger = logging.getLogger('barb')


def netconf_to_device(ip, user, passwd, log_file):

    logging.basicConfig(filename='myapp.log', level=logging.INFO)
    logger.info('Started netconf_to_device')
    logger.info('IP address is %s ', ip)
    logger.info('user is %s ', user)
    logger.info('password is %s ', passwd)

    # Define your NETCONF device parameters
    hostname = ip
    username =  user
    password = passwd
    port = 830  # Default NETCONF port

    cleaned_rpc_calls= ''

    # for line in log_file:
    #     logger.info('before strip:  x%sx', line)
    #     clean_line = line.strip()
    #     logger.info('after strip:  y%sy', clean_line)
    #     new_rpc = cleaned_rpc_calls+clean_line
    #     cleaned_rpc_calls = new_rpc


    # Define your RPC XML payload
    rpc_command = """
    <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
        <get>
            <!-- Your specific RPC command goes here -->
        </get>
    </rpc>
    """

    logger.info('This is the RPC calls being sent')
    logger.info(log_file)
    # Connect to the NETCONF device
    with manager.connect(
        host=hostname,
        port=port,
        username=username,
        password=password,
        hostkey_verify=False,  # You might want to set it to True for production
        timeout=100,
        device_params={'name': 'alu'}
    ) as m:
        # Send the RPC call
        logger.info('It returned from the connect')
        logger.info('%s', log_file)
        response = m.dispatch(log_file)

        logger.info("RESPONSE")
        logger.info(response)
        # Print the response
        m.close_session()
        print(response.xml)


# Mainline of Program
#

code = """
# <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
	<edit-config>
		<target>
			<running/>
		</target>
		<default-operation>merge</default-operation>
		<test-option>test-then-set</test-option>
		<config>
			<classifiers xmlns="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">
				<classifier>
					<name>UNTAGGED</name>
					<filter-entry>
						<filter-parameter xmlns:classifier="urn:ciena:params:xml:ns:yang:ciena-pn::ciena-mef-classifier">classifier:vtag-stack</filter-parameter>
						<untagged-exclude-priority-tagged>true</untagged-exclude-priority-tagged>
					</filter-entry>
				</classifier>
			</classifiers>
		</config>
	</edit-config>
# </rpc>

"""
code2 ="<get><filter type=\"subtree\"><system xmlns=\"http://openconfig.net/yang/system\"><config><hostname/></config></system></filter></get>"
result = netconf_to_device('10.92.44.34', 'diag', 'ciena123', code)
