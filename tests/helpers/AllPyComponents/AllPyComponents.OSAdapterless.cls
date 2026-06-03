Class AllPyComponents.OSAdapterless Extends Ens.BusinessService
{

Property TargetConfigName As %VarString;

Parameter SETTINGS = "TargetConfigName:Target";

Method OnProcessInput(pInput As %RegisteredObject, Output pOutput As %RegisteredObject) As %Status
{
    set status = $$$OK
    try{
        do ..SendRequestSync(..TargetConfigName,pInput, .pOutput)

    } catch e{
        set status = $system.Status.Error(5001, e.AsSystemError())
        $$$LOGERROR(status)
    }

    Quit status
}

}
