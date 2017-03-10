import requests
import csv
from decimal import Decimal
from pprint import pprint
import json
from datetime import datetime
import requests
import os
import boto3

class FastlyApi(object):

     def __init__(self,path, headers):
         self.path = path
         self.headers = headers

     def _url(self):
         return 'https://api.fastly.com' + self.path

     def get_fastly_billing_data(self,path,headers):
         print "AM HERE", path
         return requests.get(self._url(), headers= self.headers)

     def get_billing_fields(self, *args):
         """first argument to this method is
         json data from fastly api
         """
         billing_data = get_fastly_billing_data(path, headers)
         return billing_data

     def get_services_data(self, data):
         """
         :param data: data from fastly
         :return: data with service IDs
         """
         services_data = data['services']
         return services_data

     def get_overall_bandwidth(self,data):
         """

         :param data:
         :return: overall bandwidth
         """
         overall_bandwidth = data['total']['bandwidth']
         return overall_bandwidth

     def get_overall_bandwidth_cost(self, data):
         """

         :param data:
         :return: overall bandwidth cost
         """
         total_bandwidth_cost = data['total']['bandwidth_cost']
         return total_bandwidth_cost

     def get_total_number_of_request(self, data):
         """

         :param data:
         :return: total number of request
         """
         total_number_of_request = data['total']['requests']
         return total_number_of_request

     def get_total_request_cost(self, data):
         """

         :param data:
         :return: total request cost
         """
         total_request_cost = data['total']['requests_cost']
         return total_request_cost


     def get_total_extra_cost(self, data):
         """

         :param data:
         :return: total extra cost
         """
         total_extra_cost = data['total']['extras_cost']
         return total_extra_cost

     def get_total_rollover_cost(self, data):
         """

         :param data:
         :return: rollover cost
         """
         total_rollover_cost = data['total']['rollover']
         return total_rollover_cost


     def get_serviceId_bandwidth_name(self, data):
         """
         This method returns service ID, bandwidth and name
         """

         total_rollover_cost = 0
         if 'rollover' in data['total'].keys():
             total_rollover_cost = self.get_total_rollover_cost(data)
         services_data = self.get_services_data(data)
         number_of_services = len(services_data.keys())
         print 'len', number_of_services
         overall_bandwidth = self.get_overall_bandwidth(data)
         request_total_by_service = 0
         total_bandwidth = 0
         service_bandwidth = 0
         name = ''

         total_bandwidth_cost = self.get_overall_bandwidth_cost(data)
         total_number_of_request = self.get_total_number_of_request(data)
         total_request_cost = self.get_total_request_cost(data)
         total_extra_cost = self.get_total_extra_cost(data)

         print "TOTAL COST", data['total']['cost']


         #calculate extra cost per service
         extra_cost_per_service = total_extra_cost / number_of_services

         #calculate rollover cost per service
         rollover_cost_per_service = total_rollover_cost / number_of_services

         #print "EXTRA COST", extra_cost_per_service, "rollover: ", rollover_cost_per_service
         #to prove the calculation is right
         overall_cost = 0
         with open("/tmp/fastly-billing.csv", 'wb') as csv_file:
             writer = csv.writer(csv_file)
             writer.writerow(['Name', 'Service ID', 'Bandwidth Cost', 'Request Cost',  'Service Cost'])
             for service_id, values_dict in services_data.iteritems():
                 for key, value in values_dict.iteritems():
                     if key == 'name':
                         name = values_dict[key]
                         continue
                     band_add = values_dict[key]['bandwidth']
                     req_add = values_dict[key]['requests']
                     service_bandwidth += band_add
                     request_total_by_service += req_add
                 total_bandwidth += service_bandwidth

                 #bandwidth cost per service
                 service_percent_bandwidth = (service_bandwidth / overall_bandwidth) * 100
                 service_bandwidth_cost = (service_bandwidth / overall_bandwidth) * total_bandwidth_cost

                 #request cost calculation
                 no_of_request_percent =  (request_total_by_service / total_number_of_request) * 100
                 request_cost_per_service = (request_total_by_service / total_number_of_request) * total_request_cost

                 #total_cost_per_service =  service_bandwidth_cost + request_cost_per_service + extra_cost_per_service \
                     #+ rollover_cost_per_service
		   
		 #request cost per service + extra + rollover
                 request_cost_per_service = request_cost_per_service + extra_cost_per_service 
                 
                 #bandwith cost + rollover
                 service_bandwidth_cost = service_bandwidth_cost + rollover_cost_per_service
                 
                 #mewly added calculation
                 total_cost_per_service = request_cost_per_service + service_bandwidth_cost

                 overall_cost += total_cost_per_service
                 

                 service_bandwidth_cost = str(round(Decimal(service_bandwidth_cost), 3))
                 total_cost_per_service = str(round(Decimal(total_cost_per_service), 3))
                 request_cost_per_service = str(round(Decimal(request_cost_per_service), 3))
                 writer.writerow(
                     [name, service_id, service_bandwidth_cost, request_cost_per_service, total_cost_per_service])
                 service_bandwidth = 0
                 request_total_by_service = 0
                 total_cost_per_service = 0
             print "OVER_ALL", overall_cost
         fieldnames = ['Name', 'Service ID', 'Bandwidth Cost', 'Request Cost',  'Service Cost']
         ff = open("/tmp/fastly-billing.csv", 'r')
         ee = open("/tmp/fastly-billing.csv", 'r')
         next(ff)
         next(ee)
         readers = csv.DictReader(ff, fieldnames)
         output = csv.DictReader(ee, fieldnames)
         for index in output:
	   print json.dumps(index)
         json_file = open("/tmp/fastly-billing.json", 'w')
         json_data = json.dump([r for r in readers], json_file)
         #json_file.write(json_data)




def main(event, context):

    FASTLY_KEY = os.environ['FASTLY_KEY']

    period = datetime.now().strftime("%Y-%m")
    period = period.split("-")
    year = period[0]
    month = period[1]

    path = '/billing/year/%s/month/%s' % (year, month)

    headers = {'Fastly-Key' : FASTLY_KEY}

    fastly_obj = FastlyApi(path,headers)

    #get the billing data in json format
    resp_data = fastly_obj.get_fastly_billing_data(path,headers)

    data = resp_data.json()

    fastly_obj.get_serviceId_bandwidth_name(data)

    my_bucket = 'fastly-cost.ft.com'
    s3_client = boto3.client('s3')
    
    #upload file to s3 bucket
    s3_client.upload_file('/tmp/fastly-billing.json',my_bucket,'fastly-billing.json')
    

if __name__ == '__main__':
    main()

