from ckanapi import RemoteCKAN

API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJUM3RFTFpEaDFGZVJvN05RWmJTNDItX3g5S2FJT2N6ZGM5OTZCR0FNdmRjIiwiaWF0IjoxNzg4OTAzNjEwfQ.VM-qBgL4CnKbENa3ZOcYpPOm2mC5DkNIDRfTn6Pf4nU"

rc = RemoteCKAN('https://www.data.qld.gov.au/', apikey=API_TOKEN)
result = rc.action.datastore_search(
    resource_id="126ed6f0-c3e1-4c97-b8a2-6be14032033d",
    limit=5,
    q="jones",
)
print(result['records'])

