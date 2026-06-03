from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem

iris_package_name = "QuickStart"

class MyProduction(Production):
    description = "QuickStart production wiring service → process → operation"
    actor_pool_size = 2

    services = [
        ServiceItem(
            "QuickStart.CustomBS",
            "QuickStart.CustomBS",
            host_settings={"TargetConfigName": "QuickStart.CustomBP"}
        )
    ]
    processes = [
        ProcessItem(
            "QuickStart.CustomBP",
            "QuickStart.CustomBP",
            host_settings={"TargetConfigName": "QuickStart.CustomBO"}
        )
    ]
    operations = [
        OperationItem(
            "QuickStart.CustomBO",
            "QuickStart.CustomBO"
        )
    ]