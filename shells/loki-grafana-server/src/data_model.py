from cloudshell.shell.core.driver_context import ResourceCommandContext, AutoLoadDetails, AutoLoadAttribute, \
    AutoLoadResource
from collections import defaultdict


class LegacyUtils(object):
    def __init__(self):
        self._datamodel_clss_dict = self.__generate_datamodel_classes_dict()

    def migrate_autoload_details(self, autoload_details, context):
        model_name = context.resource.model
        root_name = context.resource.name
        root = self.__create_resource_from_datamodel(model_name, root_name)
        attributes = self.__create_attributes_dict(autoload_details.attributes)
        self.__attach_attributes_to_resource(attributes, '', root)
        self.__build_sub_resoruces_hierarchy(root, autoload_details.resources, attributes)
        return root

    def __create_resource_from_datamodel(self, model_name, res_name):
        return self._datamodel_clss_dict[model_name](res_name)

    def __create_attributes_dict(self, attributes_lst):
        d = defaultdict(list)
        for attribute in attributes_lst:
            d[attribute.relative_address].append(attribute)
        return d

    def __build_sub_resoruces_hierarchy(self, root, sub_resources, attributes):
        d = defaultdict(list)
        for resource in sub_resources:
            splitted = resource.relative_address.split('/')
            parent = '' if len(splitted) == 1 else resource.relative_address.rsplit('/', 1)[0]
            rank = len(splitted)
            d[rank].append((parent, resource))

        self.__set_models_hierarchy_recursively(d, 1, root, '', attributes)

    def __set_models_hierarchy_recursively(self, dict, rank, manipulated_resource, resource_relative_addr, attributes):
        if rank not in dict: # validate if key exists
            pass

        for (parent, resource) in dict[rank]:
            if parent == resource_relative_addr:
                sub_resource = self.__create_resource_from_datamodel(
                    resource.model.replace(' ', ''),
                    resource.name)
                self.__attach_attributes_to_resource(attributes, resource.relative_address, sub_resource)
                manipulated_resource.add_sub_resource(
                    self.__slice_parent_from_relative_path(parent, resource.relative_address), sub_resource)
                self.__set_models_hierarchy_recursively(
                    dict,
                    rank + 1,
                    sub_resource,
                    resource.relative_address,
                    attributes)

    def __attach_attributes_to_resource(self, attributes, curr_relative_addr, resource):
        for attribute in attributes[curr_relative_addr]:
            setattr(resource, attribute.attribute_name.lower().replace(' ', '_'), attribute.attribute_value)
        del attributes[curr_relative_addr]

    def __slice_parent_from_relative_path(self, parent, relative_addr):
        if parent is '':
            return relative_addr
        return relative_addr[len(parent) + 1:] # + 1 because we want to remove the seperator also

    def __generate_datamodel_classes_dict(self):
        return dict(self.__collect_generated_classes())

    def __collect_generated_classes(self):
        import sys, inspect
        return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class LokiGrafanaServer(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Loki Grafana Server'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype LokiGrafanaServer
        """
        result = LokiGrafanaServer(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'LokiGrafanaServer'

    @property
    def loki_port(self):
        """
        :rtype: float
        """
        return self.attributes['Loki Grafana Server.loki port'] if 'Loki Grafana Server.loki port' in self.attributes else None

    @loki_port.setter
    def loki_port(self, value='3100'):
        """
        port loki is hosted on
        :type value: float
        """
        self.attributes['Loki Grafana Server.loki port'] = value

    @property
    def loki_https(self):
        """
        :rtype: bool
        """
        return self.attributes['Loki Grafana Server.loki https'] if 'Loki Grafana Server.loki https' in self.attributes else None

    @loki_https.setter
    def loki_https(self, value=False):
        """
        set to true for https protocol
        :type value: bool
        """
        self.attributes['Loki Grafana Server.loki https'] = value

    @property
    def sandbox_api_ip(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.sandbox api ip'] if 'Loki Grafana Server.sandbox api ip' in self.attributes else None

    @sandbox_api_ip.setter
    def sandbox_api_ip(self, value):
        """
        ip of sandbox api server
        :type value: str
        """
        self.attributes['Loki Grafana Server.sandbox api ip'] = value

    @property
    def sandbox_api_port(self):
        """
        :rtype: float
        """
        return self.attributes['Loki Grafana Server.sandbox api port'] if 'Loki Grafana Server.sandbox api port' in self.attributes else None

    @sandbox_api_port.setter
    def sandbox_api_port(self, value='82'):
        """
        port of api host
        :type value: float
        """
        self.attributes['Loki Grafana Server.sandbox api port'] = value

    @property
    def sandbox_api_https(self):
        """
        :rtype: bool
        """
        return self.attributes['Loki Grafana Server.sandbox api https'] if 'Loki Grafana Server.sandbox api https' in self.attributes else None

    @sandbox_api_https.setter
    def sandbox_api_https(self, value=False):
        """
        whether sandbox api is configured with https
        :type value: bool
        """
        self.attributes['Loki Grafana Server.sandbox api https'] = value

    @property
    def promtail_dispro_job(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.promtail dispro job'] if 'Loki Grafana Server.promtail dispro job' in self.attributes else None

    @promtail_dispro_job.setter
    def promtail_dispro_job(self, value='DisProLog'):
        """
        name of job tailing the dispro json log
        :type value: str
        """
        self.attributes['Loki Grafana Server.promtail dispro job'] = value

    @property
    def promtail_teamserver_job(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.promtail teamserver job'] if 'Loki Grafana Server.promtail teamserver job' in self.attributes else None

    @promtail_teamserver_job.setter
    def promtail_teamserver_job(self, value='TeamServerLog'):
        """
        name of job tailing the teamserver json log
        :type value: str
        """
        self.attributes['Loki Grafana Server.promtail teamserver job'] = value

    @property
    def grafana_dashboard_url(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.grafana dashboard url'] if 'Loki Grafana Server.grafana dashboard url' in self.attributes else None

    @grafana_dashboard_url.setter
    def grafana_dashboard_url(self, value='http://localhost:3000/goto/IXuCCtX7z?orgId=1'):
        """
        Some attribute description
        :type value: str
        """
        self.attributes['Loki Grafana Server.grafana dashboard url'] = value

    @property
    def user(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.User'] if 'Loki Grafana Server.User' in self.attributes else None

    @user.setter
    def user(self, value):
        """
        User with administrative privileges
        :type value: str
        """
        self.attributes['Loki Grafana Server.User'] = value

    @property
    def password(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.Password'] if 'Loki Grafana Server.Password' in self.attributes else None

    @password.setter
    def password(self, value):
        """
        
        :type value: string
        """
        self.attributes['Loki Grafana Server.Password'] = value

    @property
    def enable_password(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.Enable Password'] if 'Loki Grafana Server.Enable Password' in self.attributes else None

    @enable_password.setter
    def enable_password(self, value):
        """
        The enable password is required by some CLI protocols such as Telnet and is required according to the device configuration.
        :type value: string
        """
        self.attributes['Loki Grafana Server.Enable Password'] = value

    @property
    def power_management(self):
        """
        :rtype: bool
        """
        return self.attributes['Loki Grafana Server.Power Management'] if 'Loki Grafana Server.Power Management' in self.attributes else None

    @power_management.setter
    def power_management(self, value=True):
        """
        Used by the power management orchestration, if enabled, to determine whether to automatically manage the device power status. Enabled by default.
        :type value: bool
        """
        self.attributes['Loki Grafana Server.Power Management'] = value

    @property
    def sessions_concurrency_limit(self):
        """
        :rtype: float
        """
        return self.attributes['Loki Grafana Server.Sessions Concurrency Limit'] if 'Loki Grafana Server.Sessions Concurrency Limit' in self.attributes else None

    @sessions_concurrency_limit.setter
    def sessions_concurrency_limit(self, value='1'):
        """
        The maximum number of concurrent sessions that the driver will open to the device. Default is 1 (no concurrency).
        :type value: float
        """
        self.attributes['Loki Grafana Server.Sessions Concurrency Limit'] = value

    @property
    def snmp_read_community(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.SNMP Read Community'] if 'Loki Grafana Server.SNMP Read Community' in self.attributes else None

    @snmp_read_community.setter
    def snmp_read_community(self, value):
        """
        The SNMP Read-Only Community String is like a password. It is sent along with each SNMP Get-Request and allows (or denies) access to device.
        :type value: string
        """
        self.attributes['Loki Grafana Server.SNMP Read Community'] = value

    @property
    def snmp_write_community(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.SNMP Write Community'] if 'Loki Grafana Server.SNMP Write Community' in self.attributes else None

    @snmp_write_community.setter
    def snmp_write_community(self, value):
        """
        The SNMP Write Community String is like a password. It is sent along with each SNMP Set-Request and allows (or denies) chaning MIBs values.
        :type value: string
        """
        self.attributes['Loki Grafana Server.SNMP Write Community'] = value

    @property
    def snmp_v3_user(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.SNMP V3 User'] if 'Loki Grafana Server.SNMP V3 User' in self.attributes else None

    @snmp_v3_user.setter
    def snmp_v3_user(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Loki Grafana Server.SNMP V3 User'] = value

    @property
    def snmp_v3_password(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.SNMP V3 Password'] if 'Loki Grafana Server.SNMP V3 Password' in self.attributes else None

    @snmp_v3_password.setter
    def snmp_v3_password(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: string
        """
        self.attributes['Loki Grafana Server.SNMP V3 Password'] = value

    @property
    def snmp_v3_private_key(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.SNMP V3 Private Key'] if 'Loki Grafana Server.SNMP V3 Private Key' in self.attributes else None

    @snmp_v3_private_key.setter
    def snmp_v3_private_key(self, value):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Loki Grafana Server.SNMP V3 Private Key'] = value

    @property
    def snmp_v3_authentication_protocol(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.SNMP V3 Authentication Protocol'] if 'Loki Grafana Server.SNMP V3 Authentication Protocol' in self.attributes else None

    @snmp_v3_authentication_protocol.setter
    def snmp_v3_authentication_protocol(self, value='No Authentication Protocol'):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Loki Grafana Server.SNMP V3 Authentication Protocol'] = value

    @property
    def snmp_v3_privacy_protocol(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.SNMP V3 Privacy Protocol'] if 'Loki Grafana Server.SNMP V3 Privacy Protocol' in self.attributes else None

    @snmp_v3_privacy_protocol.setter
    def snmp_v3_privacy_protocol(self, value='No Privacy Protocol'):
        """
        Relevant only in case SNMP V3 is in use.
        :type value: str
        """
        self.attributes['Loki Grafana Server.SNMP V3 Privacy Protocol'] = value

    @property
    def snmp_version(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.SNMP Version'] if 'Loki Grafana Server.SNMP Version' in self.attributes else None

    @snmp_version.setter
    def snmp_version(self, value=''):
        """
        The version of SNMP to use. Possible values are v1, v2c and v3.
        :type value: str
        """
        self.attributes['Loki Grafana Server.SNMP Version'] = value

    @property
    def enable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['Loki Grafana Server.Enable SNMP'] if 'Loki Grafana Server.Enable SNMP' in self.attributes else None

    @enable_snmp.setter
    def enable_snmp(self, value=True):
        """
        If set to True and SNMP isn???t enabled yet in the device the Shell will automatically enable SNMP in the device when Autoload command is called. SNMP must be enabled on the device for the Autoload command to run successfully. True by default.
        :type value: bool
        """
        self.attributes['Loki Grafana Server.Enable SNMP'] = value

    @property
    def disable_snmp(self):
        """
        :rtype: bool
        """
        return self.attributes['Loki Grafana Server.Disable SNMP'] if 'Loki Grafana Server.Disable SNMP' in self.attributes else None

    @disable_snmp.setter
    def disable_snmp(self, value=False):
        """
        If set to True SNMP will be disabled automatically by the Shell after the Autoload command execution is completed. False by default.
        :type value: bool
        """
        self.attributes['Loki Grafana Server.Disable SNMP'] = value

    @property
    def console_server_ip_address(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.Console Server IP Address'] if 'Loki Grafana Server.Console Server IP Address' in self.attributes else None

    @console_server_ip_address.setter
    def console_server_ip_address(self, value):
        """
        The IP address of the console server, in IPv4 format.
        :type value: str
        """
        self.attributes['Loki Grafana Server.Console Server IP Address'] = value

    @property
    def console_user(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.Console User'] if 'Loki Grafana Server.Console User' in self.attributes else None

    @console_user.setter
    def console_user(self, value):
        """
        
        :type value: str
        """
        self.attributes['Loki Grafana Server.Console User'] = value

    @property
    def console_port(self):
        """
        :rtype: float
        """
        return self.attributes['Loki Grafana Server.Console Port'] if 'Loki Grafana Server.Console Port' in self.attributes else None

    @console_port.setter
    def console_port(self, value):
        """
        The port on the console server, usually TCP port, which the device is associated with.
        :type value: float
        """
        self.attributes['Loki Grafana Server.Console Port'] = value

    @property
    def console_password(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.Console Password'] if 'Loki Grafana Server.Console Password' in self.attributes else None

    @console_password.setter
    def console_password(self, value):
        """
        
        :type value: string
        """
        self.attributes['Loki Grafana Server.Console Password'] = value

    @property
    def cli_connection_type(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.CLI Connection Type'] if 'Loki Grafana Server.CLI Connection Type' in self.attributes else None

    @cli_connection_type.setter
    def cli_connection_type(self, value='Auto'):
        """
        The CLI connection type that will be used by the driver. Possible values are Auto, Console, SSH, Telnet and TCP. If Auto is selected the driver will choose the available connection type automatically. Default value is Auto.
        :type value: str
        """
        self.attributes['Loki Grafana Server.CLI Connection Type'] = value

    @property
    def cli_tcp_port(self):
        """
        :rtype: float
        """
        return self.attributes['Loki Grafana Server.CLI TCP Port'] if 'Loki Grafana Server.CLI TCP Port' in self.attributes else None

    @cli_tcp_port.setter
    def cli_tcp_port(self, value):
        """
        TCP Port to user for CLI connection. If kept empty a default CLI port will be used based on the chosen protocol, for example Telnet will use port 23.
        :type value: float
        """
        self.attributes['Loki Grafana Server.CLI TCP Port'] = value

    @property
    def backup_location(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.Backup Location'] if 'Loki Grafana Server.Backup Location' in self.attributes else None

    @backup_location.setter
    def backup_location(self, value):
        """
        Used by the save/restore orchestration to determine where backups should be saved.
        :type value: str
        """
        self.attributes['Loki Grafana Server.Backup Location'] = value

    @property
    def backup_type(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.Backup Type'] if 'Loki Grafana Server.Backup Type' in self.attributes else None

    @backup_type.setter
    def backup_type(self, value='File System'):
        """
        Supported protocols for saving and restoring of configuration and firmware files. Possible values are 'File System' 'FTP' and 'TFTP'. Default value is 'File System'.
        :type value: str
        """
        self.attributes['Loki Grafana Server.Backup Type'] = value

    @property
    def backup_user(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.Backup User'] if 'Loki Grafana Server.Backup User' in self.attributes else None

    @backup_user.setter
    def backup_user(self, value):
        """
        Username for the storage server used for saving and restoring of configuration and firmware files.
        :type value: str
        """
        self.attributes['Loki Grafana Server.Backup User'] = value

    @property
    def backup_password(self):
        """
        :rtype: string
        """
        return self.attributes['Loki Grafana Server.Backup Password'] if 'Loki Grafana Server.Backup Password' in self.attributes else None

    @backup_password.setter
    def backup_password(self, value):
        """
        Password for the storage server used for saving and restoring of configuration and firmware files.
        :type value: string
        """
        self.attributes['Loki Grafana Server.Backup Password'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def system_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.System Name'] if 'CS_GenericResource.System Name' in self.attributes else None

    @system_name.setter
    def system_name(self, value):
        """
        A unique identifier for the device, if exists in the device terminal/os.
        :type value: str
        """
        self.attributes['CS_GenericResource.System Name'] = value

    @property
    def vendor(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Vendor'] if 'CS_GenericResource.Vendor' in self.attributes else None

    @vendor.setter
    def vendor(self, value=''):
        """
        The name of the device manufacture.
        :type value: str
        """
        self.attributes['CS_GenericResource.Vendor'] = value

    @property
    def contact_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Contact Name'] if 'CS_GenericResource.Contact Name' in self.attributes else None

    @contact_name.setter
    def contact_name(self, value):
        """
        The name of a contact registered in the device.
        :type value: str
        """
        self.attributes['CS_GenericResource.Contact Name'] = value

    @property
    def location(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Location'] if 'CS_GenericResource.Location' in self.attributes else None

    @location.setter
    def location(self, value=''):
        """
        The device physical location identifier. For example Lab1/Floor2/Row5/Slot4.
        :type value: str
        """
        self.attributes['CS_GenericResource.Location'] = value

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Model'] if 'CS_GenericResource.Model' in self.attributes else None

    @model.setter
    def model(self, value=''):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['CS_GenericResource.Model'] = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_GenericResource.Model Name'] if 'CS_GenericResource.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_GenericResource.Model Name'] = value


class ResourcePort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Loki Grafana Server.ResourcePort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype ResourcePort
        """
        result = ResourcePort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'ResourcePort'

    @property
    def mac_address(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.ResourcePort.MAC Address'] if 'Loki Grafana Server.ResourcePort.MAC Address' in self.attributes else None

    @mac_address.setter
    def mac_address(self, value=''):
        """
        
        :type value: str
        """
        self.attributes['Loki Grafana Server.ResourcePort.MAC Address'] = value

    @property
    def ipv4_address(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.ResourcePort.IPv4 Address'] if 'Loki Grafana Server.ResourcePort.IPv4 Address' in self.attributes else None

    @ipv4_address.setter
    def ipv4_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['Loki Grafana Server.ResourcePort.IPv4 Address'] = value

    @property
    def ipv6_address(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.ResourcePort.IPv6 Address'] if 'Loki Grafana Server.ResourcePort.IPv6 Address' in self.attributes else None

    @ipv6_address.setter
    def ipv6_address(self, value):
        """
        
        :type value: str
        """
        self.attributes['Loki Grafana Server.ResourcePort.IPv6 Address'] = value

    @property
    def port_speed(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.ResourcePort.Port Speed'] if 'Loki Grafana Server.ResourcePort.Port Speed' in self.attributes else None

    @port_speed.setter
    def port_speed(self, value):
        """
        The port speed (e.g 10Gb/s, 40Gb/s, 100Mb/s)
        :type value: str
        """
        self.attributes['Loki Grafana Server.ResourcePort.Port Speed'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_Port.Model Name'] if 'CS_Port.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_Port.Model Name'] = value


class GenericPowerPort(object):
    def __init__(self, name):
        """
        
        """
        self.attributes = {}
        self.resources = {}
        self._cloudshell_model_name = 'Loki Grafana Server.GenericPowerPort'
        self._name = name

    def add_sub_resource(self, relative_path, sub_resource):
        self.resources[relative_path] = sub_resource

    @classmethod
    def create_from_context(cls, context):
        """
        Creates an instance of NXOS by given context
        :param context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :type context: cloudshell.shell.core.driver_context.ResourceCommandContext
        :return:
        :rtype GenericPowerPort
        """
        result = GenericPowerPort(name=context.resource.name)
        for attr in context.resource.attributes:
            result.attributes[attr] = context.resource.attributes[attr]
        return result

    def create_autoload_details(self, relative_path=''):
        """
        :param relative_path:
        :type relative_path: str
        :return
        """
        resources = [AutoLoadResource(model=self.resources[r].cloudshell_model_name,
            name=self.resources[r].name,
            relative_address=self._get_relative_path(r, relative_path))
            for r in self.resources]
        attributes = [AutoLoadAttribute(relative_path, a, self.attributes[a]) for a in self.attributes]
        autoload_details = AutoLoadDetails(resources, attributes)
        for r in self.resources:
            curr_path = relative_path + '/' + r if relative_path else r
            curr_auto_load_details = self.resources[r].create_autoload_details(curr_path)
            autoload_details = self._merge_autoload_details(autoload_details, curr_auto_load_details)
        return autoload_details

    def _get_relative_path(self, child_path, parent_path):
        """
        Combines relative path
        :param child_path: Path of a model within it parent model, i.e 1
        :type child_path: str
        :param parent_path: Full path of parent model, i.e 1/1. Might be empty for root model
        :type parent_path: str
        :return: Combined path
        :rtype str
        """
        return parent_path + '/' + child_path if parent_path else child_path

    @staticmethod
    def _merge_autoload_details(autoload_details1, autoload_details2):
        """
        Merges two instances of AutoLoadDetails into the first one
        :param autoload_details1:
        :type autoload_details1: AutoLoadDetails
        :param autoload_details2:
        :type autoload_details2: AutoLoadDetails
        :return:
        :rtype AutoLoadDetails
        """
        for attribute in autoload_details2.attributes:
            autoload_details1.attributes.append(attribute)
        for resource in autoload_details2.resources:
            autoload_details1.resources.append(resource)
        return autoload_details1

    @property
    def cloudshell_model_name(self):
        """
        Returns the name of the Cloudshell model
        :return:
        """
        return 'GenericPowerPort'

    @property
    def model(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.GenericPowerPort.Model'] if 'Loki Grafana Server.GenericPowerPort.Model' in self.attributes else None

    @model.setter
    def model(self, value):
        """
        The device model. This information is typically used for abstract resource filtering.
        :type value: str
        """
        self.attributes['Loki Grafana Server.GenericPowerPort.Model'] = value

    @property
    def serial_number(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.GenericPowerPort.Serial Number'] if 'Loki Grafana Server.GenericPowerPort.Serial Number' in self.attributes else None

    @serial_number.setter
    def serial_number(self, value):
        """
        
        :type value: str
        """
        self.attributes['Loki Grafana Server.GenericPowerPort.Serial Number'] = value

    @property
    def version(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.GenericPowerPort.Version'] if 'Loki Grafana Server.GenericPowerPort.Version' in self.attributes else None

    @version.setter
    def version(self, value):
        """
        The firmware version of the resource.
        :type value: str
        """
        self.attributes['Loki Grafana Server.GenericPowerPort.Version'] = value

    @property
    def port_description(self):
        """
        :rtype: str
        """
        return self.attributes['Loki Grafana Server.GenericPowerPort.Port Description'] if 'Loki Grafana Server.GenericPowerPort.Port Description' in self.attributes else None

    @port_description.setter
    def port_description(self, value):
        """
        The description of the port as configured in the device.
        :type value: str
        """
        self.attributes['Loki Grafana Server.GenericPowerPort.Port Description'] = value

    @property
    def name(self):
        """
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        
        :type value: str
        """
        self._name = value

    @property
    def cloudshell_model_name(self):
        """
        :rtype: str
        """
        return self._cloudshell_model_name

    @cloudshell_model_name.setter
    def cloudshell_model_name(self, value):
        """
        
        :type value: str
        """
        self._cloudshell_model_name = value

    @property
    def model_name(self):
        """
        :rtype: str
        """
        return self.attributes['CS_PowerPort.Model Name'] if 'CS_PowerPort.Model Name' in self.attributes else None

    @model_name.setter
    def model_name(self, value=''):
        """
        The catalog name of the device model. This attribute will be displayed in CloudShell instead of the CloudShell model.
        :type value: str
        """
        self.attributes['CS_PowerPort.Model Name'] = value



