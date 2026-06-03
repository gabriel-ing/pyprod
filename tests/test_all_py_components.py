import iris
import pytest
import time
import warnings

from intersystems_pyprod import director


@pytest.fixture(scope="module",autouse=True)
def startprod():
    status = director.start_production("AllPyComponents.MyProduction")
    print("production starting status = ", status)
    end_loop = 1
    start_time = time.time()

    while end_loop:
        if time.time()-start_time > 12:
            end_loop = 0
            print("unable to start production in 12 seconds")
            isrunning = 0
            break
   
        status, prod, running = director.get_production_status()

        if running == 1:
            isrunning = 1
            end_loop = 0
        else:
            time.sleep(0.5)
    print("productionrunning status = ", isrunning)

    yield

    status = director.stop_production()

    end_loop = 1
    start_time = time.time()
    while end_loop:
        if time.time()-start_time > 12:
            end_loop = 0
            print("unable to stop production in 12 seconds")

        status, prod, running = director.get_production_status()

        if running != 1:
            end_loop = 0
        else:
            time.sleep(0.5)
    


def test_bo_method_1():
    """
    This method tests an adapterless business service. 
    """
    status, adapterless = director.create_business_service("AllPyComponents.AdapterlessBS")
    adapterless.TargetConfigName = "AllPyComponents.CustomBP"
    status, response = adapterless.process_input("testMyJson")
    response = response.name

    assert response == "response from bo_method_1", f"response was {response}"

def test_bo_method_2():
    """
    This method tests an adapterless business service. 
    """
    status, adapterless = director.create_business_service("AllPyComponents.AdapterlessBS")
    adapterless.TargetConfigName = "AllPyComponents.CustomBP"
    status, response = adapterless.process_input("testMyPickle")
    response = response.name

    assert response == "response from bo_method_2", f"response was {response}"

def test_OSAdapterless():
    """
    This method tests the adapterless service made with a pure 
    Objectscript service
    """

    status, adapterless = director.create_business_service("AllPyComponents.OSAdapterless")
    mymessage = iris.AllPyComponents.MyPickleData._New()
    mymessage.name = "testMyPickle"
    status, response = adapterless.process_input(mymessage)
    response = response.name
    assert response == "testMyPickle", f"response was {response}"


def test_AdapterlessService_getattr():
    status, os_adapterless = director.create_business_service("AllPyComponents.OSAdapterless")
    with pytest.raises(AttributeError):
        _ = os_adapterless.nonexistent_property  
    with pytest.raises(AttributeError):    
          os_adapterless.nonexistent_property = "value"                                    
    with pytest.raises(AttributeError):    
          _ = os_adapterless.ProcessInput
              
