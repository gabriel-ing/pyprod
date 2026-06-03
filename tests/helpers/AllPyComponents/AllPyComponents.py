from intersystems_pyprod import (
    IRISParameter,
    IRISProperty,
    BusinessService,
    BusinessProcess,
    BusinessOperation,
    OutboundAdapter,
    Column,
    JsonSerialize,
    PickleSerialize,
    IRISLog,
    Status,
    debug_host,
)

iris_package_name = "AllPyComponents"

class MyJsonData(JsonSerialize):
    name = Column(default="default name")
    amount = Column(default=0)

class MyPickleData(PickleSerialize):
    name = Column()
    amount = 1

class AdapterlessBS(BusinessService):
    TargetConfigName = IRISProperty(settings="Target")
    NewProp = IRISProperty(33,int,settings="Target")
    def on_process_input(self, input):
        status = Status.OK()
        msg = MyJsonData(input)
        status, response = self.SendRequestSync(self.TargetConfigName, msg)
        return status, response
    
class CustomBP(BusinessProcess):
    target_config_name: str = IRISProperty(settings="Target")
    myStr = IRISProperty(datatype="str", settings="my settings", default="default string", description="A string property for the process")
    myInt = IRISProperty(datatype="int", settings="my settings", default=10, description="An integer property for the process")
    myBool = IRISProperty(datatype="bool", settings="my settings", default=1, description="A boolean property for the process")
    myNum = IRISProperty(datatype="num", settings="my settings", default=42, description="Number of concurrent tasks for the adapter")
    
    def on_request(self, request):
        IRISLog.Info("message received hreereere")
        status = Status.OK()
        if request.name == "testMyJson" :
            syncRequest = MyJsonData("MyJsonData request from BP to BO", 1)
        elif request.name == "testMyPickle":
            syncRequest = MyPickleData("MyPickleData request from BP to BO", 1)
        status, response = self.SendRequestSync(self.target_config_name, syncRequest)
        return status, response


class CustomBO(BusinessOperation):
    ADAPTER = IRISParameter("AllPyComponents.CustomOutAdapter")
    message_map = {
        f"{iris_package_name}.MyJsonData": "bo_method_1",
        "AllPyComponents.MyPickleData": "bo_method_2"
    }

    def bo_method_1(self, request):
        status = Status.OK()
        IRISLog.Info("Data received at bo_method_1 is: " + request.name)
        self.ADAPTER.out_adapter_method("From bo_method_1")
        response = MyJsonData("response from bo_method_1", 0)
        return status, response

    def bo_method_2(self, request):
        status = Status.OK()
        IRISLog.Info("Data received at bo_method_2 is: " + request.name)
        response = MyPickleData("response from bo_method_2", 0)
        return status, response
  

class CustomOutAdapter(OutboundAdapter):
    def out_adapter_method(self, information="default"):
        status = Status.OK()
        IRISLog.Info("Data received at Outbound Adapter is: " + information)
        return status

