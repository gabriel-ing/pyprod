Class AllPyComponents.OSCustomBP Extends Ens.BusinessProcess
{

Property TargetConfigName As %VarString;

Parameter SETTINGS = "TargetConfigName:Target";

Method OnRequest(request As %Library.Persistent, Output response As %Library.Persistent) As %Status
{
    set status = $$$OK

    set status = ..SendRequestSync(..TargetConfigName,request, .response)

    Quit status
}


}
