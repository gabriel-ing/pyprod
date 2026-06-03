from intersystems_pyprod import (BusinessProcess,Status, Production, ServiceItem, ProcessItem)

iris_package_name = "Readme"

class HelloWorldBP(BusinessProcess):
    def OnRequest(self, request):
        return Status.OK(), request


class MyProduction(Production):
    services = [
        ServiceItem(
            "MyFileService",
            "EnsLib.File.PassthroughService",
            host_settings={
                "TargetConfigNames": "MyCustomBP",
            },
            adapter_settings={
                "FilePath": "path/to/read/files/for/Readme/in",
                "DeleteFromServer": 0,
            },
        )
    ]
    processes = [
        ProcessItem("MyCustomBP", f"{iris_package_name}.HelloWorldBP")
    ]