import time

from intersystems_pyprod import (
    InboundAdapter,BusinessService, BusinessProcess, 
    BusinessOperation, OutboundAdapter, JsonSerialize, 
    IRISProperty, IRISParameter, IRISLog, Status)

iris_package_name = "HelloWorld"
class MyRequest(JsonSerialize):
    content: str

class MyResponse(JsonSerialize):
    content: str

class MyInAdapter(InboundAdapter):
    def OnTask(self):
        time.sleep(0.5)
        self.business_host_process_input("request message")
        return Status.OK()

class MyService(BusinessService):
    ADAPTER = IRISParameter("HelloWorld.MyInAdapter")
    target = IRISProperty(settings="Target")
    def OnProcessInput(self, input):
        persistent_message = MyRequest(input)
        status, response = self.SendRequestSync(self.target, persistent_message)
        IRISLog.Info(response.content)
        return status

class MyProcess(BusinessProcess):
    target = IRISProperty(settings="Target")
    def on_request(self, input):
        status, response = self.SendRequestSync(self.target,input)
        return status, response


class MyOperation(BusinessOperation):
    ADAPTER = IRISParameter("HelloWorld.MyOutAdapter")
    def OnMessage(self, input):
        status = self.ADAPTER.custom_method(input)
        response = MyResponse("response message")
        return status, response


class MyOutAdapter(OutboundAdapter):
    def custom_method(self, input):
        IRISLog.Info(input.content)
        return Status.OK()
