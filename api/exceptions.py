from rest_framework.exceptions import APIException


class NoClientRegistered(APIException):
    status_code = 200
    default_detail = "No client registered"
    default_code = "no_client_registered"


# class NoContractRegistered(APIException):
#     status_code = 200
#     default_detail = "No contract registered"
#     default_code = "no_contract_registered"
#
#
# class NoEventRegistered(APIException):
#     status_code = 200
#     default_detail = "No event registered"
#     default_code = "no_event_registered"

class MissingCredentials(APIException):
    status_code = 403
    default_detail = "Missing credentials: You cannot access the details of this page"
    default_code = "missing_credentials"


class NotInChargeOfClient(APIException):
    status_code = 403
    default_detail = "You are not in charge of this client"
    default_code = "not_in_charge_of_client"


class NotInChargeOfContract(APIException):
    status_code = 403
    default_detail = "You are not in charge of this contract"
    default_code = "not_in_charge_of_contract"


class NotInChargeOfEvent(APIException):
    status_code = 403
    default_detail = "You are not in charge of this event"
    default_code = "not_in_charge_of_event"


class ClientNotFound(APIException):
    status_code = 404
    default_detail = "Client not found"
    default_code = "client_not_found"


class ContractNotFound(APIException):
    status_code = 404
    default_detail = "Contract not found"
    default_code = "contract_not_found"


class EventNotFound(APIException):
    status_code = 404
    default_detail = "Event not found"
    default_code = "event_not_found"
