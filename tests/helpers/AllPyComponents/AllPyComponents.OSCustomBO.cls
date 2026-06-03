Class AllPyComponents.OSCustomBO Extends Ens.BusinessOperation
{

Method OnMessage(pRequest As %Library.Persistent, Output pResponse As %Library.Persistent) As %Status
{
    set status = $$$OK
    $$$LOGINFO("request received")
    set pResponse = pRequest
    Quit status
}

}
