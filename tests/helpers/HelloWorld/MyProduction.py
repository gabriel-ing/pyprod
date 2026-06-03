
from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem

iris_package_name = "HelloWorld"

class MyProduction(Production):
    services = [ServiceItem("MyServiceName","HelloWorld.MyService",
                            host_settings={
                                "target":"MyProcessName"
                            })]
    processes = [ProcessItem("MyProcessName","HelloWorld.MyProcess",
                             host_settings={
                                 "target":"MyOperationName"
                             })]
    operations = [OperationItem("MyOperationName","HelloWorld.MyOperation")]