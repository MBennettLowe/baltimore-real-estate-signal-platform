# explored the API's
import requests

"""
r = requests.get("https://baltegis.baltimorecity.gov/mapping/rest/services/CityView/RealProperty_OB/FeatureServer", params={"f": "json"})
print(r.status_code)
print(r.json())


r = requests.get("https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/3", params={"f": "json"})
print(r.status_code)
print(r.json())

"""
r = requests.get("https://egisdata.baltimorecity.gov/egis/rest/services/Housing/DHCD_Open_Baltimore_Datasets/FeatureServer/1", params={"f": "json"})
print(r.status_code)
print(r.json())

"""
r = requests.get("https://services1.arcgis.com/UWYHeuuJISiGmgXx/arcgis/rest/services/Tax_Lien_Certificate_Sale_Properties1/FeatureServer", params={"f": "json"})
print(r.status_code)
print(r.json())

"""