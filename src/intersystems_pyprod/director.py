# wraps Ens.Director methods
from typing import Any

import iris

def _snake_to_pascal(name: str) -> str:
    # Check if the string is in snake_case
    if "_" in name and (name.lower() == name or name.upper() == name):
        return "".join(word.capitalize() for word in name.split("_") if word)
    # Return original if not snake_case
    return name

def start_production(prod_name: str = None) -> str:
    """Start a production.

    Parameters
    ----------
    prod_name : str, optional
        The full IRIS classname of the production to be started, e.g. 
        "MyPackage.MyProduction". If not specified, defaults to the "last" 
        production used.
    
    Returns
    -------
    status : str
        IRIS status code. 1 indicates success.
    """
    if prod_name is None:
        status = iris.Ens.Director.StartProduction()
    else:
        status = iris.Ens.Director.StartProduction(prod_name)
    return status


def stop_production(timeout:int = 10, force: bool = False) -> str:
    """Stop the currently running produciton.

    Parameters
    ----------
    timeout: int, optional
        Seconds to wait for jobs to do down. 
    force : bool, optional
        If True, forcefully kills jobs that cannot stop on their own.
    
    Returns
    -------
    status : str
        IRIS status code. 1 indicates success
    """
    status = iris.Ens.Director.StopProduction(timeout, int(force))
    return status


def restart_production(timeout:int = 10, force: bool = False) -> str:
    """Stop and restart the currently running production.

    Parameters
    ----------
    timeout: int, optional
        Seconds to wait for jobs to do down. 
    force : bool, optional
        If True, forcefully kills jobs that cannot stop on their own.
    
    Returns
    -------
    status : str
        IRIS status code. 1 indicates success

    """
    status = iris.Ens.Director.RestartProduction(timeout, int(force))
    return status


def get_production_status(lock_timeout: int = 10, skip_lock_if_running: bool = False) -> tuple[str, str, str]:
    """Get the current status of the production (if there is a production that is either running, suspended or troubled).

    Parameters
    ----------
    lock_timeout : int, optional 
        Seconds to wait before the attempted lock operation on the produciton times out. 
        A value of 0 means to make one attempt, then time out.
    skip_lock_if_running : bool, optional                   
          If True, skips acquiring the lock when a production is running. 
    Returns
    -------
    status : str
        IRIS status code. 1 indicates success
    production_name : str
        Name of the production when the state is either running, suspended or troubled
    running_state : str
        1 (running), 2(stopped, no production_name is returned with this state), 3(suspended), 4(troubled) 
    """
    production_name = iris.ref()
    state = iris.ref()
    status = iris.Ens.Director.GetProductionStatus(production_name, state, lock_timeout, int(skip_lock_if_running))

    production_name_value = production_name.value
    production_name.value = None
    del production_name

    state_value = state.value
    state.value = None
    del state

    return status, production_name_value, state_value


def clean_production(kill_app_data_too: bool = False) -> str:
    """.. WARNING:: NEVER use this method on a live, deployed production. This method removes all messages from queues and removes 
    all current information about the production. Use this only on a production that is still under development.
    The method will only function when the production is not running.

    Parameters  
    ----------                                              
      kill_app_data_too : bool, optional                      
          If True, also removes application data.                                                       
                                                              
    Returns                                                 
    -------                                                 
      status : str
          IRIS status code. 1 indicates success. 

    """
    return iris.Ens.Director.CleanProduction(int(kill_app_data_too))


def update_production(timeout: int = 10, force: bool = False, called_by_schedule_handler: bool = False) -> str:
    """This method updates the running production to apply configuration changes to it.

    Parameters
    ----------
    timeout: int, optional
        Seconds to wait for jobs to do down. 
    force : bool, optional
        If True, forcefully kills jobs that cannot stop on their own.
    called_by_schedule_handler : bool, optional
        This parameter is set to True when it is called by the schedule handler.

    Returns
    -------
    status : str
        IRIS status code. 1 indicates success. 
    

    """
    return iris.Ens.Director.UpdateProduction(timeout, int(force), int(called_by_schedule_handler))

def enable_config_item(config_item_name: str, enable: bool = True, do_update: bool = True) -> str:
    """Enable or disable a ConfigItem in a Production. The Production may be running or not.

    Parameters
    ----------
    config_item_name : str
        The name of the config item to be enabled or disabled.
    enable : bool
        In the case of multiple matching items with the same config name, if any is 
        already enabled then the enable=True option will do nothing and the enable=False 
        option will disable the running matching production item, or if not running then
        the first matching enabled item that it finds. 
    pDoUpdate : bool 
        Default value of True will update the production

    Returns
    -------
    status : str
        IRIS status code. 1 indicates success. 

    """
    return iris.Ens.Director.EnableConfigItem(config_item_name, int(enable), int(do_update))

def list_all_productions() -> tuple[str, list[str], dict[str,str]]:
    """
    Returns
    -------
    status : str
        IRIS status code. 1 indicates success. 
    list_of_productions : list[str]
        list of all the productions present in this namespace
    complete_production_details : dict[str,dict[str,str]]:
        Production names mapped to a dict with keys "Status", "LastStartTime", "LastStopTime"
    """
    production_data_ref = iris.arrayref()
    status = iris.Ens.Director.GetProductionSummary(production_data_ref)
    production_data = production_data_ref.value
    production_data_ref.value = None
    del production_data_ref    

    complete_dict = {}

    for key, value in production_data.items():
        actual_value = value.split('\x19\x01')

        actual_value[0] = actual_value[0].lstrip('\t\x01')
        actual_value[-1] = actual_value[-1].rstrip('\x02\x04')

        # Clean leftover ObjectScript list/null-ish markers
        actual_value = [
            item.replace('\x02\x01\x02\x01', "").strip()
            for item in actual_value
        ]

        complete_dict[key] = {
            "status": actual_value[0] if len(actual_value) > 0 and actual_value[0] else None,
            "last_start_time": actual_value[1] if len(actual_value) > 1 and actual_value[1] else None,
            "last_stop_time": actual_value[2] if len(actual_value) > 2 and actual_value[2] else None,
        }

    return status, list(production_data.keys()), complete_dict


def get_host_messages(host_name: str, max_results: int = 100):
    """
    This method returns messages either sent from or received at host_name, most recent first. 
    
    Parameters
    ----------
    host_name : str
        Name of the business host as it appears in the production
    max_results : int
        Maximum number of messages (sent or received) to return, ordered by most recent first

    Returns
    -------
    message : list[dict[str,Any]]
    """
    sql = """
        SELECT TOP ?
            ID,
            TimeCreated,
            SourceConfigName,
            TargetConfigName,
            Status,
            SessionId,
            MessageBodyClassName,
            MessageBodyId
        FROM Ens.MessageHeader
        WHERE SourceConfigName = ?
           OR TargetConfigName = ?
        ORDER BY TimeCreated DESC
    """

    stmt = iris.sql.prepare(sql)
    rs = stmt.execute(max_results, host_name, host_name)

    messages = []

    for row in rs:
        messages.append({
            "id": row[0],
            "time_created": str(row[1]),
            "source": row[2],
            "target": row[3],
            "status": row[4],
            "session_id": row[5],
            "body_class": row[6],
            "body_id": row[7],
        })

    return messages


class _AdapterlessService:
    """Wraps an IRIS adapterless business service returned by "create_business_service().
    Do not instantiate directly — always obtain via "create_business_service()".

    IRIS properties on the underlying service (e.g. TargetConfigName) can be get/set 
    directly on this object and will be forwarded to the IRIS side automatically.
    """

    def __init__(self, _adapterless_bs,_service_class_name):
        # writing directly to dict as __setattr__/__getattr__ is defined and can cause recurion
        self.__dict__['_adapterless_bs'] = _adapterless_bs
        self.__dict__['_service_class_name'] = _service_class_name
    
    def __setattr__(self, name, value):
        if iris._Dictionary.CompiledProperty._ExistsId(f"{self._service_class_name}||{name}"):
            setattr(self._adapterless_bs, _snake_to_pascal(name), value)
        else:
            raise AttributeError(f"'{self._service_class_name}' object has no Property '{name}'")
            
    def __getattr__(self, name):
        if name == "ProcessInput":
            raise AttributeError("Use process_input() instead")
        name = _snake_to_pascal(name)
        is_property = iris._Dictionary.CompiledProperty._ExistsId(f"{self._service_class_name}||{name}")
        is_method = iris._Dictionary.CompiledMethod._ExistsId(f"{self._service_class_name}||{name}")
        if not is_property and not is_method:
            raise AttributeError(f"'{self._service_class_name}' object has no Property or Method '{name}'")
        return getattr(self._adapterless_bs, name)
            
    
    def process_input(self, input: Any) -> tuple[str, Any]:
        """Send an input to the business service and return the status and response

        Parameters
        ----------
        input : Any 
            The business service code must know how to handle this object

        Returns
        -------
        status : str
            IRIS status code. 1 indicates success. 
        response: Any
            the response object returned by the service
        """

        response = iris.ref()
        status = self._adapterless_bs.ProcessInput(input, response)
        response_value = response.value
        response.value = None
        del response
        return status, response_value
    
    def __del__(self):
        try:
            self._adapterless_bs.PythonClassObject = ""
        except Exception:
            pass

def create_business_service(service_class_name:str) -> tuple[str, _AdapterlessService]:
    """Create an adapterless business service instance.
    Used to send messages into a running production without going through an inbound adapter.

    Parameters
    ----------
    service_class_name : str
            The full IRIS class name of the business service, e.g. "MyPackage.MyBusinessService".

    Returns
    -------
    status : str
            IRIS status code. 1 indicates success.
    service : _AdapterlessService
            Wraps the created business service. Use service.process_input()
            to send messages into the production.
    """
    mybs = iris.ref()
    status = iris.Ens.Director.CreateBusinessService(service_class_name, mybs)
    adapterless = _AdapterlessService(mybs.value,service_class_name)
    return status, adapterless
