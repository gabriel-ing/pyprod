# pyprod — API Reference

This document describes the core building blocks of a production, how they interact with each other, and how to implement them using pyprod.

![SystemDiagramOfProductions](https://github.com/intersystems/pyprod/blob/main/docs/HelloWorldFiles/SystemDiagramOfProductions.png?raw=true)

---

## Table of Contents

- [Production Overview](#-production-overview-)
    - [Production Configuration Page](#-production-configuration-page-)
    - [Status Object](#-status-object-)
- [Linking to the User Interface](#-linking-to-the-user-interface-)
    - [Package Name (Project Organization)](#-package-name-project-organization-)
    - [IRISProperty](#-irisproperty-)
    - [IRISParameter](#-irisparameter-)
    - [IRISLog](#-irislog-)
    - [Debug](#-debug-)

- [Persistable Messages](#-persistable-messages-)
    - [Serialization types](#-serialization-types-)
    - [Column](#-column-)
- [Production Components](#-production-components-)
  - [Inbound Adapter](#-inbound-adapter-)
  - [Business Service](#-business-service-)
  - [Business Process](#-business-process-)
  - [Business Operation](#-business-operation-)
  - [Outbound Adapter](#-outbound-adapter-)
  - [Production Class](#-production-class-)
  - [ServiceItem](#-serviceitem-)
  - [ProcessItem](#-processitem-)
  - [OperationItem](#-operationitem-)
- [Director Module](#-director-module-)
---

## <span style="color:#2f81f7"> Production Overview </span>

An InterSystems IRIS Production is composed of multiple **Business Hosts** that communicate by passing messages through the message passing engine. These business hosts can be one of the following:
- **Business Services** — Normalize and persist inbound data
- **Business Processes** — Contain orchestration and business logic
- **Business Operations** — Perform outbound actions 

There are other production components, which allow the hosts to interface with the external sources:

- **Inbound Adapters** — Interface to receive data into the production.
- **Outbound Adapters** — Interface to send data from the production to an external system

All the above components have a common callback definition in pyprod

- They are defined as sub classes of the desired component superclass, which is imported from pyprod
- Each of them has certain **required** callbacks
- A [Status Object](#-status-object-) must be returned as the first return value for each of these callbacks
- Additional return values (if any) must follow the Status

A typical production component would look like this:

```python
from intersystems_pyprod import ComponentSuperclass

class MyComponent(ComponentSuperclass):
    def RequiredCallback(self, ...):
        ...
        return status, output
```

Note: All the callbacks can be defined in either snake case or pascal case. Using pascal case allows to highlight them as callbacks of a production component and has been the traditional naming style in InterSystems IRIS productions. 


---

###  <span style="color:#58a6ff"> Namespace </span>
In InterSystems IRIS, any code runs in a namespace, which is a logical entity. A namespace provides access to data and to code, which is stored (typically) in multiple databases.

---

###  <span style="color:#58a6ff"> Production Configuration Page </span>

To create and configure interoperability productions using pyprod, you use the production configuration page. 

After writing your python classes, you link them to a namespace in IRIS. Then, from  desired namespace in the IRIS management portal **https://baseURL/csp/sys/UtilHome.csp**, you go to **Interoperability > Configure > Production** to reach the production configuration page. 

This is where you add all the components that you create in pyprod, create unique instances from them using settings, link them together, and start the production.

---


### <span style="color:#58a6ff"> Status Object </span>

All the callbacks and method calls in pyprod return a **Status object** as the first value, which indicates a success or a failure.

 - In the case of success, the status equals 1.
 - In the case of failure, the status is an encoded string containing the error status and one or more error codes and text messages.

#### Creating Status Objects

`pyprod` provides a `Status` class.

Example:

```python
from intersystems_pyprod import Status

def callback():
    return Status.OK()
    # or
    return Status.ERROR("Descriptive error message")

```

---

## <span style="color:#2f81f7"> Linking to the User Interface </span>
A key step to building interoperability production is linking the components you create, to the user interface. That also allows us to create different instances from the same classes and connect them to each other.The following are some key elements that are used to link the production components to the UI.

### <span style="color:#58a6ff"> Package Name (Project Organization) </span>

All component classes that are loaded into the IRIS namespace from the python scripts are organized into **packages**. These are differnet from any python package that you might be using or creating. These are part of the logical grouping that is done at the backend by IRIS inside its namespaces. **`iris_package_name`** is a ***pyprod-defined configuration variable*** which can be used to define the package name under which a class will be added in the backend. So, a component class created in python, once loaded to IRIS, can be seen on the Production configuration page as:

`iris_package_name.class_name`

iris_package_name can be period separated string(no other special characters allowed). Each part after a period becomes a subpacakge. 

Users can define the package name in their python scripts in three ways:

- Define `iris_package_name` as a **global variable** in the user script
- Define `iris_package_name` as a **class attribute**
- Default value (name of the python script)

In case `iris_package_name` is defined both as a global variable in the script and as a class attribute, the class attribute takes precedence. 

---

### <span style="color:#58a6ff"> IRISProperty </span>

- Instance specific variables  
IRISProperty essentially allows the users to create instance variables. This also enables linking the component to the UI and allowing the initial value to be entered from the UI.
- State Management  
Allows the user to maintain and modify state for **Adapters**, **Business Services**, and **Business Operations** as these components stay active in the CPU process that starts them for the entire duration of the production (Business processes do not maintain a long running state. A new instance of a Business Process is created for each incoming message).

**Constructor signature:**

```python
IRISProperty(
    default=None,
    datatype="",
    description="",
    settings="category:control"
)
```

#### Arguments

**`datatype`**
All string and numeric datatypes can be handled . If you do not define the datatype field, the backend will cast all datatypes as a string.  

 **`settings`** This argument needs to be defined to display the property in the UI. The settings have to be entered as colon ":" separated values. The first value, `category` indicated the group under which the property is displayed on the UI. The second, `control`, specifies the name of a specific control to use when viewing and modifying the setting in the Production Configuration page. For instance, to display a drop down list of all business hosts available for selection, you use the following value for control:  

- selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId}

so the complete settings argument will look like: settings=`"myCategory:selector?context={Ens.ContextSearch/ProductionItems?targets=1&productionName=@productionId}"`

Many other pre-defined selector types can be seen here: 
https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=EGDV_prog#EGDV_prog_settings_control_examples 

You can also define settings without specifying the category or control values. 

        1. settings = ""                   :   Adds the IRISProperty to the UI as an empty text box
        2. settings = "category"           :   Adds the IRISProperty to the UI under the category name, as an empty text box
        3. settings = "category:control"   :   Adds the IRISProperty to the UI under the category name, as the stated control
        4. settings = ":control"           :   Adds the IRISProperty to the UI, as the stated control
        5. settings = "-"                  :   Removes any inherited property by this name from the UI

**`description`** Optional attribute that is used to display the text that appears when you click on the property name in the UI.


>NOTE
>If you choose to define instance variables using a custom `__init__` method, you must preserve the constructor signature defined
>by the base class. ***DO NOT*** introduce additional parameters. The subclass constructor must accept only the `iris_host_object`
>argument and must delegate initialization to the base class using super():
>
```python
    def __init__(self,iris_host_object):
        super().__init__(iris_host_object)
        self.instance_variable = 0
```

### <span style="color:#58a6ff"> IRISParameter </span>
IRISParameter allows the users to store class constants on IRIS side. This is primarily needed to select the ADAPTER for a Service or Operation class:  

While defining adapters, note that the adapeter name will have two parts: package name and the class name. Both cannot have any special characters.

**Constructor signature:**

```python
IRISParameter(
    value, 
    datatype="", 
    description=""
)
```

#### Arguments

**`value`**
Must define this argument. It takes in values in the format `iris_package_name.class_name`

**`description`**
Optional argument that you should leave empty while setting ADAPTER parameter. 

**`description`**
Optional argument that is used to display the text that appears when you click on the ADAPTER parameter name in the UI

---

### <span style="color:#58a6ff">  Important note on IRISProperty </span>
Even though defined at the class level, IRISProperty attributes does not behave like typical python class attributes. This is because these are just used to provide a link to the UI for the python class instances. So all instances can have different values of IRISProperty without affecting overall class behavior.

---
### <span style="color:#58a6ff"> IRISLog </span>
This class allows you to link your production code to the default IRIS logger. 

This ensures that log messages emitted from Python code can also appear in the IRIS Production Log Viewer

You can also write your logs using any python logging module, however that won't be saved on IRIS (unless you explicitly send it to the IRIS database)

**Usage**

Add the following statement in your code:
```python
IRISLog.Info("info message")
IRISLog.Warning("warning message")
IRISLog.Error("error message")
IRISLog.Status(Status.OK())
IRISLog.Status(Status.ERROR("error string"))

```

---
### <span style="color:#58a6ff"> Debug </span>
You need to import the debug_host method from pyprod into your python code to link your production to a debugger. 
The usage is detailed in the [dedicated debugging page](https://github.com/intersystems/pyprod/blob/main/docs/debugging.md).  

---
## <span style="color:#2f81f7"> Persistable Messages </span>

### <span style="color:#58a6ff"> Serialization types </span>

The message passing engine tracks and persists all communication between **Business Services**, **Business Processes** and **Business Operations**. Thus, all this communication needs to be in the form of **persistable messages**.
pyprod provides two approaches to encapsulate your information in the form of a persistable message depending on the serialization format used.

1. **JsonSerialize**  
This class uses python's built in json module to convert your message to and from a serialized format.   
**NOTE**: There is a provision to speed up message passing for JsonSerialize messages by using a third party library called orjson instead of python's in-built json module.

2. **PickleSerialize**  
This class used python's in-built pickle module to convert your messages to and from a serialized format.  
**NOTE**: Never unpickle data from untrusted or unauthenticated sources as pickle deserialization can execute arbitrary code.  
Use this class when your message contains Python objects that cannot be represented in JSON.

A typical way to create a persistable message using any of these would look like this:

Creating a custom message class
``` python
class MyMessage(JsonSerialize):
    field_1 = "default_field_1"
    field_2: int
    ....

class MyMessage(PickleSerialize):
    field_1 = ("default_field_1_1","default_field_1_2")
    field_2: int
    ....
```

Using the custom message class

```python
MyInformation = MyMessage()
MyInformation.field_1 = "New Value"
MyInformation.field_2 = 0
```

or

```python
MyInformation = MyMessage("New Value", 0)
```

or

```python
MyInformation = MyMessage("New Value")
MyInformation.field_2 = 0
```

or 

```python
MyInformation = MyMessage(field_2 = 0)
MyInformation.field_1 = "New Value"
```


---


### <span style="color:#58a6ff"> Column </span>

Persisted messages are stored on disk in the **IRIS database** by the message-passing engine. When viewed in relational form, fields defined using `Column()` appear as **separate columns** in the corresponding table. `Column()` also allows us to create indexes on these fields for efficient sql querying.

`Column` is used exclusively with **persistable message classes**.


**Constructor signature:**

```python
Column(
        default=None,
        datatype=None,
        description=None,
        index=False
    )
```

**Example usage:**

```python
class MyMessageClass(MessageClassType):
    field_1 = Column()
    field_2 = Column(index = True)
```

> **Note**  
> `Column()` supports string and numeric datatypes only


## <span style="color:#2f81f7"> Production Components </span>

All production components have the following commonalities:
1. Need to inherit from a ***`required superclass`***
2. Need to define certain ***`callbacks as instance methods`***
3. Use certain ***`existing instance methods of the superclass to pass messages`***


### <span style="color:#58a6ff"> Inbound Adapter </span>

Inbound Adapters act as the **interface to external systems** for receiving information and forward it into the production pipeline.

#### Superclass: `InboundAdapter`


#### Required Callback: `OnTask` / `on_task`

This callback serves as the entry point for inbound data within the inbound adapter class.

Responsibilities:

- Receive external input
- Forward data to the associated Business Service
- No message persistence occurs at this stage

> **Parameters**  
> No arguments required (except self as it is an instance method)
> 
> **Returns**  
> **`status`** 


#### Message Passing: `business_host_process_input`

This method forwards data directly to the Business Service.

Characteristics:

- Accepts any Python data type
- No persistence or message tracing
- The Inbound Adapter and its Business Service execute in the same CPU process

#### Required Implementation

```python
from intersystems_pyprod import InboundAdapter

class MyInboundAdapter(InboundAdapter):
    def OnTask(self):
        message = ...
        status = self.business_host_process_input(message)
        return status
```

### <span style="color:#58a6ff"> Business Service </span>

A Business Service receives inbound data, either using an inbound adapter, or directly. It then converts this data into a [persistable message](#-persistable-messages-), and forwards it to the desired target within the production.

#### Superclass: `BusinessService`


#### Required Callback: `OnProcessInput` / `on_process_input`

This callback is invoked when:

- Input is received from an Inbound Adapter
- Input is sent directly to an adapterless Business Service

> **Parameters**
> 
> - **`input`** — Incoming object, either from an inbound adapter or via direct call to this method for an adapterless business service
> 
> **Returns**
> 
> - **`status`** 
> - **`response`** 

#### Message Passing Methods

##### `SendRequestSync` / `send_request_sync`

- Sends a request and waits for a response
- Blocking call
- Use when an immediate response is required

##### `SendRequestAsync` / `send_request_async`

- Sends a request without waiting for a response
- Non-blocking call
- Use when no response is required

#### Required Implementation

```python
from intersystems_pyprod import BusinessService

class MyBusinessService(BusinessService):

    #optional
    ADAPTER = IRISParameter("PackageName.AdapterName")
    target_dispatch_name = IRISProperty("PackageName.MyHostName")

    def OnProcessInput(self, input):
        # Convert input into a persistable request object
        request = ...

        status, response = self.SendRequestSync(target_dispatch_name, request, timeout=-1, description="")
        # OR
        status = self.SendRequestAsync(target_dispatch_name, request, description="")

        return status, response
```

**NOTE**: To create an Adapterless business serivce, you do not need to define the ADAPTER parameter. The ADAPTER parameter is only required when the input is to be received from an Inbound Adapter. See [AllPyComponents.py](https://github.com/intersystems/pyprod/blob/main/tests/helpers/AllPyComponents/AllPyComponents.py) and the test_BOMethod1() method in associated [test_all_py_components.py](https://github.com/intersystems/pyprod/blob/main/tests/test_all_py_components.py) to see how to use an Adapterless business service

### <span style="color:#58a6ff"> Business Process </span>

A Business Process contains the **core orchestration and business logic** of a production.

It typically:

- Receives persistable requests from Business Services
- Performs transformations on these requests
- Coordinates calls to Business Operations
- Aggregates and returns responses

#### Superclass: `BusinessProcess`

#### Callbacks

##### `OnRequest` / `on_request`

This is a required callback that must be defined in any class inhering from BusinessProcess. This is invoked when a new request arrives.

> **Parameters**
> 
> - **`request`** — Incoming request object
> 
> **Returns**
> 
> - **`status`** 
> - **`response`** - Persistable message

---

##### `OnResponse` / `on_response`

This is an optional callback that must be defined only when a **SendRequestAsync** call is made from within the OnRequest callback, with response_required set to 1.  Invoked when an asynchronous response arrives.

> **Parameters**
> 
> - **`request`** — Original request
> - **`response`** — Final response object
> - **`call_request`** — Request associated with this response
> - **`call_response`** — Incoming response object
> - **`completion_key`** — Correlation key supplied during the asynchronous send
> 
> **Returns**
> 
> - **`status`** 
> - **`response`** - Persistable message


#### Message Passing

##### `SendRequestSync` / `send_request_sync`

- Blocking call
- Response handled within `OnRequest`

##### `SendRequestAsync` / `send_request_async`

- Non-blocking call
- When `response_required=1`, the response is routed to `OnResponse`

#### Required Implementation

```python
from intersystems_pyprod import BusinessProcess

class CustomBP(BusinessProcess):
    target_dispatch_name = IRISProperty("PackageName.MyHostName")

    def OnRequest(self, request):
        status, response = self.SendRequestSync( self.target_dispatch_name, request,timeout=-1,description="")
        # OR
        status = self.SendRequestAsync(self.target_dispatch_name,request,response_required=1,completion_key=0,
description="")
        return status, response

    def OnResponse(self, request, response, call_request, call_response, completion_key):
        # Handle asynchronous response
        return status, response
```


### <span style="color:#58a6ff"> Business Operation </span>

A Business Operation sends data, either using an outbound adapter, or directly, to the final external target. 
All the requests routed to a business operation are first assessed for their message type. Then, the method that corresponds to this message type is looked up in a ***message map*** that you define within the opearation class. Finally, this method is used to handle the request. 

#### Superclass: `BusinessOperation`


#### Optional Callback: `OnMessage` / `on_message`
This callback can be defined in case you want a method to handle all message types that are not present in the message map. This also allows you to define a business operation without a message map in case you want a single method to handle all incoming request types.

> **Parameters**  
> **`request`** - all methods in a business operation handle an incoming request of a persistable message type
> 
> **Returns**  
> **`status`**  
> **`response`** - Optional persistable message 


#### Message Passing

Business Operations can pass messages to other hosts, or to an external target.

**To pass messages to other hosts within the production**

##### `SendRequestSync` / `send_request_sync`
Same as Business Service methods

##### `SendRequestAsync` / `send_request_async`
Same as Business Service methods


**To pass messages outside the production**

No persistance/tracing happens beyond this point. So the outgoing messages can be of any type (persistable or not).  
To send a message via the outbound adapter, you directly call the adapter methods using the optional ADAPTER IRISParameter defined in the BO class.

#### Required Implementation

```python
from intersystems_pyprod import InboundAdapter

class MyBusinessOperation(BusinessOperation):

    #optional
    ADAPTER = IRISParameter("PackageName.AdapterName")

    MessageMap = {
        "PackageName.MessageType1" : "method_1",
        "PackageName.MessageType2" : "method_2"
    }

    # Note: the response is optional, but must be a persistable type if present
    def method_1(self, request):
        self.ADAPTER.adapter_method_1("arg1", arg2 = "arg2")
        return status, response

    def method_2(self, request):
        self.ADAPTER.adapter_method_1()
        return status

```

#### Defining a message map 
The message type of an incoming message has two parts. The first part is the [iris_package_name](#-package-name-project-organization-) of the script in which you defined the message. The second part is the name of the message class that you used. 
The message map is essentially a python dictionary with keys as the message type and values as the business opeation methods. 

### <span style="color:#58a6ff"> Outbound Adapter </span>

Outbound Adapters act as an interface to external systems. They send the final output to the external system in the format required by that system. The adapter, linked to the business operation using the ADAPTER parameter, is run by the same CPU process as the Business operation.

#### Superclass: `OutboundAdapter`

#### No callbacks needed 

#### Message Passing
No persistable message is passed forward from the adapter. However, its methods can return an output back to a call from the business operation.

#### Required Implementation

```python
from intersystems_pyprod import InboundAdapter

class MyOutboundAdapter(OutboundAdapter):

    def adapter_method_1(arg1 = "arg1 default", arg2 = "arg2 default"):
        status = Status.OK()
        return status
    def adapter_method_2(arg1 = "arg1 default", arg2 = "arg2 default"):
        status = Status.OK()
        # Note: The output can be of any type and not necessarily a persistable message type
        return status, output

```

### <span style="color:#58a6ff"> Production Class </span>

`Production` is a declarative base class for defining an IRIS production entirely in Python. Subclass it to declare the production's structure — its services, processes, and operations — and to configure production-level settings. When the file is loaded into an IRIS namespace, the production definition is generated automatically from this class.

> **Note**  
> Only attributes defined in the `Production` superclass are valid. Setting any other attribute will emit a warning at load time.

#### Superclass: `Production`

#### Class Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `services` | `list[ServiceItem]` | `None` | Business services to include in the production |
| `processes` | `list[ProcessItem]` | `None` | Business processes to include in the production |
| `operations` | `list[OperationItem]` | `None` | Business operations to include in the production |
| `description` | `str` | `""` | Human-readable description of the production |
| `actor_pool_size` | `int` | `2` | Number of jobs in the shared actor pool for business processes |
| `testing_enabled` | `bool` | `False` | Enable testing infrastructure for the production |
| `log_general_trace_events` | `bool` | `False` | Log trace events not associated with any particular config item |
| `shutdown_timeout` | `int` | `120` | Seconds to wait for jobs to stop during shutdown |
| `update_timeout` | `int` | `10` | Seconds to wait for jobs to stop during an update |
| `alert_notification_manager` | `str` | `""` | Full config item name of the alert notification manager |
| `alert_notification_operation` | `str` | `""` | Full config item name of the alert notification operation |
| `alert_notification_recipients` | `str` | `""` | Comma-separated list of alert notification recipients |
| `alert_action_window` | `int` | `60` | Time window in minutes for alert action |

> **Note**  
> `actor_pool_size`, `testing_enabled`, `log_general_trace_events`, and all item-level settings can be overridden by System Default Settings in the IRIS management portal. Overriding will occur even when a value is explicitly set in the production definition.

#### Required Implementation

```python
from intersystems_pyprod import Production, ServiceItem, ProcessItem, OperationItem

iris_package_name = "HelloWorld"

class MyProduction(Production):
    description = "A simple Hello World production"
    actor_pool_size = 2

    services = [
        ServiceItem("HelloWorld.MyService", "HelloWorld.MyService",
                    host_settings={"target": "HelloWorld.MyProcess"})
    ]
    processes = [
        ProcessItem("HelloWorld.MyProcess", "HelloWorld.MyProcess",
                    host_settings={"target": "HelloWorld.MyOperation"})
    ]
    operations = [
        OperationItem("HelloWorld.MyOperation", "HelloWorld.MyOperation")
    ]
```

---

### <span style="color:#58a6ff"> ServiceItem </span>

Declares a Business Service configuration item inside a `Production` definition. Each `ServiceItem` becomes one entry in the production's item list.

#### Constructor Signature

```python
ServiceItem(
    name,
    class_name,
    *,
    host_settings=None,
    adapter_settings=None,
    category="",
    pool_size=1,
    enabled=True,
    foreground=False,
    comment="",
    log_trace_events=False,
    schedule=""
)
```

#### Arguments

**`name`** *(str, required)*  
The config item name as it appears in the production, e.g. `"MyPackage.MyService"`.

**`class_name`** *(str, required)*  
The full IRIS class name of the business service, e.g. `"MyPackage.MyBusinessService"`.

**`host_settings`** *(dict, optional)*  
A dictionary of settings to apply to the business service host. Keys are property names (snake_case or PascalCase) and values are the desired setting values. A warning is emitted at load time for any key that does not match an existing property on the class.

**`adapter_settings`** *(dict, optional)*  
A dictionary of settings to apply to the inbound adapter associated with this service. Same key/value rules as `host_settings`. Only applicable when the service uses an inbound adapter.

**`category`** *(str, optional)*  
Comma-separated list of category names for display grouping on the Production Configuration page. Does not affect runtime behavior.

**`pool_size`** *(int, default `1`)*  
Number of jobs to start for this config item. Use `0` for adapterless Business Services (uses the shared actor pool); use `1` for adapter-based services. For TCP-based services with `JobPerConnection=1`, values greater than `1` limit the number of connection jobs.

**`enabled`** *(bool, default `True`)*  
Whether this config item starts enabled in the production.

**`foreground`** *(bool, default `False`)*  
Whether to run the job in the foreground rather than background. Non-container only.

**`comment`** *(str, optional)*  
Free-text comment displayed in the Production Configuration page.

**`log_trace_events`** *(bool, default `False`)*  
Whether to log trace events for this item.

**`schedule`** *(str, optional)*  
Specifies when this item should be stopped and restarted. Accepts either a comma-separated list of event specifications in the format `action:YYYY-MM-DDThh:mm:ss` (where `action` is `START` or `STOP`), or a named schedule prefixed with `@`. Example: `"START:*-*-*T08:00:00,STOP:*-*-*T17:00:00"` starts the item daily at 8 a.m. and stops it at 5 p.m. Named schedules are created on the **Interoperability > Configure > Schedule Specs** page and referenced as `"@MyScheduleName"`.

#### Example

```python
ServiceItem(
    "MyPackage.MyService",
    "MyPackage.MyBusinessService",
    host_settings={"TargetConfigName": "MyPackage.MyProcess",
                   "GenerateSuperSessionID": 1},
    adapter_settings={"Port": 12345, "AllowedIPAddresses": "127.0.0.1"},
    pool_size=1,
    enabled=True,
    comment="Receives TCP input and forwards to MyProcess"
)
```

---

### <span style="color:#58a6ff"> ProcessItem </span>

Declares a Business Process configuration item inside a `Production` definition. `ProcessItem` has the same parameters as `ServiceItem` except it does not accept `adapter_settings`, since business processes do not use adapters.

#### Constructor Signature

```python
ProcessItem(
    name,
    class_name,
    *,
    host_settings=None,
    category="",
    pool_size=1,
    enabled=True,
    foreground=False,
    comment="",
    log_trace_events=False,
    schedule=""
)
```

#### Arguments

All arguments have the same meaning as in [`ServiceItem`](#-serviceitem-). The `adapter_settings` argument is not available for `ProcessItem`.

> **Note on `pool_size`**  
> Use `pool_size=0` to run business processes from the shared actor pool (the default approach). Use `pool_size=1` only for FIFO message-router processes that require a dedicated job.

#### Example

```python
ProcessItem(
    "MyPackage.MyProcess",
    "MyPackage.MyBusinessProcess",
    host_settings={"TargetConfigName": "MyPackage.MyOperation"},
    pool_size=0
)
```

---

### <span style="color:#58a6ff"> OperationItem </span>

Declares a Business Operation configuration item inside a `Production` definition. `OperationItem` accepts the same parameters as `ServiceItem`, including `adapter_settings` for configuring an outbound adapter.

#### Constructor Signature

```python
OperationItem(
    name,
    class_name,
    *,
    host_settings=None,
    adapter_settings=None,
    category="",
    pool_size=1,
    enabled=True,
    foreground=False,
    comment="",
    log_trace_events=False,
    schedule=""
)
```

#### Arguments

All arguments have the same meaning as in [`ServiceItem`](#-serviceitem-).

#### Example

```python
OperationItem(
    "MyPackage.MyOperation",
    "MyPackage.MyBusinessOperation",
    host_settings={"FailureTimeout": 30},
    adapter_settings={"IPAddress": "127.0.0.1", "Port": 12346,
                      "StayConnected": 0, "GetReply": 0}
)
```

---

## <span style="color:#2f81f7"> Director Module </span>

The `director` module wraps `Ens.Director`, the IRIS interoperability runtime controller. It provides functions to start, stop, restart, inspect, and interact with productions from Python code running inside an IRIS namespace.

Most functions return an IRIS status code as the first value. A value of `1` indicates success; any other value is an encoded error string. The exception is `get_host_messages`, which returns a list directly.

Import the functions you need directly from the module:

```python
from intersystems_pyprod.director import (
    start_production,
    stop_production,
    restart_production,
    get_production_status,
    update_production,
    clean_production,
    enable_config_item,
    list_all_productions,
    get_host_messages,
    create_business_service,
)
```

---

### <span style="color:#58a6ff"> `start_production` </span>

Start a production.

```python
start_production(prod_name: str = None) -> str
```

#### Parameters

**`prod_name`** *(str, optional)*  
The full IRIS class name of the production to start, e.g. `"MyPackage.MyProduction"`. If omitted, defaults to the last production used in this namespace.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

#### Example

```python
status = start_production("MyPackage.MyProduction")
```

---

### <span style="color:#58a6ff"> `stop_production` </span>

Stop the currently running production.

```python
stop_production(timeout: int = 10, force: bool = False) -> str
```

#### Parameters

**`timeout`** *(int, default `10`)*  
Seconds to wait for running jobs to shut down gracefully.

**`force`** *(bool, default `False`)*  
If `True`, forcefully kills jobs that do not stop within the timeout.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

---

### <span style="color:#58a6ff"> `restart_production` </span>

Stop and restart the currently running production.

```python
restart_production(timeout: int = 10, force: bool = False) -> str
```

#### Parameters

Same as [`stop_production`](#-stop_production-).

#### Returns

**`status`** — IRIS status code. `1` indicates success.

---

### <span style="color:#58a6ff"> `update_production` </span>

Apply configuration changes to a running production without a full stop/start cycle.

```python
update_production(timeout: int = 10, force: bool = False, called_by_schedule_handler: bool = False) -> str
```

#### Parameters

**`timeout`** *(int, default `10`)*  
Seconds to wait for affected jobs to stop before the update is applied.

**`force`** *(bool, default `False`)*  
If `True`, forcefully kills jobs that do not stop within the timeout.

**`called_by_schedule_handler`** *(bool, default `False`)*  
Set to `True` only when this function is invoked by the internal schedule handler.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

---

### <span style="color:#58a6ff"> `get_production_status` </span>

Get the current status of the production (when it is running, suspended, or troubled).

```python
get_production_status(lock_timeout: int = 10, skip_lock_if_running: bool = False) -> tuple[str, str, str]
```

#### Parameters

**`lock_timeout`** *(int, default `10`)*  
Seconds to wait before the lock operation times out. `0` means one attempt then time out.

**`skip_lock_if_running`** *(bool, default `False`)*  
If `True`, skips acquiring the lock when the production is already running.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

**`production_name`** *(str)* — Name of the production when the state is running, suspended, or troubled. Empty when stopped.

**`running_state`** *(str)* — One of:

| Value | Meaning |
|-------|---------|
| `1` | Running |
| `2` | Stopped (no `production_name` is returned) |
| `3` | Suspended |
| `4` | Troubled |

#### Example

```python
status, prod_name, state = get_production_status()
if state == "1":
    print(f"{prod_name} is running")
```

---

### <span style="color:#58a6ff"> `clean_production` </span>

> **WARNING**  
> Never use this on a live, deployed production. This removes all messages from queues and all current production state. Use only during development, and only when the production is stopped.

```python
clean_production(kill_app_data_too: bool = False) -> str
```

#### Parameters

**`kill_app_data_too`** *(bool, default `False`)*  
If `True`, also removes application data in addition to production state.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

---

### <span style="color:#58a6ff"> `enable_config_item` </span>

Enable or disable a config item in a production. The production may be running or stopped.

```python
enable_config_item(config_item_name: str, enable: bool = True, do_update: bool = True) -> str
```

#### Parameters

**`config_item_name`** *(str, required)*  
The name of the config item as it appears in the production, e.g. `"MyPackage.MyService"`.

**`enable`** *(bool, default `True`)*  
`True` to enable, `False` to disable. If multiple items share the same config name and any is already enabled, `enable=True` is a no-op. `enable=False` disables the running matching item, or the first enabled match if none are running.

**`do_update`** *(bool, default `True`)*  
If `True`, calls `update_production` automatically after the change so it takes effect on a running production immediately.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

#### Example

```python
status = enable_config_item("MyPackage.MyService", enable=False)
```

---

### <span style="color:#58a6ff"> `list_all_productions` </span>

Return a summary of all productions present in the current namespace.

```python
list_all_productions() -> tuple[str, list[str], dict[str, dict[str, str]]]
```

#### Returns

**`status`** — IRIS status code. `1` indicates success.

**`list_of_productions`** *(list[str])* — Names of all productions in the namespace.

**`complete_production_details`** *(dict[str, dict[str, str]])* — Production names mapped to a dict with the following keys:

| Key | Description |
|-----|-------------|
| `"status"` | Current status string (e.g. `"Running"`, `"Stopped"`) |
| `"last_start_time"` | Timestamp of the last start, or `None` |
| `"last_stop_time"` | Timestamp of the last stop, or `None` |

#### Example

```python
status, names, details = list_all_productions()
for name in names:
    print(name, details[name]["status"])
```

---

### <span style="color:#58a6ff"> `get_host_messages` </span>

Return messages sent from or received by a business host, most recent first.

```python
get_host_messages(host_name: str, max_results: int = 100) -> list[dict[str, Any]]
```

#### Parameters

**`host_name`** *(str, required)*  
The config item name of the business host as it appears in the production.

**`max_results`** *(int, default `100`)*  
Maximum number of messages to return.

#### Returns

A list of message dicts, each with the following keys:

| Key | Description |
|-----|-------------|
| `"id"` | Message header ID |
| `"time_created"` | Timestamp the message was created |
| `"source"` | Source config item name |
| `"target"` | Target config item name |
| `"status"` | Message status |
| `"session_id"` | Session ID |
| `"body_class"` | Full class name of the message body |
| `"body_id"` | ID of the message body object |

#### Example

```python
messages = get_host_messages("MyPackage.MyOperation", max_results=20)
for msg in messages:
    print(msg["time_created"], msg["source"], "->", msg["target"])
```

---

### <span style="color:#58a6ff"> `create_business_service` </span>

Create an adapterless business service instance. Used to inject messages directly into a running production from Python code, without going through an inbound adapter.

```python
create_business_service(service_class_name: str) -> tuple[str, _AdapterlessService]
```

#### Parameters

**`service_class_name`** *(str, required)*  
The full IRIS class name of the adapterless business service, e.g. `"MyPackage.MyBusinessService"`.

#### Returns

**`status`** — IRIS status code. `1` indicates success.

**`service`** — An `_AdapterlessService` wrapper object. Do not instantiate `_AdapterlessService` directly; always obtain it through this function.

#### `_AdapterlessService`

The returned object exposes the IRIS properties of the underlying service directly as Python attributes. Reads and writes are forwarded to the IRIS side automatically. Snake_case attribute names are converted to PascalCase before lookup.

It also exposes one method:

##### `process_input(input: Any) -> tuple[str, Any]`

Send an input to the business service and return the result.

> **Parameters**  
> **`input`** — Any Python object that the business service's `OnProcessInput` callback knows how to handle.  
>
> **Returns**  
> **`status`** — IRIS status code. `1` indicates success.  
> **`response`** — The response object returned by the service.

#### Example

```python
from intersystems_pyprod.director import create_business_service

status, service = create_business_service("MyPackage.MyAdapterlessService")
service.TargetConfigName = "MyPackage.MyProcess"   # set an IRIS property
status, response = service.process_input(my_request)
```