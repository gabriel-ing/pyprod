import iris

RUNNING = 1
STOPPED = 2
TROUBLED = 3
SUSPENDED = 4


STATUS_MESSAGES = {
    RUNNING: "Running",
    STOPPED: "Stopped",
    TROUBLED: "Troubled",
    SUSPENDED: "Suspended",
}


class ProductionStatusError(RuntimeError):
    pass

def get_prod_status():
    """
    Returns the name and status of the production as a dictionary.
    Status codes are: 
    1 - Running
    2 - Stopped
    3 - Troubled
    4 - Suspended
    """

    production_name = iris.ref("")
    production_status = iris.ref("")

    response = iris.Ens.Director.GetProductionStatus(production_name, production_status)
    if response != 1:
        raise ProductionStatusError(f"Failed to get production status: {response}")
    return {"name": production_name.value, "status": production_status.value, "status_message": STATUS_MESSAGES.get(production_status.value, "Unknown")}


def start_prod(production_name):
    """Starts the production."""

    if not production_name or not production_name.strip():
        return {"ok": False, "message": "Production name is required to start a production."}

    prod = get_prod_status()
    if prod['status'] in [RUNNING, TROUBLED, SUSPENDED]: # Running, Troubled, or Suspended
            if prod['name'] == production_name:
                return {"ok": False, "message": f"Production {prod['name']} is already active with status {prod['status_message']}. Use -r flag to restart the production."}
            else:
                return {"ok": False, "message": f"Production {prod['name']} is already active with status {prod['status_message']}. Please stop (--stop) the production before starting a new one."}

    response = iris.Ens.Director.StartProduction(production_name)
    if response == 1:
            return {"ok": True, "message": f"Production {production_name} started successfully."}
    else:
        return {"ok": False, "message": f"Failed to start production {production_name}: {response}."}



def stop_prod(timeout=10, force=False):
    """Stops the production."""

    
    if timeout < 0:
        return {"ok": False, "message": "Timeout must be non-negative."}

    prod = get_prod_status()
    
    # Production status code 2 is $$$eProductionStateStopped
    if prod['status'] == STOPPED:
            return {"ok": False, "message": "There is no production running in the current namespace. Use --start flag to start a production."}
    

    response = iris.Ens.Director.StopProduction(timeout, force)
    if response == 1:
        return {"ok": True, "message": f"Production {prod['name']} stopped successfully."}
    else:
        return {"ok": False, "message": f"Failed to stop production {prod['name']}: {response}. Try increasing the timeout or setting force to 1."}



def restart_prod(timeout=10, force=False):
    """Restarts the production."""
    # iris.Ens.Director internally checks if a production is running before restarting it
    
    if timeout < 0:
        return {"ok": False, "message": "Timeout must be non-negative."}

    prod = get_prod_status()
    if prod['status'] == STOPPED:
            return {"ok": False, "message": "There is no production running to restart in the current namespace. Use --start flag to start a named production."}
    
    response = iris.Ens.Director.RestartProduction(timeout, force)

    if response == 1:
        return {"ok": True, "message": "Production restarted successfully."}
    else:   
        return {"ok": False, "message": f"Failed to restart production: {response}, try increasing the timeout or setting force to 1."}


