from intersystems_pyprod import Production, ServiceItem, OperationItem

iris_package_name = "TCPAdaptersFromOs"

class MyProduction(Production):
    actor_pool_size = 2

    services = [ServiceItem("TCPAdaptersFromOs.TCPBusinessService","TCPAdaptersFromOs.TCPBusinessService",
                        host_settings = {"TargetConfig":"TCPAdaptersFromOs.TCPBusinessOperation"},
                        adapter_settings={"AllowedIPAddresses":"127.0.0.1","Port":12345,"StayConnected":0}
                        )]
    operations = [OperationItem("TCPAdaptersFromOs.TCPBusinessOperation","TCPAdaptersFromOs.TCPBusinessOperation",
                            adapter_settings={"GetReply":0,"IPAddress":"127.0.0.1",
                                              "Port":12346, "StayConnected":0})]