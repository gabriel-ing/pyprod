from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem


iris_package_name = "AllPyComponents"

class MyProduction(Production):
    description = "My production from my class file"
    log_general_trace_events = True
    actor_pool_size = 2
    shutdown_timeout = 120
    update_timeout = 10
    alert_notification_manager = f"{iris_package_name}.AdapterlessBS"
    alert_notification_operation = f"{iris_package_name}.AdapterlessBS"
    alert_notification_recipients = (
        f"{iris_package_name}.AdapterlessBP, {iris_package_name}.AdapterlessBO"
    )
    not_a_production_setting = (
        "this is not a valid setting for a production and will give a warning"
    )

    services = [
        ServiceItem(
            f"{iris_package_name}.AdapterlessBS",
            f"{iris_package_name}.AdapterlessBS",
            host_settings={
                "TargetConfigName": f"{iris_package_name}.CustomBP",
                "GenerateSuperSessionID": 20,
            },
            pool_size=30,
        ),
        ServiceItem(
            "AllPyComponents.OSAdapterless",
            "AllPyComponents.OSAdapterless",
            host_settings={
                "TargetConfigName": f"{iris_package_name}.OSCustomBP",
                "NotASetting": (
                    "Should display a warning but will appear in the production definition. "
                    "Will not affect the running of the production"
                ),
            },
            comment="creating a pure objectscript adapterless service which sends message to a pure OS BP",
        ),
    ]

    processes = [
        ProcessItem(
            "AllPyComponents.CustomBP",
            "AllPyComponents.CustomBP",
            host_settings={"target_config_name": f"{iris_package_name}.CustomBO"},
        ),
        ProcessItem(
            "AllPyComponents.OSCustomBP",
            "AllPyComponents.OSCustomBP",
            host_settings={"TargetConfigName": f"{iris_package_name}.OSCustomBO"},
            comment="pure OS BP which sends message to pure OS BO",
        ),
    ]

    operations = [
        OperationItem(
            "AllPyComponents.CustomBO",
            "AllPyComponents.CustomBO",
            host_settings={"FailureTimeout": 23},
            adapter_settings={
                "KeepaliveInterval": 0,
                "NotASetting": (
                    "Should display a warning but will appear in the production definition. "
                    "Will not affect the running of the production"
                ),
            },
        ),
        OperationItem(
            "AllPyComponents.OSCustomBO",
            "AllPyComponents.OSCustomBO",
            host_settings={"FailureTimeout": 18},
        ),
    ]
