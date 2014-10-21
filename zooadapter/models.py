import HTMLParser,re,urllib,rsa,json
from django.db import models
from solo.models import SingletonModel
from common.models import Common
from pydap.responses.lib import BaseResponse
from pydap.lib import walk
from pydap.client import open_url

class ZooAdapterConfig(SingletonModel):

   class Meta:
      verbose_name_plural = "Config"
      verbose_name = "Config"

   zoo_server_address = models.CharField(max_length=255)
   thredds_server_address = models.CharField(max_length=255)
   zoo_public_key = models.CharField(max_length=1000)
   zoo_private_key = models.CharField(max_length=1000)

   def get_public_key(self):
      """ Get ready-to-use PublicKey object."""
      return rsa.PublicKey.load_pkcs1(ZooAdapter.config.zoo_public_key)

   def get_private_key(self):
      """ Get ready-to-use PrivateKey object."""
      return rsa.PrivateKey.load_pkcs1(ZooAdapter.config.zoo_private_key)

   def get_zoo_server_address(self):
      """ Return zoo server address ready for use."""
      return Common.prepare_config_address(self.zoo_server_address)

   def get_thredds_server_address(self):
      """ Return thredds server address ready for use."""
      return Common.prepare_config_address(self.thredds_server_address)

   def __unicode__(self):
      return u"Zoo Adapter Configuration"

class ZooComputationStatus(models.Model):
   code = models.IntegerField(primary_key=True)
   status = models.CharField(max_length=100)
   details = models.CharField(max_length=1000)

class ZooAdapter():

   config = ZooAdapterConfig.objects.get()

   @staticmethod
   def update_thredds_address(address):
      """Update address of the THREDDS server used by Zoo.

      Keyword arguments:
      address -- new THREDDS server address
      """

      pubkey = ZooAdapter.config.get_public_key()

      encrypted_address = rsa.encrypt(urllib.quote_plus(address),pubkey)

      host_url = (ZooAdapter.config.get_zoo_server_address() +
            '/cgi-bin/operators/zoo_loader.cgi?request=Execute'
            '&service=WPS&version=1.0.0.0&identifier=ChangeThredds'
            '&DataInputs=url=' + encrypted_address)

      result = urllib.urlopen(host_url)


   @staticmethod
   def get_datafile_variables(url):
      """Get datafile variables in JSON format
         
      Keyword arguments:
      url -- datafile remote url
      """

      dataset = open_url(url)
      attributes = {}
      for child in walk(dataset):
         parts = child.id.split('.')
         if hasattr(child, "dimensions") and len(parts) == 1:
            isVar = False
            item = {}
            if len(child.dimensions) == 1:
               if (child.dimensions[0] != child.id
                     and child.dimensions[0] == 'time'):
                  isVar = True
                  item['dimensions'] = 1
            elif len(child.dimensions) == 3:
               if ('lat' in child.dimensions
                     and 'lon' in child.dimensions
                     and 'time' in child.dimensions):
                  isVar = True
                  item['dimensions'] = 3

            if isVar:
                  # Generates a name for the variable. Uses its long name if
                  # possible, otherwise uses the id.
                  if (child.attributes.has_key('long_name')
                        and child.attributes['long_name'] != ""):
                     item['name'] = child.attributes['long_name']
                  else:
                     item['name'] = child.id

                  attributes[child.id] = item

      if hasattr(dataset, 'close'):
         dataset.close()

      out = json.dumps(attributes)
      return out

   @staticmethod
   def schedule_computation(computation):
      """ Submit a Computation to the Zoo server and schedule it to run.

      Returns a dictionary of result links (wms, nc, opendap)
   
      Keyword arguments:
      computation -- the computation to schedule
      """

      return_bundle = {}
      result_links = {}

      schedule_link = ZooAdapter._get_schedule_link(computation)

      # contains info about our scheduled_computation
      filehandle = urllib.urlopen(schedule_link)
      text = filehandle.read()

      result_links['wms'] = ZooAdapter._get_result_link(text, 'wms')
      result_links['nc'] = ZooAdapter._get_result_link(text, 'ncfile')
      result_links['opendap'] = ZooAdapter._get_result_link(text, 'opendap')

      return_bundle['status'] = ZooAdapter._get_result_status(text)
      return_bundle['result_links'] = result_links

      return return_bundle

   @staticmethod
   def _get_result_status(text):
      """Get the status of the computation from the result file.
         
      Keyword arguments:
      filehandle -- the result file"""

      regex = ('<wps:Output>.*' 
            '<ows:Identifier>Status</ows:Identifier>.*' 
            '<wps:LiteralData.*?>(\d*)</wps:LiteralData>'
            '.*</wps:Output>')

      match = re.search(regex, text, re.DOTALL)

      if match:
         return ZooComputationStatus.objects.filter(code=match.group(1))[0]

      return None
      
   @staticmethod
   def _get_schedule_link(computation):
      """ Constructs & returns the link to use to schedule a Computation 
      in Zoo. """

      descriptor_file = (ZooAdapter.config.get_zoo_server_address() + 
            '/cgi-bin/zoo_loader.cgi?request=Execute&service=WPS'
            '&version=1.0.0.0&identifier=jobScheduler&DataInputs='
            'selection=' + computation.calculation.name + ';'
            'urls=')

      datafiles_str = ''
            
      #append all data files
      for data in computation.get_computationdata():
         datafiles_str += data.datafile.cached_file + '?'
         datafiles_str += '|'.join(data.variables) + '|'

      #Remove trailing pipe 
      descriptor_file += datafiles_str[:-1]

      #add computation id
      descriptor_file += ';jobid=' + str(computation.id)

      return descriptor_file

   @staticmethod
   def _get_result_link(text, format):
      """ Search for a result link for a particular format (wms, nc, opendap)
      within the xml file returned when scheduling a computation.

      Keyword arguments:
      filehandle -- the description file for a scheduled computation
      format -- the foramt to search for (wms, nc or opendap)
      """

      regex = '\[' + format + '\](.*?)\[/' + format + '\]'
      result_url = ''

      match = re.search(regex, text)

      if match:
         result_url = match.group(1)
         # decode html entities
         html_parser = HTMLParser.HTMLParser()
         result_url = html_parser.unescape(result_url)

      return result_url

class ZooDashboard(SingletonModel):
   """ Empty model used purely to generate a link on the admin frontend """

   class Meta:
      verbose_name_plural = "Dashboard"
      verbose_name = "Dashboard"

   @staticmethod
   def _make_request(type):
      """Will return relevant information from a request to get SLURM info from
      ZOO.

      Keyword arguments:
      type -- What info to get (sinfo, squeue or snodes)
      """

      if (type is not 'sinfo'
            and type is not 'squeue'
            and type is not 'snodes'):
         return None

      url = (ZooAdapter.config.get_zoo_server_address() +
             '/cgi-bin/zoo_loader.cgi?request=Execute&service=WPS'
             '&version=1.0.0.0&identifier=slurmInfo&DataInputs=option=' + type)

      filehandle = urllib.urlopen(url)
      text = filehandle.read()

      regex = '<wps:LiteralData.*?>(.*?)</wps:LiteralData>'
      match = re.search(regex,text, re.DOTALL)

      if match:
         return match.group(1)

      return None

   @staticmethod
   def _dict_from_table(lines):
      """ Creates a dict from the tab-separated table that SLURM prints out.

      Keyword arguments:
      lines -- list of strings (each line of the SLURM output table)
      """

      return_items = []
      item_tmp = {}
      keys = []

      for count,line in enumerate(lines):

         if line.strip():

            # the first line lists keys
            if count is 0:
               keys = line.split()
               # convert to lower-case
               keys = map(str.lower, keys)
               continue

            # create dict from values
            item_tmp = dict(zip(keys, line.split()))
            return_items.append(item_tmp)

      return return_items 

   @staticmethod
   def get_zoo_server_info():
      """Reads the server info from SLURM on Zoo.

      Returns a list of dictionaries containing info about the SLURM server(s).
      Currently we just have one running, so this should just be a single item.
      """
   
      text = ZooDashboard._make_request('sinfo')
      # skip first line, which is just a timestamp
      if text:
         lines = text.splitlines()[1:]
         info_dict = ZooDashboard._dict_from_table(lines)
         return info_dict[0]
      return None

   @staticmethod
   def get_jobs_info():
      """Reads job info from SLURM on Zoo.

      Returns a list of dictionaries containing info about each job running on
      SLURM.
      """

      text = ZooDashboard._make_request('squeue')
      
      if text:
         lines = text.splitlines()
         return ZooDashboard._dict_from_table(lines)
      return None

   @staticmethod
   def get_nodes_info():
      """ Reads node info from SLURM on Zoo.

      Returns a list of dictionaries containing info about the client machines
      running under SLURM (nodes). 
      """
      text = ZooDashboard._make_request('snodes')

      nodes_array = []

      if text is None:
         return None

      for line in text.splitlines():

         if line.strip():
            node_tmp = {}

            for raw_value in line.split(' '):
               if raw_value:
                  value_split = raw_value.split('=')
                  key = value_split[0].lower()
                  node_tmp[key] = value_split[1]

            nodes_array.append(node_tmp)

      return nodes_array

