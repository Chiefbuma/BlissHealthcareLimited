from shareplum import Site, Office365
from shareplum.site import Version

import json
import os


USERNAME = "biosafety@blisshealthcare.co.ke"
PASSWORD = "Streamlit@2024"
SHAREPOINT_URL = "https://blissgvske.sharepoint.com"
SHAREPOINT_SITE = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports/"


class SharePoint:
    
    def auth(self):
        self.authcookie = Office365(
            SHAREPOINT_URL,
            username=USERNAME,
            password=PASSWORD,
        ).GetCookies()
        self.site = Site(
            SHAREPOINT_SITE,
            version=Version.v365,
            authcookie=self.authcookie,
        )
        return self.site

   def connect_to_list(self, ls_name, columns=None, query=None, next_page=None):
        try:
            self.auth_site = self.auth()
            sp_list = self.auth_site.List(list_name=ls_name)
            
            # If next_page is provided, use it for pagination
            if next_page:
                list_data = sp_list.GetListItems(query=query, next_page=next_page)
            else:
                list_data = sp_list.GetListItems(query=query)
            
            # Filter the list based on the provided columns
            if columns:
                filtered_list_data = [
                    {col: item[col] for col in columns if col in item}
                    for item in list_data['results']  # assuming the result is stored under 'results'
                ]
                return {'results': filtered_list_data, '__next': list_data.get('__next')}
            else:
                return {'results': list_data['results'], '__next': list_data.get('__next')}
        
        except Exception as e:
            raise e