import iris

def get_prod():
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
    iris.Ens.Director.GetProductionStatus(production_name, production_status)
    return {"name": production_name.value, "status": production_status.value}



def start_prod(production_name):
    """Starts the production."""

    if not production_name:
        return {"status": 0, "message": "Production name is required to start a production."}

    prod = get_prod()
    if prod['status'] == 1:
            if prod['name'] == production_name:
                print(f"Production {prod['name']} is already running. Use -r flag to restart the production.")
            else:
                print(f"Production {prod['name']} is already running. Please stop (--stop) the production before starting a new one.")
            return
    print(f"Starting production {production_name}...")
    status = iris.Ens.Director.StartProduction(production_name)
    if status == 1:
        return {"status": 1, "message": f"Production {production_name} started successfully."}
    else:
        return {"status": 0, "message": f"Failed to start production {production_name}: {status}."}



def stop_prod(timeout=10, force=0):
    """Stops the production."""

    prod = get_prod()
    
    # Production status code 2 is $$$eProductionStateStopped
    if prod['status'] == 2:
            print(f"There is no production running. Use --start flag to start a production.")
            return
    
    print(f"Stopping production {prod['name']}...")
    status = iris.Ens.Director.StopProduction(timeout, force)
    if status == 1:
        return {"status": 1, "message": f"Production {prod['name']} stopped successfully."}
    else:
        return {"status": 0, "message": f"Failed to stop production {prod['name']}: {status}. Try increasing the timeout or setting force to 1."}



def restart_prod(timeout=10, force=0):
    """Restarts the production."""
    # iris.Ens.Director internally checks if a production is running before restarting it
    status = iris.Ens.Director.RestartProduction(timeout, force)
    if status == 1:
        return {"status": 1, "message": "Production restarted successfully."}
    else:   
        return {"status": 0, "message": f"Failed to restart production: {status}, try increasing the timeout or setting force to 1."}


if __name__ == "__main__":
    stop_prod()